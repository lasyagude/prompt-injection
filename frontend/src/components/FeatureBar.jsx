import React from 'react';

export default function FeatureBar({ label, value, hint }) {
  let colorClass = "bg-allow";
  let textClass = "text-allow";
  if (value >= 0.40) {
    colorClass = "bg-warn";
    textClass = "text-warn";
  }
  if (value >= 0.70) {
    colorClass = "bg-block";
    textClass = "text-block";
  }

  return (
    <div className="rounded-lg border border-panel-border bg-panel-soft p-3">
      <div className="mb-2 flex items-start justify-between gap-3">
        <div>
          <div className="text-xs font-medium text-text-primary">{label}</div>
          {hint && <div className="mt-0.5 text-[11px] leading-4 text-text-faint">{hint}</div>}
        </div>
        <div className={`font-mono text-xs font-semibold ${textClass}`}>{value.toFixed(2)}</div>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-terminal-bg">
        <div
          className={`h-full rounded-full transition-all duration-500 ease-out ${colorClass}`}
          style={{ width: `${Math.min(value * 100, 100)}%` }}
        />
      </div>
    </div>
  );
}
