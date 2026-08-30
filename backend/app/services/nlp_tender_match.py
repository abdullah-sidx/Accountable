"""
Accountable Platform — NLP Tender Match Service
================================================
Parses complaint descriptions and links them to public tender records
using a multi-stage NLP pipeline:

  Stage 1 – Pre-processing & keyword extraction
      spaCy NER + YAKE keyword extraction on complaint text.

  Stage 2 – Semantic embedding
      sentence-transformers (all-MiniLM-L6-v2) to encode complaints and
      tenders into dense vectors; cosine similarity for semantic matching.

  Stage 3 – Keyword overlap scoring
      Jaccard similarity on extracted keywords for an interpretable signal.

  Stage 4 – Shell-company network flagging
      Cross-reference matched tenders' awarded contractors against the
      shell-company suspect list; flag if risk_score > SHELL_RISK_THRESHOLD.

  Stage 5 – Persistence
      Write TenderMatch rows; update complaint NLP fields.

Entry point
-----------
    await match_complaint_to_tenders(complaint_id: int) -> None

Called as a FastAPI BackgroundTask right after complaint creation.
"""

from __future__ import annotations

import logging
import re
import string
from typing import Optional

import yake
from sentence_transformers import SentenceTransformer, util
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import async_session_factory
from app.database.models import Complaint, Contractor, Tender, TenderMatch

# Optional spaCy — gracefully degraded if model not installed
try:
    import spacy

    _nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:  # noqa: BLE001
    _nlp = None
    SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EMBEDDING_MODEL = "all-MiniLM-L6-v2"      # ~80 MB, fast CPU inference
TOP_K_TENDERS = 10                          # Max tender matches to store per complaint
SEMANTIC_WEIGHT = 0.65                      # Weight for sentence-transformer score
KEYWORD_WEIGHT = 0.35                       # Weight for Jaccard keyword overlap
MIN_COMBINED_SCORE = 0.30                   # Minimum score to persist a TenderMatch
SHELL_RISK_THRESHOLD = 0.60                 # Contractor risk_score flag boundary

# YAKE keyword extractor config
YAKE_LANGUAGE = "en"
YAKE_MAX_NGRAM = 3
YAKE_DEDUP_THRESHOLD = 0.9
YAKE_TOP_N = 15

# Module-level model singleton (loaded once)
_sentence_model: Optional[SentenceTransformer] = None


def _get_sentence_model() -> SentenceTransformer:
    global _sentence_model
    if _sentence_model is None:
        logger.info("Loading sentence-transformer model: %s", EMBEDDING_MODEL)
        _sentence_model = SentenceTransformer(EMBEDDING_MODEL)
    return _sentence_model


# ---------------------------------------------------------------------------
# Text pre-processing
# ---------------------------------------------------------------------------

_STOP_WORDS = frozenset(
    [
        "the", "a", "an", "is", "in", "at", "of", "and", "or", "to", "for",
        "with", "this", "that", "it", "on", "are", "was", "be", "as", "by",
        "not", "but", "from", "have", "has", "been", "we", "our", "their",
    ]
)


def _clean_text(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _tokenise(text: str) -> set[str]:
    tokens = _clean_text(text).split()
    return {t for t in tokens if t not in _STOP_WORDS and len(t) > 2}


# ---------------------------------------------------------------------------
# Keyword extraction
# ---------------------------------------------------------------------------

def _extract_keywords_yake(text: str) -> list[str]:
    """Extract domain keywords using YAKE (unsupervised, language-agnostic)."""
    kw_extractor = yake.KeywordExtractor(
        lan=YAKE_LANGUAGE,
        n=YAKE_MAX_NGRAM,
        dedupLim=YAKE_DEDUP_THRESHOLD,
        top=YAKE_TOP_N,
        features=None,
    )
    keywords = kw_extractor.extract_keywords(text)
    # YAKE returns (keyword, score) — lower score = more relevant
    return [kw for kw, _score in keywords]


def _extract_entities_spacy(text: str) -> list[str]:
    """Extract named entities (ORG, GPE, PRODUCT, WORK_OF_ART) via spaCy."""
    if not SPACY_AVAILABLE or _nlp is None:
        return []
    doc = _nlp(text[:5000])  # spaCy has a token limit
    return [
        ent.text.lower()
        for ent in doc.ents
        if ent.label_ in {"ORG", "GPE", "PRODUCT", "WORK_OF_ART", "FAC", "LOC"}
    ]


def _extract_all_keywords(text: str) -> list[str]:
    """Combine YAKE + spaCy NER keywords, deduplicated."""
    yake_kws = _extract_keywords_yake(text)
    spacy_ents = _extract_entities_spacy(text)
    combined = list(dict.fromkeys([kw.lower() for kw in yake_kws + spacy_ents]))
    return combined


# ---------------------------------------------------------------------------
# Similarity computation
# ---------------------------------------------------------------------------

def _jaccard_overlap(set_a: set[str], set_b: set[str]) -> float:
    """Jaccard similarity = |A ∩ B| / |A ∪ B|."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def _compute_keyword_overlap(
    complaint_keywords: list[str], tender_keywords: list[str]
) -> tuple[float, list[str]]:
    """
    Return (jaccard_score, matched_keyword_list) for a complaint–tender pair.
    """
    set_c = set(_tokenise(" ".join(complaint_keywords)))
    set_t = set(_tokenise(" ".join(tender_keywords)))
    score = _jaccard_overlap(set_c, set_t)
    matched = sorted(set_c & set_t)
    return score, matched


def _combined_score(semantic: float, keyword: float) -> float:
    return SEMANTIC_WEIGHT * semantic + KEYWORD_WEIGHT * keyword


# ---------------------------------------------------------------------------
# Embedding helpers
# ---------------------------------------------------------------------------

def _embed(texts: list[str]) -> "torch.Tensor":  # type: ignore[name-defined]
    model = _get_sentence_model()
    return model.encode(texts, convert_to_tensor=True, show_progress_bar=False)


def _tender_full_text(tender: Tender) -> str:
    parts = [tender.title or "", tender.description or "", tender.department or ""]
    return " ".join(filter(None, parts))


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

async def _load_all_tenders(db: AsyncSession) -> list[Tender]:
    """Load all tenders. In production, restrict to recent / relevant subset."""
    result = await db.execute(select(Tender))
    return list(result.scalars().all())


async def _load_complaint(db: AsyncSession, complaint_id: int) -> Optional[Complaint]:
    result = await db.execute(
        select(Complaint).where(Complaint.id == complaint_id)
    )
    return result.scalars().first()


async def _check_shell_flag(db: AsyncSession, contractor_id: Optional[int]) -> bool:
    """Return True if the contractor is a shell-company suspect."""
    if contractor_id is None:
        return False
    result = await db.execute(
        select(Contractor.is_shell_company_suspect, Contractor.risk_score).where(
            Contractor.id == contractor_id
        )
    )
    row = result.first()
    if row is None:
        return False
    is_suspect, risk_score = row
    return bool(is_suspect) or (risk_score is not None and risk_score >= SHELL_RISK_THRESHOLD)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

async def match_complaint_to_tenders(complaint_id: int) -> None:
    """
    Main entry point.  Runs full NLP tender-match pipeline for a complaint.

    Steps
    -----
    1. Load complaint from DB.
    2. Extract keywords + spaCy entities from complaint description.
    3. Compute sentence-transformer embedding for complaint.
    4. Load all tenders; compute embeddings + keyword sets.
    5. Rank tenders by combined semantic + keyword score.
    6. Persist top-K TenderMatch rows; flag shell-company associations.
    7. Update complaint.nlp_keywords and complaint.nlp_category.
    """
    async with async_session_factory() as db:
        complaint = await _load_complaint(db, complaint_id)
        if not complaint:
            logger.error("match_complaint_to_tenders: complaint %d not found", complaint_id)
            return

        description = complaint.description or ""
        if not description.strip():
            logger.warning("Complaint %d has empty description; skipping NLP", complaint_id)
            return

        # --- Stage 1: Keyword extraction ---
        complaint_keywords = _extract_all_keywords(description)
        logger.info(
            "Complaint %d keywords: %s", complaint_id, complaint_keywords[:8]
        )

        # --- Stage 2: Semantic embedding ---
        complaint_embedding = _embed([description])

        # --- Stage 3: Load tenders & build corpus ---
        tenders = await _load_all_tenders(db)
        if not tenders:
            logger.warning("No tenders in DB; skipping tender match for complaint %d", complaint_id)
            # Still persist keyword info
            complaint.nlp_keywords = complaint_keywords
            await db.commit()
            return

        tender_texts = [_tender_full_text(t) for t in tenders]
        tender_embeddings = _embed(tender_texts)

        # Precompute tender keyword sets
        tender_keyword_sets: list[list[str]] = [
            _extract_keywords_yake(txt) for txt in tender_texts
        ]

        # --- Stage 4: Compute similarity scores ---
        import torch  # local import to keep module load light if torch absent

        semantic_scores = util.cos_sim(complaint_embedding, tender_embeddings)[0]

        results: list[tuple[float, float, list[str], Tender]] = []
        for idx, tender in enumerate(tenders):
            sem_score = float(semantic_scores[idx])
            kw_score, matched_kws = _compute_keyword_overlap(
                complaint_keywords, tender_keyword_sets[idx]
            )
            combined = _combined_score(sem_score, kw_score)
            if combined >= MIN_COMBINED_SCORE:
                results.append((combined, kw_score, matched_kws, tender))

        # Sort descending by combined score; take top K
        results.sort(key=lambda x: x[0], reverse=True)
        top_results = results[:TOP_K_TENDERS]

        logger.info(
            "Complaint %d: %d tender matches above threshold %.2f",
            complaint_id,
            len(top_results),
            MIN_COMBINED_SCORE,
        )

        # --- Stage 5: Shell-company flagging & persistence ---
        for combined, kw_score, matched_kws, tender in top_results:
            sem_score = combined  # approximation for logging; re-derive below
            sem_score_exact = float(
                util.cos_sim(complaint_embedding, tender_embeddings[tenders.index(tender)])[0][0]
            )

            shell_flagged = await _check_shell_flag(db, tender.awarded_contractor_id)

            # Upsert TenderMatch
            existing_match = await db.execute(
                select(TenderMatch).where(
                    TenderMatch.complaint_id == complaint_id,
                    TenderMatch.tender_id == tender.id,
                )
            )
            match_row = existing_match.scalars().first()

            if match_row:
                match_row.similarity_score = sem_score_exact
                match_row.keyword_overlap_score = kw_score
                match_row.combined_confidence = combined
                match_row.matched_keywords = matched_kws
                match_row.shell_company_flagged = shell_flagged
            else:
                match_row = TenderMatch(
                    complaint_id=complaint_id,
                    tender_id=tender.id,
                    similarity_score=sem_score_exact,
                    keyword_overlap_score=kw_score,
                    combined_confidence=combined,
                    matched_keywords=matched_kws,
                    shell_company_flagged=shell_flagged,
                )
                db.add(match_row)

            if shell_flagged:
                logger.warning(
                    "Shell company flagged: complaint %d ↔ tender %d (contractor %d)",
                    complaint_id,
                    tender.id,
                    tender.awarded_contractor_id,
                )

        # --- Stage 6: Update complaint NLP metadata ---
        complaint.nlp_keywords = complaint_keywords
        complaint.nlp_category = _infer_category(complaint_keywords)

        await db.commit()
        logger.info("Tender match pipeline complete for complaint %d", complaint_id)


# ---------------------------------------------------------------------------
# Category inference (rule-based heuristic)
# ---------------------------------------------------------------------------

_CATEGORY_RULES: dict[str, list[str]] = {
    "road": ["road", "pothole", "footpath", "pavement", "highway", "bridge", "street"],
    "drainage": ["drain", "sewage", "waterlogging", "flood", "sewer", "gutter"],
    "electricity": ["electricity", "power", "streetlight", "transformer", "wire"],
    "water_supply": ["water", "pipe", "borewell", "tap", "supply", "leakage"],
    "sanitation": ["garbage", "waste", "trash", "cleaning", "toilet", "dustbin"],
    "construction": ["construction", "building", "contractor", "tender", "project"],
    "corruption": ["corruption", "bribe", "fraud", "embezzlement", "misuse", "scam"],
}


def _infer_category(keywords: list[str]) -> Optional[str]:
    """Assign the most likely issue category from extracted keywords."""
    keyword_set = set(" ".join(keywords).lower().split())
    scores: dict[str, int] = {}
    for category, terms in _CATEGORY_RULES.items():
        scores[category] = sum(1 for t in terms if t in keyword_set)

    best_cat = max(scores, key=lambda c: scores[c])
    return best_cat if scores[best_cat] > 0 else None
