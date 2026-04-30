import React from 'react';
import { Gauge, MessageSquare, RefreshCcw, ShieldAlert, ShieldX, Timer } from 'lucide-react';

const StatCard = ({ label, value, icon: IconComponent, tone = "text-text-primary" }) => (
  <div className="rounded-lg border border-panel-border bg-panel-soft p-3">
    <div className="mb-2 flex items-center justify-between gap-2 text-xs text-text-muted">
      <span>{label}</span>
      {React.createElement(IconComponent, { size: 15, className: tone })}
    </div>
    <div className={`font-mono text-xl font-semibold ${tone}`}>{value}</div>
  </div>
);

export default function StatsPanel({ stats, onReset }) {
  return (
    <aside className="hidden min-h-0 overflow-y-auto border-l border-panel-border bg-panel-bg/90 p-5 xl:flex xl:flex-col">
      <div className="mb-4">
        <div className="text-xs uppercase tracking-[0.2em] text-text-muted">Session Stats</div>
        <div className="mt-1 text-sm font-semibold text-text-primary">Runtime summary</div>
      </div>

      <div className="grid flex-grow content-start gap-3">
        <StatCard label="Messages" value={stats?.total_turns ?? 0} icon={MessageSquare} />
        <StatCard label="Flagged" value={stats?.flagged ?? 0} icon={ShieldAlert} tone="text-warn" />
        <StatCard label="Blocked" value={stats?.blocked ?? 0} icon={ShieldX} tone="text-block" />
        <StatCard label="Avg Risk" value={(stats?.avg_risk ?? 0).toFixed(2)} icon={Gauge} tone="text-accent" />
        <StatCard label="Avg Latency" value={`${(stats?.avg_latency_ms ?? 0).toFixed(0)} ms`} icon={Timer} />
      </div>

      <button
        onClick={onReset}
        className="mt-5 flex w-full items-center justify-center gap-2 rounded-lg border border-panel-border bg-panel-soft py-2.5 text-sm font-semibold text-text-muted transition hover:border-block/50 hover:bg-block/10 hover:text-block"
      >
        <RefreshCcw size={15} />
        Reset Session
      </button>
    </aside>
  );
}
