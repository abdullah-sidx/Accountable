/**
 * LeafletMap.jsx
 *
 * IMPORTANT: This file must ONLY be imported dynamically (client-side only).
 * It uses react-leaflet and leaflet/dist/leaflet.css which both reference
 * `window` at module evaluation time — importing them during SSR throws:
 *   ReferenceError: window is not defined
 *
 * LiveIssueMap.jsx guards the import with typeof window !== 'undefined'.
 */

import { useEffect } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";

// ── Category colours ─────────────────────────────────────────────────────────

const CATEGORY_COLORS = {
  Pothole:        "#ef4444", // red-500
  Drainage:       "#3b82f6", // blue-500
  Garbage:        "#f97316", // orange-500
  "Water leak":   "#06b6d4", // cyan-500
  "Street light": "#eab308", // yellow-500
  Encroachment:   "#8b5cf6", // violet-500
};

const DEFAULT_COLOR = "#6b7280";

function categoryColor(cat) {
  return CATEGORY_COLORS[cat] ?? DEFAULT_COLOR;
}

// ── MapFlyTo — re-centres on mount ───────────────────────────────────────────

function MapFlyTo({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: true });
  }, [map, center, zoom]);
  return null;
}

// ── In-map legend ────────────────────────────────────────────────────────────

function MapLegend() {
  return (
    <div
      style={{
        position: "absolute",
        bottom: 24,
        right: 12,
        zIndex: 1000,
        background: "var(--card, #fff)",
        border: "1px solid var(--border, #e5e7eb)",
        borderRadius: 12,
        padding: "10px 12px",
        fontSize: 11,
        pointerEvents: "none",
        boxShadow: "0 1px 4px rgba(0,0,0,.1)",
      }}
    >
      <p style={{ fontWeight: 600, marginBottom: 6 }}>Issue type</p>
      <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "flex", flexDirection: "column", gap: 4 }}>
        {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
          <li key={cat} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span
              style={{
                display: "inline-block",
                width: 10,
                height: 10,
                borderRadius: "50%",
                backgroundColor: color,
                flexShrink: 0,
              }}
            />
            <span style={{ color: "#6b7280" }}>{cat}</span>
          </li>
        ))}
      </ul>
      <p style={{ marginTop: 6, color: "#9ca3af", fontSize: 10 }}>Circle size = severity</p>
    </div>
  );
}

// ── LeafletMap — the actual Leaflet JSX tree ─────────────────────────────────

export default function LeafletMap({ center, zoom, points }) {
  return (
    <div style={{ position: "relative", height: "100%", width: "100%" }}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: "100%", width: "100%", zIndex: 0 }}
        scrollWheelZoom
      >
        <MapFlyTo center={center} zoom={zoom} />

        {/* OpenStreetMap tiles — no API key required */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Issue markers */}
        {points.map((point) => {
          const radius = 4 + (point.weight ?? 1) * 1.4;
          const color = categoryColor(point.category);

          // Deterministic photo seed per issue
          const thumbSeed = encodeURIComponent(
            `${point.category ?? "civic"}-bhatkal-${point.id}`,
          );
          const thumbUrl = `https://source.unsplash.com/160x90/?${thumbSeed}`;

          const desc =
            point.description ??
            `${point.category ?? "Issue"} reported near ${point.ward ?? "this location"}. Severity ${point.weight ?? point.intensity ?? "—"}/10. Awaiting resolution.`;

          const dupCount = point.duplicate_count ?? 2;

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
              <Popup minWidth={200} maxWidth={240}>
                {/* Thumbnail */}
                <img
                  src={thumbUrl}
                  alt={`Photo of ${point.category ?? "civic issue"}`}
                  width={224}
                  height={90}
                  style={{ width: "100%", height: 90, objectFit: "cover", borderRadius: 6, display: "block" }}
                  onError={(e) => { e.currentTarget.style.display = "none"; }}
                />

                {/* Info */}
                <div style={{ marginTop: 8 }}>
                  <p style={{ fontWeight: 600, fontSize: 13, margin: 0 }}>
                    {point.category ?? "Issue"}
                  </p>
                  <p style={{ fontSize: 11, color: "#6b7280", margin: "2px 0 6px" }}>
                    {point.ward ?? "Unknown ward"}
                  </p>
                  <p style={{ fontSize: 12, lineHeight: 1.45, margin: "0 0 8px" }}>
                    {desc}
                  </p>

                  {/* CV Deduplication badge */}
                  <span
                    style={{
                      display: "inline-flex",
                      alignItems: "center",
                      gap: 4,
                      backgroundColor: "#fef3c7",
                      color: "#92400e",
                      fontSize: 11,
                      fontWeight: 600,
                      padding: "2px 8px",
                      borderRadius: 999,
                      border: "1px solid #fcd34d",
                    }}
                    title="Backend CV deduplication matched this report to similar nearby submissions"
                  >
                    🔍 Duplicate Reports: {dupCount}
                  </span>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {/* Legend lives outside MapContainer to dodge z-index conflicts */}
      <MapLegend />
    </div>
  );
}
