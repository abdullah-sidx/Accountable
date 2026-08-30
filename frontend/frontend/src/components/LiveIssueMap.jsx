import { useEffect, useMemo, useRef, useState } from "react";
import { issuesApi } from "../services/apiClient";

/**
 * LiveIssueMap — city-wide heatmap of unresolved civic problems.
 *
 * Renders a Google Maps HeatmapLayer when a Maps API key is available
 * (VITE_GOOGLE_MAPS_API_KEY); otherwise falls back to an SVG density map so the
 * view is always useful.
 */

const CITY_CENTER = { lat: 12.9716, lng: 77.5946 };
const MAPS_KEY =
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_GOOGLE_MAPS_API_KEY) || "";

const SAMPLE_POINTS = [
  { id: "1", lat: 12.9752, lng: 77.5905, weight: 9, category: "Pothole", ward: "Ward 12" },
  { id: "2", lat: 12.9689, lng: 77.6011, weight: 7, category: "Garbage", ward: "Ward 08" },
  { id: "3", lat: 12.9801, lng: 77.6032, weight: 5, category: "Street light", ward: "Ward 19" },
  { id: "4", lat: 12.9648, lng: 77.5872, weight: 8, category: "Water leak", ward: "Ward 05" },
  { id: "5", lat: 12.9723, lng: 77.6104, weight: 4, category: "Drainage", ward: "Ward 21" },
  { id: "6", lat: 12.9612, lng: 77.5959, weight: 6, category: "Pothole", ward: "Ward 03" },
  { id: "7", lat: 12.9836, lng: 77.5881, weight: 3, category: "Encroachment", ward: "Ward 17" },
  { id: "8", lat: 12.9770, lng: 77.5789, weight: 7, category: "Garbage", ward: "Ward 11" },
];

function useGoogleMaps(apiKey) {
  const [status, setStatus] = useState(apiKey ? "loading" : "unavailable");

  useEffect(() => {
    if (!apiKey) return;
    if (window.google?.maps?.visualization) {
      setStatus("ready");
      return;
    }
    const existing = document.querySelector("script[data-accountable-maps]");
    const onLoad = () => setStatus("ready");
    const onError = () => setStatus("unavailable");
    if (existing) {
      existing.addEventListener("load", onLoad);
      existing.addEventListener("error", onError);
      return () => {
        existing.removeEventListener("load", onLoad);
        existing.removeEventListener("error", onError);
      };
    }
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=visualization`;
    script.async = true;
    script.dataset.accountableMaps = "true";
    script.addEventListener("load", onLoad);
    script.addEventListener("error", onError);
    document.head.appendChild(script);
    return () => {
      script.removeEventListener("load", onLoad);
      script.removeEventListener("error", onError);
    };
  }, [apiKey]);

  return status;
}

function SvgDensityMap({ points, onHover }) {
  const lats = points.map((p) => p.lat);
  const lngs = points.map((p) => p.lng);
  const minLat = Math.min(...lats) - 0.004;
  const maxLat = Math.max(...lats) + 0.004;
  const minLng = Math.min(...lngs) - 0.004;
  const maxLng = Math.max(...lngs) + 0.004;

  const project = (p) => ({
    x: ((p.lng - minLng) / (maxLng - minLng)) * 100,
    y: (1 - (p.lat - minLat) / (maxLat - minLat)) * 100,
  });

  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="h-full w-full">
      <defs>
        <radialGradient id="heat" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="oklch(0.62 0.22 25)" stopOpacity="0.55" />
          <stop offset="55%" stopColor="oklch(0.78 0.16 70)" stopOpacity="0.28" />
          <stop offset="100%" stopColor="oklch(0.62 0.19 265)" stopOpacity="0" />
        </radialGradient>
        <pattern id="grid" width="8" height="8" patternUnits="userSpaceOnUse">
          <path d="M8 0H0V8" fill="none" stroke="currentColor" strokeWidth="0.2" opacity="0.35" />
        </pattern>
      </defs>
      <rect width="100" height="100" className="fill-map-canvas" />
      <rect width="100" height="100" fill="url(#grid)" className="text-map-grid" />
      {points.map((p) => {
        const { x, y } = project(p);
        return (
          <circle
            key={`h-${p.id}`}
            cx={x}
            cy={y}
            r={4 + p.weight * 1.6}
            fill="url(#heat)"
          />
        );
      })}
      {points.map((p) => {
        const { x, y } = project(p);
        return (
          <circle
            key={`d-${p.id}`}
            cx={x}
            cy={y}
            r={1.1}
            className="fill-primary"
            onMouseEnter={() => onHover(p)}
            onMouseLeave={() => onHover(null)}
          />
        );
      })}
    </svg>
  );
}

export default function LiveIssueMap() {
  const mapsStatus = useGoogleMaps(MAPS_KEY);
  const mapNodeRef = useRef(null);
  const [points, setPoints] = useState(SAMPLE_POINTS);
  const [source, setSource] = useState("sample");
  const [hovered, setHovered] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState("All");

  useEffect(() => {
    let cancelled = false;
    issuesApi
      .heatmap()
      .then((data) => {
        const rows = Array.isArray(data) ? data : data?.points;
        if (!cancelled && Array.isArray(rows) && rows.length) {
          setPoints(rows);
          setSource("live");
        }
      })
      .catch(() => {
        if (!cancelled) setSource("sample");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const categories = useMemo(
    () => ["All", ...Array.from(new Set(points.map((p) => p.category).filter(Boolean)))],
    [points],
  );

  const visible = useMemo(
    () => (categoryFilter === "All" ? points : points.filter((p) => p.category === categoryFilter)),
    [points, categoryFilter],
  );

  useEffect(() => {
    if (mapsStatus !== "ready" || !mapNodeRef.current) return;
    const { google } = window;
    const map = new google.maps.Map(mapNodeRef.current, {
      center: CITY_CENTER,
      zoom: 13,
      disableDefaultUI: false,
      styles: [{ elementType: "geometry", stylers: [{ color: "#f7f8fc" }] }],
    });
    const layer = new google.maps.visualization.HeatmapLayer({
      data: visible.map(
        (p) => new google.maps.visualization.WeightedLocation({
          location: new google.maps.LatLng(p.lat, p.lng),
          weight: p.weight ?? 1,
        }),
      ),
      radius: 34,
      opacity: 0.75,
    });
    layer.setMap(map);
    return () => layer.setMap(null);
  }, [mapsStatus, visible]);

  const unresolved = visible.reduce((sum, p) => sum + (p.weight ?? 1), 0);

  return (
    <section className="rounded-2xl border border-border bg-card p-5 shadow-soft">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold tracking-tight text-foreground">Live issue map</h2>
          <p className="text-sm text-muted-foreground">
            City-wide heatmap of unresolved civic problems ·{" "}
            {source === "live" ? "live backend feed" : "sample data (backend offline)"}
          </p>
        </div>
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

      <div className="relative mt-4 h-80 overflow-hidden rounded-xl border border-border">
        {mapsStatus === "ready" ? (
          <div ref={mapNodeRef} className="h-full w-full" />
        ) : (
          <SvgDensityMap points={visible} onHover={setHovered} />
        )}
        {hovered && (
          <div className="pointer-events-none absolute left-3 top-3 rounded-lg border border-border bg-card/95 px-3 py-2 text-xs shadow-soft">
            <p className="font-semibold text-foreground">{hovered.category}</p>
            <p className="text-muted-foreground">
              {hovered.ward} · severity {hovered.weight}
            </p>
          </div>
        )}
      </div>

      <dl className="mt-4 grid grid-cols-3 gap-3 text-center">
        <div className="rounded-xl bg-muted p-3">
          <dt className="text-xs text-muted-foreground">Open reports</dt>
          <dd className="text-xl font-semibold text-foreground">{visible.length}</dd>
        </div>
        <div className="rounded-xl bg-muted p-3">
          <dt className="text-xs text-muted-foreground">Severity load</dt>
          <dd className="text-xl font-semibold text-foreground">{unresolved}</dd>
        </div>
        <div className="rounded-xl bg-muted p-3">
          <dt className="text-xs text-muted-foreground">Wards affected</dt>
          <dd className="text-xl font-semibold text-foreground">
            {new Set(visible.map((p) => p.ward)).size}
          </dd>
        </div>
      </dl>
    </section>
  );
}
