import { useEffect, useMemo, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { issuesApi } from "../services/apiClient";

/**
 * LiveIssueMap — city-wide heatmap of unresolved civic problems.
 *
 * Renders a real Leaflet map centred on Bhatkal, Karnataka (13.9820, 74.5560).
 * CircleMarkers are coloured and sized by issue category and severity.
 * Data is fetched live from the FastAPI backend at /api/issues/heatmap.
 * Falls back to SAMPLE_POINTS when the backend is offline.
 */

// ── Constants ────────────────────────────────────────────────────────────────

const BHATKAL_CENTER = [13.982, 74.556];
const DEFAULT_ZOOM = 14;

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

// Colour palette per issue category (Tailwind-matching hex values)
const CATEGORY_COLORS = {
  Pothole:      "#ef4444", // red-500
  Drainage:     "#3b82f6", // blue-500
  Garbage:      "#f97316", // orange-500
  "Water leak": "#06b6d4", // cyan-500
  "Street light": "#eab308", // yellow-500
  Encroachment: "#8b5cf6", // violet-500
};

const DEFAULT_COLOR = "#6b7280"; // gray-500

function categoryColor(cat) {
  return CATEGORY_COLORS[cat] ?? DEFAULT_COLOR;
}

// ── Fly-to helper (re-centres map when Bhatkal center is confirmed) ──────────

function MapFlyTo({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: true });
  }, [map, center, zoom]);
  return null;
}

// ── Legend ───────────────────────────────────────────────────────────────────

function MapLegend() {
  return (
    <div className="pointer-events-none absolute bottom-6 right-3 z-[1000] rounded-xl border border-border bg-card/95 p-3 shadow-soft text-xs">
      <p className="mb-2 font-semibold text-foreground">Issue type</p>
      <ul className="space-y-1">
        {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
          <li key={cat} className="flex items-center gap-2">
            <span
              className="inline-block h-2.5 w-2.5 flex-shrink-0 rounded-full"
              style={{ backgroundColor: color }}
            />
            <span className="text-muted-foreground">{cat}</span>
          </li>
        ))}
      </ul>
      <p className="mt-2 text-[10px] text-muted-foreground">Circle size = severity</p>
    </div>
  );
}

// ── Main component ───────────────────────────────────────────────────────────

export default function LiveIssueMap() {
  const [points, setPoints] = useState(SAMPLE_POINTS);
  const [source, setSource] = useState("sample");
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState("All");

  // Fetch live data from FastAPI backend
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
      .catch(() => {
        if (!cancelled) setSource("sample");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Build category list dynamically from fetched data
  const categories = useMemo(
    () => ["All", ...Array.from(new Set(points.map((p) => p.category).filter(Boolean)))],
    [points],
  );

  // Apply active filter
  const visible = useMemo(
    () =>
      categoryFilter === "All"
        ? points
        : points.filter((p) => p.category === categoryFilter),
    [points, categoryFilter],
  );

  const severityLoad = visible.reduce((sum, p) => sum + (p.weight ?? 1), 0);
  const wardsAffected = new Set(visible.map((p) => p.ward)).size;

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

      {/* Map container */}
      <div className="relative mt-4 h-80 overflow-hidden rounded-xl border border-border">
        <MapContainer
          center={BHATKAL_CENTER}
          zoom={DEFAULT_ZOOM}
          className="h-full w-full"
          scrollWheelZoom={true}
          // zIndex management: keep Leaflet controls above the card but below modal overlays
          style={{ zIndex: 0 }}
        >
          <MapFlyTo center={BHATKAL_CENTER} zoom={DEFAULT_ZOOM} />

          {/* OpenStreetMap tiles — no API key required */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Issue markers */}
          {visible.map((point) => {
            const radius = 4 + (point.weight ?? 1) * 1.4; // 5 – 18 px
            const color = categoryColor(point.category);
            return (
              <CircleMarker
                key={point.id}
                center={[point.lat, point.lng]}
                radius={radius}
                pathOptions={{
                  color,
                  fillColor: color,
                  fillOpacity: 0.72,
                  weight: 1.5,
                }}
              >
                <Popup>
                  <div className="text-sm">
                    <p className="font-semibold">{point.category}</p>
                    <p className="text-muted-foreground">{point.ward}</p>
                    <p className="mt-1">
                      Severity:{" "}
                      <span className="font-medium">{point.weight ?? point.intensity ?? "—"}</span>
                      /10
                    </p>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>

        {/* Legend overlay (rendered outside MapContainer to avoid Leaflet z-index issues) */}
        <MapLegend />
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
