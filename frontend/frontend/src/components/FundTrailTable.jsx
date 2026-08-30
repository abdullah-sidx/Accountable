import { Fragment, useEffect, useMemo, useState } from "react";
import { fundsApi } from "../services/apiClient";

/**
 * FundTrailTable — visualises the monetary chain from government sanction
 * down to the work actually completed on the ground.
 */

const SAMPLE_TRAIL = [
  {
    id: "PRJ-2291",
    project: "Ward 12 road resurfacing",
    sanctioned: 4200000,
    released: 4200000,
    contracted: 3850000,
    spent: 3100000,
    workVerified: 62,
    contractor: "Sri Balaji Infra",
    warrantyStatus: "Valid until 2027-07-02",
    stages: [
      { label: "Sanctioned",       amount: 4200000, date: "2026-01-12", status: "done" },
      { label: "Released to ward", amount: 4200000, date: "2026-02-03", status: "done" },
      { label: "Contract awarded", amount: 3850000, date: "2026-02-27", status: "done" },
      { label: "Bills paid",       amount: 3100000, date: "2026-06-14", status: "partial" },
      { label: "Work verified",    amount: 2604000, date: "2026-07-02", status: "partial" },
    ],
  },
  {
    id: "PRJ-2318",
    project: "Storm drain desilting — Zone 4",
    sanctioned: 1850000,
    released: 1200000,
    contracted: 1150000,
    spent: 1150000,
    workVerified: 96,
    contractor: "Kaveri Works Pvt Ltd",
    warrantyStatus: "Valid until 2027-07-19",
    stages: [
      { label: "Sanctioned",       amount: 1850000, date: "2026-03-04", status: "done" },
      { label: "Released to ward", amount: 1200000, date: "2026-03-30", status: "partial" },
      { label: "Contract awarded", amount: 1150000, date: "2026-04-11", status: "done" },
      { label: "Bills paid",       amount: 1150000, date: "2026-06-28", status: "done" },
      { label: "Work verified",    amount: 1104000, date: "2026-07-19", status: "done" },
    ],
  },
  {
    id: "PRJ-2402",
    project: "LED street lighting retrofit",
    sanctioned: 9600000,
    released: 5000000,
    contracted: 4800000,
    spent: 2100000,
    workVerified: 23,
    contractor: "Nova Lumen Systems",
    warrantyStatus: "Pending — work not yet verified",
    stages: [
      { label: "Sanctioned",       amount: 9600000, date: "2026-04-22", status: "done" },
      { label: "Released to ward", amount: 5000000, date: "2026-05-15", status: "partial" },
      { label: "Contract awarded", amount: 4800000, date: "2026-05-29", status: "done" },
      { label: "Bills paid",       amount: 2100000, date: "2026-08-01", status: "partial" },
      { label: "Work verified",    amount:  483000, date: "—",          status: "pending" },
    ],
  },
];

const inr = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value ?? 0);

function LeakBar({ sanctioned, spent, workVerified }) {
  const spentPct = sanctioned ? Math.min(100, (spent / sanctioned) * 100) : 0;
  return (
    <div className="min-w-40">
      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
        <div className="h-full rounded-full bg-primary" style={{ width: `${spentPct}%` }} />
      </div>
      <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-success"
          style={{ width: `${Math.min(100, workVerified)}%` }}
        />
      </div>
      <p className="mt-1 text-[11px] text-muted-foreground">
        {Math.round(spentPct)}% money spent · {workVerified}% work verified
      </p>
    </div>
  );
}

export default function FundTrailTable() {
  const [rows, setRows] = useState(SAMPLE_TRAIL);
  const [source, setSource] = useState("sample");
  const [expanded, setExpanded] = useState(SAMPLE_TRAIL[0].id);

  useEffect(() => {
    let cancelled = false;
    fundsApi
      .trail()
      .then((data) => {
        const list = Array.isArray(data) ? data : data?.projects;
        if (!cancelled && Array.isArray(list) && list.length) {
          setRows(list);
          setSource("live");
          setExpanded(list[0]?.id);
        }
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  const totals = useMemo(
    () =>
      rows.reduce(
        (acc, r) => ({
          sanctioned: acc.sanctioned + (r.sanctioned ?? 0),
          spent: acc.spent + (r.spent ?? 0),
        }),
        { sanctioned: 0, spent: 0 },
      ),
    [rows],
  );

  const gap = totals.sanctioned - totals.spent;

  return (
    <section className="rounded-2xl border border-border bg-card p-5 shadow-soft">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold tracking-tight text-foreground">Fund trail</h2>
          <p className="text-sm text-muted-foreground">
            Sanction → release → contract → payment → verified work ·{" "}
            {source === "live" ? "live treasury feed" : "sample data"}
          </p>
        </div>
        <div className="rounded-xl bg-muted px-3 py-2 text-right">
          <p className="text-xs text-muted-foreground">Unaccounted so far</p>
          <p className="text-base font-semibold text-foreground">{inr(gap)}</p>
        </div>
      </header>

      <div className="mt-4 overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <caption className="sr-only">
            Monetary chain from government sanctions to verified work per project
          </caption>
          <thead>
            <tr className="text-left text-xs uppercase tracking-wide text-muted-foreground">
              <th scope="col" className="py-2 pr-4 font-medium">Project</th>
              <th scope="col" className="py-2 pr-4 font-medium">Sanctioned</th>
              <th scope="col" className="py-2 pr-4 font-medium">Released</th>
              <th scope="col" className="py-2 pr-4 font-medium">Paid out</th>
              <th scope="col" className="py-2 pr-4 font-medium">Money vs work</th>
              <th scope="col" className="py-2 font-medium" />
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const open = expanded === row.id;
              return (
                <Fragment key={row.id}>
                  <tr className="border-t border-border align-top">
                    <td className="py-3 pr-4">
                      <p className="font-medium text-foreground">{row.project}</p>
                      <p className="text-xs text-muted-foreground">
                        {row.id} · {row.contractor}
                      </p>
                    </td>
                    <td className="py-3 pr-4 tabular-nums text-foreground">{inr(row.sanctioned)}</td>
                    <td className="py-3 pr-4 tabular-nums text-foreground">{inr(row.released)}</td>
                    <td className="py-3 pr-4 tabular-nums text-foreground">{inr(row.spent)}</td>
                    <td className="py-3 pr-4">
                      <LeakBar
                        sanctioned={row.sanctioned}
                        spent={row.spent}
                        workVerified={row.workVerified ?? 0}
                      />
                    </td>
                    <td className="py-3 text-right">
                      <button
                        type="button"
                        onClick={() => setExpanded(open ? null : row.id)}
                        aria-expanded={open}
                        className="rounded-lg border border-border px-2.5 py-1 text-xs font-medium text-muted-foreground transition-colors hover:border-primary/50 hover:text-foreground"
                      >
                        {open ? "Hide chain" : "View chain"}
                      </button>
                    </td>
                  </tr>
                  {open && (
                    <tr className="bg-muted/60">
                      <td colSpan={6} className="px-3 py-4">

                        {/* ── Contractor & Warranty strip ───────────────── */}
                        <div className="mb-4 flex flex-wrap gap-3">
                          {/* Contractor */}
                          <div className="flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2 text-sm">
                            <span className="text-muted-foreground">Contractor:</span>
                            <span className="font-medium text-foreground">
                              {row.contractor ?? "—"}
                            </span>
                          </div>

                          {/* Warranty status */}
                          <div className="flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2 text-sm">
                            <span className="text-muted-foreground">Warranty Status:</span>
                            <span
                              className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                                (row.warrantyStatus ?? "").startsWith("Valid")
                                  ? "bg-success/15 text-success"
                                  : (row.warrantyStatus ?? "").startsWith("Pending")
                                    ? "bg-warning/20 text-warning-foreground"
                                    : "bg-destructive/15 text-destructive"
                              }`}
                            >
                              {row.warrantyStatus ?? "Unknown"}
                            </span>
                          </div>
                        </div>

                        {/* ── Stage steps ───────────────────────────────── */}
                        <ol className="grid gap-3 md:grid-cols-5">
                          {(row.stages ?? []).map((stage, i) => (
                            <li
                              key={stage.label}
                              className="rounded-xl border border-border bg-card p-3"
                            >
                              <p className="text-[11px] uppercase tracking-wide text-muted-foreground">
                                Step {i + 1}
                              </p>
                              <p className="mt-0.5 text-sm font-medium text-foreground">
                                {stage.label}
                              </p>
                              <p className="tabular-nums text-sm text-foreground">
                                {inr(stage.amount)}
                              </p>
                              <p className="text-xs text-muted-foreground">{stage.date}</p>
                              <span
                                className={`mt-2 inline-block rounded-full px-2 py-0.5 text-[11px] font-medium ${
                                  stage.status === "done"
                                    ? "bg-success/15 text-success"
                                    : stage.status === "partial"
                                      ? "bg-warning/20 text-warning-foreground"
                                      : "bg-destructive/15 text-destructive"
                                }`}
                              >
                                {stage.status}
                              </span>
                            </li>
                          ))}
                        </ol>
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
