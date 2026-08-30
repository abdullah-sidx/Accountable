"""
Accountable Platform — CV Deduplication Service
=================================================
Merges duplicate public complaints based on:
  1. Geographic proximity  – complaints within GEO_RADIUS_METRES are candidates.
  2. Visual similarity     – OpenCV ORB feature matching on attached images.
  3. Text similarity       – TF-IDF cosine fallback when no images are present.

A complaint is marked duplicate when the combined confidence score exceeds
DUPLICATE_THRESHOLD (default 0.75).

Entry point
-----------
    await deduplicate_complaints(new_complaint_id: int) -> None

Called as a FastAPI BackgroundTask immediately after a new complaint is saved.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from math import asin, cos, radians, sin, sqrt
from typing import Optional

import cv2
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import async_session_factory
from app.database.models import Complaint, ComplaintImage, ComplaintStatus

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tuneable constants
# ---------------------------------------------------------------------------

GEO_RADIUS_METRES: float = 500.0       # Candidate window for dedup search
IMAGE_MATCH_THRESHOLD: float = 0.55    # ORB good-match ratio (Lowe's test)
TEXT_SIMILARITY_THRESHOLD: float = 0.60
DUPLICATE_THRESHOLD: float = 0.75      # Final combined score to call it a dup

# Weight distribution for combined score
W_GEO = 0.20
W_IMAGE = 0.50
W_TEXT = 0.30


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class CandidatePair:
    existing_id: int
    geo_score: float = 0.0
    image_score: float = 0.0
    text_score: float = 0.0
    combined_score: float = field(init=False)

    def __post_init__(self) -> None:
        self.combined_score = (
            W_GEO * self.geo_score
            + W_IMAGE * self.image_score
            + W_TEXT * self.text_score
        )


# ---------------------------------------------------------------------------
# Haversine distance
# ---------------------------------------------------------------------------

def _haversine_metres(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in metres between two GPS coordinates."""
    R = 6_371_000  # Earth radius in metres
    φ1, φ2 = radians(lat1), radians(lat2)
    Δφ = radians(lat2 - lat1)
    Δλ = radians(lon2 - lon1)
    a = sin(Δφ / 2) ** 2 + cos(φ1) * cos(φ2) * sin(Δλ / 2) ** 2
    return 2 * R * asin(sqrt(a))


def _geo_score(distance_m: float) -> float:
    """
    Convert raw distance to a [0, 1] proximity score.
    Score = 1.0 at distance 0, decays linearly to 0.0 at GEO_RADIUS_METRES.
    """
    if distance_m >= GEO_RADIUS_METRES:
        return 0.0
    return 1.0 - (distance_m / GEO_RADIUS_METRES)


# ---------------------------------------------------------------------------
# OpenCV ORB feature extraction & matching
# ---------------------------------------------------------------------------

def _load_image_gray(file_path: str) -> Optional[np.ndarray]:
    """Load an image from disk; return grayscale ndarray or None on failure."""
    if not os.path.exists(file_path):
        logger.warning("Image file not found: %s", file_path)
        return None
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        logger.warning("cv2.imread failed for: %s", file_path)
    return img


def _extract_orb_descriptors(
    img: np.ndarray,
    n_features: int = 500,
) -> Optional[np.ndarray]:
    """Return ORB descriptors for a grayscale image."""
    orb = cv2.ORB_create(nfeatures=n_features)
    keypoints, descriptors = orb.detectAndCompute(img, None)
    return descriptors  # shape (N, 32) uint8, or None if no keypoints


def _match_descriptors(desc1: np.ndarray, desc2: np.ndarray) -> float:
    """
    Use BFMatcher + Lowe's ratio test to compute a visual similarity score.
    Returns fraction of good matches out of total keypoints in the smaller set.
    """
    if desc1 is None or desc2 is None:
        return 0.0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    try:
        knn_matches = bf.knnMatch(desc1, desc2, k=2)
    except cv2.error as exc:
        logger.debug("BFMatcher knnMatch failed: %s", exc)
        return 0.0

    good_matches = [
        m for m, n in knn_matches if m.distance < IMAGE_MATCH_THRESHOLD * n.distance
    ]

    min_keypoints = min(len(desc1), len(desc2))
    if min_keypoints == 0:
        return 0.0

    return len(good_matches) / min_keypoints


def _image_similarity_score(paths_a: list[str], paths_b: list[str]) -> float:
    """
    Compute best-of-all-pairs ORB similarity between two complaints' image sets.
    Returns 0.0 if either complaint has no images.
    """
    if not paths_a or not paths_b:
        return 0.0

    best = 0.0
    for path_a in paths_a:
        img_a = _load_image_gray(path_a)
        if img_a is None:
            continue
        desc_a = _extract_orb_descriptors(img_a)

        for path_b in paths_b:
            img_b = _load_image_gray(path_b)
            if img_b is None:
                continue
            desc_b = _extract_orb_descriptors(img_b)

            score = _match_descriptors(desc_a, desc_b)
            if score > best:
                best = score

    return min(best, 1.0)


def _cache_feature_vector(image: ComplaintImage) -> Optional[np.ndarray]:
    """
    Load / generate and cache ORB descriptors for a complaint image.
    Descriptors are serialised to JSON in the DB column `cv_feature_vector`.
    """
    if image.cv_feature_vector:
        arr = np.array(image.cv_feature_vector, dtype=np.uint8)
        return arr if arr.ndim == 2 else None

    img = _load_image_gray(image.file_path)
    if img is None:
        return None

    descriptors = _extract_orb_descriptors(img)
    if descriptors is not None:
        image.cv_feature_vector = descriptors.tolist()  # persist on next flush
    return descriptors


# ---------------------------------------------------------------------------
# Text similarity (TF-IDF fallback)
# ---------------------------------------------------------------------------

def _text_similarity(text_a: str, text_b: str) -> float:
    """Cosine similarity between two complaint descriptions via TF-IDF."""
    if not text_a.strip() or not text_b.strip():
        return 0.0
    try:
        vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        tfidf = vectorizer.fit_transform([text_a, text_b])
        score = float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0])
        return min(score, 1.0)
    except ValueError:
        return 0.0


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

async def _fetch_complaint_with_images(
    db: AsyncSession, complaint_id: int
) -> Optional[Complaint]:
    """Load a Complaint with its images eagerly."""
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(Complaint)
        .options(selectinload(Complaint.images))
        .where(Complaint.id == complaint_id)
    )
    return result.scalars().first()


async def _fetch_open_complaints_near(
    db: AsyncSession,
    lat: float,
    lon: float,
    exclude_id: int,
) -> list[Complaint]:
    """
    Return non-duplicate, non-closed complaints within a bounding box that
    approximates GEO_RADIUS_METRES.  Exact Haversine filter applied in Python.
    """
    from sqlalchemy.orm import selectinload

    # ~1° lat ≈ 111 km  →  radius in degrees
    deg_radius = GEO_RADIUS_METRES / 111_000

    result = await db.execute(
        select(Complaint)
        .options(selectinload(Complaint.images))
        .where(
            Complaint.id != exclude_id,
            Complaint.is_duplicate.is_(False),
            Complaint.status.notin_(
                [ComplaintStatus.CLOSED, ComplaintStatus.RESOLVED]
            ),
            Complaint.latitude.between(lat - deg_radius, lat + deg_radius),
            Complaint.longitude.between(lon - deg_radius, lon + deg_radius),
        )
    )
    candidates = result.scalars().all()

    # Exact Haversine filter
    return [
        c
        for c in candidates
        if _haversine_metres(lat, lon, c.latitude, c.longitude) <= GEO_RADIUS_METRES
    ]


# ---------------------------------------------------------------------------
# Core deduplication pipeline
# ---------------------------------------------------------------------------

async def deduplicate_complaints(new_complaint_id: int) -> None:
    """
    Main entry point.  Called as a background task after a complaint is saved.

    Algorithm
    ---------
    1. Load the new complaint and its images.
    2. Fetch open complaints within GEO_RADIUS_METRES.
    3. For each candidate compute geo, image, and text scores.
    4. Build a combined score; if ≥ DUPLICATE_THRESHOLD mark as duplicate
       of the highest-scoring existing complaint.
    5. Persist changes.
    """
    async with async_session_factory() as db:
        new_complaint = await _fetch_complaint_with_images(db, new_complaint_id)
        if not new_complaint:
            logger.error("deduplicate_complaints: complaint %d not found", new_complaint_id)
            return

        candidates = await _fetch_open_complaints_near(
            db,
            new_complaint.latitude,
            new_complaint.longitude,
            exclude_id=new_complaint_id,
        )

        if not candidates:
            logger.info(
                "No geographic candidates found for complaint %d", new_complaint_id
            )
            return

        logger.info(
            "Deduplication: evaluating %d candidates for complaint %d",
            len(candidates),
            new_complaint_id,
        )

        new_image_paths = [img.file_path for img in new_complaint.images]
        pairs: list[CandidatePair] = []

        for existing in candidates:
            dist_m = _haversine_metres(
                new_complaint.latitude,
                new_complaint.longitude,
                existing.latitude,
                existing.longitude,
            )
            geo = _geo_score(dist_m)

            existing_image_paths = [img.file_path for img in existing.images]
            img_score = _image_similarity_score(new_image_paths, existing_image_paths)

            txt_score = _text_similarity(
                new_complaint.description, existing.description
            )

            pair = CandidatePair(
                existing_id=existing.id,
                geo_score=geo,
                image_score=img_score,
                text_score=txt_score,
            )
            pairs.append(pair)
            logger.debug(
                "Complaint %d vs %d → geo=%.3f img=%.3f txt=%.3f combined=%.3f",
                new_complaint_id,
                existing.id,
                geo,
                img_score,
                txt_score,
                pair.combined_score,
            )

        # Pick best match
        best = max(pairs, key=lambda p: p.combined_score)

        if best.combined_score >= DUPLICATE_THRESHOLD:
            logger.info(
                "Complaint %d flagged as DUPLICATE of %d (score=%.3f)",
                new_complaint_id,
                best.existing_id,
                best.combined_score,
            )
            new_complaint.is_duplicate = True
            new_complaint.duplicate_of_id = best.existing_id
            new_complaint.dedup_confidence_score = best.combined_score
            new_complaint.status = ComplaintStatus.DUPLICATE
        else:
            logger.info(
                "Complaint %d is NOT a duplicate (best score=%.3f)",
                new_complaint_id,
                best.combined_score,
            )

        await db.commit()
