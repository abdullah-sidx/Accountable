import { useEffect, useState } from "react";
import { gamificationApi } from "../services/apiClient";

/**
 * GamificationCard — civic points, badges and downloadable certificates.
 */

const FALLBACK = {
  name: "Citizen",
  city: "Bhatkal, Karnataka",
  city_rank: null,
  points: 1240,
  level: "Ward Watchdog",
  nextLevelAt: 1500,
  reportsFiled: 34,
  reportsResolved: 21,
  badges: [
    { id: "first-snap",     label: "First Snap",     earned: true,  hint: "Filed your first report" },
    { id: "pothole-patrol", label: "Pothole Patrol", earned: true,  hint: "10 road reports" },
    { id: "fund-sleuth",    label: "Fund Sleuth",    earned: true,  hint: "Audited 5 fund trails" },
    { id: "ward-champion",  label: "Ward Champion",  earned: false, hint: "50 resolved reports" },
    { id: "civic-marathon", label: "Civic Marathon", earned: false, hint: "90-day streak" },
  ],
};

export default function GamificationCard({ userId = "me" }) {
  const [profile, setProfile] = useState(FALLBACK);
  const [source, setSource] = useState("sample");
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    gamificationApi
      .profile(userId)
      .then((data) => {
        if (!cancelled && data && typeof data === "object") {
          setProfile({ ...FALLBACK, ...data });
          setSource("live");
        }
      })
      .catch(() => {
        if (!cancelled) setSource("sample");
      });
    return () => {
      cancelled = true;
    };
  }, [userId]);

  const progress = Math.min(100, Math.round((profile.points / profile.nextLevelAt) * 100));

  const downloadCertificate = () => {
    setDownloading(true);
    const url = gamificationApi.certificateUrl(userId);
    const link = document.createElement("a");
    link.href = url;
    link.download = `accountable-certificate-${userId}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => setDownloading(false), 800);
  };

  return (
    <section className="rounded-2xl border border-border bg-card p-5 shadow-soft">
      <header className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold tracking-tight text-foreground">Your civic score</h2>
          <p className="text-sm text-muted-foreground">
            {profile.level} · {profile.reportsResolved}/{profile.reportsFiled} reports resolved
          </p>
          {/* City + rank row */}
          <p className="mt-0.5 text-xs text-muted-foreground">
            {profile.city ?? "—"}
            {profile.city_rank != null && (
              <span className="ml-2 inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-[11px] font-semibold text-primary">
                #{profile.city_rank} city rank
              </span>
            )}
          </p>
          {/* Live / offline badge */}
          <span
            className={`mt-1.5 inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${
              source === "live"
                ? "bg-green-100 text-green-700"
                : "bg-muted text-muted-foreground"
            }`}
          >
            <span
              className={`inline-block h-1.5 w-1.5 rounded-full ${
                source === "live" ? "bg-green-500" : "bg-gray-400"
              }`}
            />
            {source === "live" ? "Backend connected" : "Sample data"}
          </span>
        </div>
        <div className="rounded-2xl bg-primary/10 px-4 py-2 text-center">
          <p className="text-2xl font-semibold tabular-nums text-primary">{profile.points}</p>
          <p className="text-[11px] uppercase tracking-wide text-muted-foreground">points</p>
        </div>
      </header>

      <div className="mt-4">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Progress to next level</span>
          <span className="tabular-nums">
            {profile.points} / {profile.nextLevelAt}
          </span>
        </div>
        <div className="mt-1.5 h-2.5 w-full overflow-hidden rounded-full bg-muted">
          <div className="h-full rounded-full bg-primary" style={{ width: `${progress}%` }} />
        </div>
      </div>

      <ul className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-3">
        {profile.badges.map((badge) => (
          <li
            key={badge.id}
            title={badge.hint}
            className={`rounded-xl border p-3 text-center ${
              badge.earned
                ? "border-primary/30 bg-primary/5"
                : "border-dashed border-border bg-background opacity-60"
            }`}
          >
            <span
              aria-hidden="true"
              className={`mx-auto flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold ${
                badge.earned
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {badge.label.charAt(0)}
            </span>
            <p className="mt-2 text-xs font-medium text-foreground">{badge.label}</p>
            <p className="text-[11px] text-muted-foreground">{badge.hint}</p>
          </li>
        ))}
      </ul>

      <button
        type="button"
        onClick={downloadCertificate}
        disabled={downloading}
        className="mt-5 w-full rounded-xl border border-primary px-4 py-2.5 text-sm font-semibold text-primary transition-colors hover:bg-primary hover:text-primary-foreground disabled:opacity-60"
      >
        {downloading ? "Preparing certificate…" : "Download civic certificate (PDF)"}
      </button>
    </section>
  );
}
