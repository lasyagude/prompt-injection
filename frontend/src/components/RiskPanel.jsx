import React from 'react';
import FeatureBar from './FeatureBar';
import { Activity, AlertTriangle, Ban, CheckCircle2, Radar } from 'lucide-react';

const decisionTheme = {
  ALLOW: {
    label: "Allow",
    color: "text-allow",
    border: "border-allow/35",
    bg: "bg-allow/10",
    ring: "stroke-allow",
    icon: CheckCircle2,
  },
  WARN: {
    label: "Warn",
    color: "text-warn",
    border: "border-warn/35",
    bg: "bg-warn/10",
    ring: "stroke-warn",
    icon: AlertTriangle,
  },
  BLOCK: {
    label: "Block",
    color: "text-block",
    border: "border-block/35",
    bg: "bg-block/10",
    ring: "stroke-block",
    icon: Ban,
  },
};

function RiskMeter({ score, theme }) {
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - Math.min(score, 1) * circumference;

  return (
    <div className="relative flex h-44 w-44 items-center justify-center">
      <svg viewBox="0 0 128 128" className="-rotate-90">
        <circle cx="64" cy="64" r={radius} fill="none" stroke="rgba(39,52,71,0.9)" strokeWidth="10" />
        <circle
          cx="64"
          cy="64"
          r={radius}
          fill="none"
          className={theme.ring}
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="absolute text-center">
        <div className={`font-mono text-4xl font-semibold tracking-wide ${theme.color}`}>{score.toFixed(2)}</div>
        <div className="mt-1 text-[11px] uppercase tracking-[0.22em] text-text-muted">Risk</div>
      </div>
    </div>
  );
}

export default function RiskPanel({ result }) {
  if (!result) {
    return (
      <aside className="hidden min-h-0 border-l border-panel-border bg-panel-bg/90 p-5 lg:flex lg:flex-col">
        <div className="flex h-full flex-col items-center justify-center rounded-xl border border-dashed border-panel-border bg-panel-soft/50 p-6 text-center">
          <Radar className="mb-3 text-accent" size={28} />
          <div className="text-sm font-medium text-text-primary">Risk telemetry waiting</div>
          <div className="mt-2 text-xs leading-5 text-text-muted">Send a prompt to inspect classifier and behavioral signals.</div>
        </div>
      </aside>
    );
  }

  const theme = decisionTheme[result.decision] || decisionTheme.ALLOW;
  const Icon = theme.icon;
  const features = result.features || {};

  return (
    <aside className="min-h-0 overflow-y-auto border-t border-panel-border bg-panel-bg/95 p-5 lg:border-l lg:border-t-0">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-text-muted">Risk Engine</div>
          <div className="mt-1 text-sm font-semibold text-text-primary">Current turn</div>
        </div>
        <div className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold uppercase tracking-wide ${theme.border} ${theme.bg} ${theme.color}`}>
          <Icon size={14} />
          {theme.label}
        </div>
      </div>

      <div className="mb-5 flex justify-center rounded-xl border border-panel-border bg-panel-soft p-5">
        <RiskMeter score={result.risk_score || 0} theme={theme} />
      </div>

      <div className="mb-5 rounded-xl border border-panel-border bg-panel-soft p-4">
        <div className="mb-2 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-medium text-text-muted">
            <Activity size={14} className="text-accent" />
            DeBERTa confidence
          </div>
          <div className={`font-mono text-sm font-semibold ${theme.color}`}>{((result.deberta_score || 0) * 100).toFixed(1)}%</div>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-terminal-bg">
          <div
            className={`h-full rounded-full transition-all duration-500 ${result.decision === "BLOCK" ? "bg-block" : result.decision === "WARN" ? "bg-warn" : "bg-allow"}`}
            style={{ width: `${Math.max(3, Math.min((result.deberta_score || 0) * 100, 100))}%` }}
          />
        </div>
      </div>

      <div>
        <div className="mb-3 text-xs uppercase tracking-[0.2em] text-text-muted">Behavioral Features</div>
        <div className="grid gap-2.5">
          <FeatureBar label="Attack Similarity" value={features.attack_pattern_similarity || 0} hint="Similarity to known injection patterns" />
          <FeatureBar label="Probing Similarity" value={features.probing_similarity || 0} hint="System prompt or rule extraction intent" />
          <FeatureBar label="Role Shift" value={features.role_shift_counter || 0} hint="Persona override or instruction reset signals" />
          <FeatureBar label="Topic Shift" value={features.conversation_trajectory || 0} hint="Sudden pivot from recent conversation" />
          <FeatureBar label="Escalation" value={features.escalation_rate || 0} hint="Rising risk across recent turns" />
          <FeatureBar label="Repetition" value={features.repetition_similarity || 0} hint="Reworded attempts after a risky turn" />
          <FeatureBar label="Flag Rate" value={features.flag_rate || 0} hint="Share of previous turns flagged" />
        </div>
      </div>
    </aside>
  );
}
