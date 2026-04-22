import React from 'react';

const StatCard = ({ label, value }) => (
  <div className="bg-[#1a1a1a] p-3 rounded border border-panel-border mb-3">
    <div className="text-xs text-text-muted mb-1">{label}</div>
    <div className="text-lg text-text-primary font-mono">{value}</div>
  </div>
);

export default function StatsPanel({ stats, onReset }) {
  return (
    <div className="w-[220px] min-w-[220px] bg-panel-bg border-l border-panel-border p-4 flex flex-col h-full overflow-y-auto">
      <div className="text-xs text-text-muted mb-4 uppercase tracking-widest">Global Stats</div>
      
      <div className="flex-grow">
        <StatCard label="Total Messages" value={stats?.total_turns ?? 0} />
        <StatCard label="Flagged" value={stats?.flagged ?? 0} />
        <StatCard label="Blocked" value={stats?.blocked ?? 0} />
        <StatCard label="Avg Risk Score" value={(stats?.avg_risk ?? 0).toFixed(2)} />
        <StatCard label="Avg Latency" value={`${(stats?.avg_latency_ms ?? 0).toFixed(0)} ms`} />
      </div>

      <button 
        onClick={onReset}
        className="mt-4 border border-block text-block bg-transparent hover:bg-block/10 py-2 rounded transition-colors text-sm font-bold tracking-wide w-full uppercase"
      >
        Reset Session
      </button>
    </div>
  );
}
