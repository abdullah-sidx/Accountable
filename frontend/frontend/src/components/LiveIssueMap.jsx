import { useEffect, useMemo, useState } from "react";
import { issuesApi } from "../services/apiClient";

/**
 * LiveIssueMap — city-wide heatmap of unresolved civic problems.
 *
 * SSR-SAFE: react-leaflet and leaflet/dist/leaflet.css are loaded lazily
 * inside a useEffect (client-only) via dynamic import().  The component
 * renders a placeholder skeleton during SSR and on first hydration, then
 * swaps in the real <LeafletMap> once the browser module is ready.
 *
 * This eliminates:
 *   ReferenceError: window is not defined
 * which Leaflet throws when evaluated in a Node SSR context.
 */

// ── Constants ─────────────────────────────────────────────────────────────────

const BHATKAL_CENTER = [13.982, 74.556];
const DEFAULT_ZOOM   = 14;

const SAMPLE_POINTS = [
  { id: "s1", lat: 13.9850, lng: 74.5520, weight: 9, category: "Pothole",      ward: "Ward 01 – Market" },
  { id: "s2", lat: 13.9831, lng: 74.5498, weight: 7, category: "Drainage",     ward: "Ward 02 – Bus Stand" },
  { id: "s3", lat: 13.9812, lng: 74.5561, weight: 8, category: "Garbage",      ward: "Ward 03 – Masjid Rd" },
  { id: "s4", lat: 13.9876, lng: 74.5483, weight: 5, category: "Water leak",   ward: "Ward 04 – Police Stn" },
  { id: "s5", lat: 13.9798, lng: 74.5539, weight: 6, category: "Street light", ward: "Ward 05 – NH-66" },
  { id: "s6", lat: 13.9904, lng: 74.5507, weight: 4, category: "Encroachment", ward: "Ward 06 – Shirali Rd" },
  { id: "s7", lat: 13.9921, lng: 74.5555, weight: 8, category: "Pothole",      ward: "Ward 07 – Ottinene" },
  { id: "s8", lat: 13.9762, lng: 74.5503, weight: 7, category: "Garbage",      ward: "Ward 09 – Maravanthe" },
];

// ── Skeleton shown during SSR / first render ──────────────────────────────────

function MapSkeleton() {
  return (
    <div
      className="h-full w-full animate-pulse rounded-xl bg-muted"
      aria-label="Map loading…"
      style={{ minHeight: 320 }}
    />
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export default function LiveIssueMap() {
  // Lazily-loaded Leaflet component — null until the browser has loaded it
  const [LeafletMap, setLeafletMap] = useState(null);

  // Data state
  const [points, setPoints]               = useState(SAMPLE_POINTS);
  const [source, setSource]               = useState("sample");
  const [loading, setLoading]             = useState(true);
  const [categoryFilter, setCategoryFilter] = useState("All");

  // ── Dynamic import: only runs in the browser ──────────────────────────────
  useEffect(() => {
    // typeof window guard is redundant inside useEffect but makes intent clear
    if (typeof window === "undefined") return;

    import("./LeafletMap.jsx")
      .then((mod) => setLeafletMap(() => mod.default))
      .catch((err) => console.error("Failed to load Leaflet:", err));
  }, []);

  // ── Fetch heatmap data from FastAPI backend ───────────────────────────────
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    issuesApi
      .heatmap()
      .then((data) => {
        if (cancelled) return;
        const rows = Array.isArray(data) ? data : data?.points;
        if (Array.isArray(rows) && rows.length > 0) {
          setPoints(rows);
          setSource("live");
        } else {
          setSource("sample");
        }
      })
      .catch(() => { if (!cancelled) setSource("sample"); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  // ── Derived state ─────────────────────────────────────────────────────────
  const categories = useMemo(
    () => ["All", ...Array.from(new Set(points.map((p) => p.category).filter(Boolean)))],
    [points],
  );

  const visible = useMemo(
    () => categoryFilter === "All" ? points : points.filter((p) => p.category === categoryFilter),
    [points, categoryFilter],
  );

  const severityLoad   = visible.reduce((sum, p) => sum + (p.weight ?? 1), 0);
  const wardsAffected  = new Set(visible.map((p) => p.ward)).size;

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <section className="rounded-2xl border border-border bg-card p-5 shadow-soft">

      {/* Header */}
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold tracking-tight text-foreground">
            Live issue map
          </h2>
          <p className="text-sm text-muted-foreground">
            Bhatkal, Karnataka ·{" "}
            {loading
              ? "loading…"
              : source === "live"
                ? "live backend feed"
                : "sample data (backend offline)"}
          </p>
        </div>

        {/* Category filter pills */}
        <div className="flex flex-wrap gap-2">
          {categories.map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setCategoryFilter(c)}
              className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
                categoryFilter === c
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-border bg-background text-muted-foreground hover:border-primary/40 hover:text-foreground"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </header>

      {/* Map area */}
      <div className="relative mt-4 h-80 overflow-hidden rounded-xl border border-border">
        {LeafletMap ? (
          // Real interactive map — only rendered client-side after dynamic import
          <LeafletMap
            center={BHATKAL_CENTER}
            zoom={DEFAULT_ZOOM}
            points={visible}
          />
        ) : (
          // SSR / hydration placeholder — no window access
          <MapSkeleton />
        )}
      </div>

      {/* Stats strip */}
      <dl className="mt-4 grid grid-cols-3 gap-3 text-center">
        <div className="rounded-xl bg-muted p-3">
          <dt className="text-xs text-muted-foreground">Open reports</dt>
          <dd className="text-xl font-semibold text-foreground">{visible.length}</dd>
        </div>
        <div className="rounded-xl bg-muted p-3">
          <dt className="text-xs text-muted-foreground">Severity load</dt>
          <dd className="text-xl font-semibold text-foreground">{severityLoad}</dd>
        </div>
        <div className="rounded-xl bg-muted p-3">
          <dt className="text-xs text-muted-foreground">Wards affected</dt>
          <dd className="text-xl font-semibold text-foreground">{wardsAffected}</dd>
        </div>
      </dl>
    </section>
  );
}
