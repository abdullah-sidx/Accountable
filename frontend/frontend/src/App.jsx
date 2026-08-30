import { useState } from "react";
import LiveIssueMap from "./components/LiveIssueMap";
import SnapTagForm from "./components/SnapTagForm";
import FundTrailTable from "./components/FundTrailTable";
import GamificationCard from "./components/GamificationCard";

/**
 * App — main layout and view routing for the Accountable civic transparency platform.
 */

const VIEWS = [
  { id: "map", label: "Live map" },
  { id: "report", label: "Report an issue" },
  { id: "funds", label: "Fund trail" },
  { id: "rewards", label: "My impact" },
];

export default function App() {
  const [view, setView] = useState("map");

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-10 border-b border-border bg-background/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <div className="flex items-center gap-2.5">
            <span
              aria-hidden="true"
              className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-sm font-bold text-primary-foreground"
            >
              A
            </span>
            <div>
              <p className="text-sm font-semibold tracking-tight">Accountable</p>
              <p className="text-xs text-muted-foreground">Civic transparency, in public</p>
            </div>
          </div>
          <nav aria-label="Main sections" className="flex flex-wrap gap-1.5">
            {VIEWS.map((v) => (
              <button
                key={v.id}
                type="button"
                onClick={() => setView(v.id)}
                aria-current={view === v.id ? "page" : undefined}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                  view === v.id
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                {v.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">
        {view === "map" && (
          <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
            <LiveIssueMap />
            <GamificationCard />
          </div>
        )}
        {view === "report" && (
          <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
            <SnapTagForm />
            <GamificationCard />
          </div>
        )}
        {view === "funds" && <FundTrailTable />}
        {view === "rewards" && (
          <div className="grid gap-6 lg:grid-cols-2">
            <GamificationCard />
            <LiveIssueMap />
          </div>
        )}
      </main>
    </div>
  );
}
