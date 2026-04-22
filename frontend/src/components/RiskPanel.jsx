import React from 'react';
import FeatureBar from './FeatureBar';

export default function RiskPanel({ result }) {
  if (!result) {
    return (
      <div className="w-[280px] min-w-[280px] bg-panel-bg border-l border-panel-border p-4 flex items-center justify-center text-text-muted">
        Send a message to begin.
      </div>
    );
  }

  let colorClass = "text-allow";
  let barColorClass = "bg-allow";
  let shadowClass = "drop-shadow-[0_0_8px_rgba(0,255,136,0.8)]";

  if (result.decision === "WARN") {
    colorClass = "text-warn";
    barColorClass = "bg-warn";
    shadowClass = "drop-shadow-[0_0_8px_rgba(255,170,0,0.8)]";
  } else if (result.decision === "BLOCK") {
    colorClass = "text-block";
    barColorClass = "bg-block";
    shadowClass = "drop-shadow-[0_0_8px_rgba(255,51,51,0.8)]";
  }

  return (
    <div className="w-[280px] min-w-[280px] bg-panel-bg border-l border-panel-border p-4 flex flex-col overflow-y-auto">
      
      <div className="mb-6 flex flex-col items-center">
        <div className="text-xs text-text-muted mb-1 uppercase tracking-widest">Risk Score</div>
        <div className={`text-4xl font-bold ${colorClass} ${shadowClass}`}>
          {result.risk_score.toFixed(2)}
        </div>
        <div className="w-full h-1 bg-[#1e1e1e] mt-3">
          <div 
            className={`h-full transition-duration-[400ms] ease-out ${barColorClass}`} 
            style={{ width: `${Math.min(result.risk_score * 100, 100)}%` }}
          />
        </div>
      </div>

      <div className="mb-6 flex flex-col items-center">
        <div className={`text-2xl font-bold uppercase tracking-widest ${colorClass} ${shadowClass}`}>
          {result.decision}
        </div>
      </div>

      <div className="mb-8">
        <div className="flex justify-between items-end mb-2">
          <div className="text-xs text-text-muted uppercase tracking-wide">DeBERTa Score</div>
          <div className={`${colorClass} font-bold text-lg`}>{(result.deberta_score * 100).toFixed(1)}%</div>
        </div>
        <div className="w-full h-3 bg-[#1e1e1e] rounded-full overflow-hidden">
          <div 
            className={`h-full transition-duration-[400ms] ease-out ${barColorClass} ${result.deberta_score > 0.5 ? 'animate-pulse' : ''}`} 
            style={{ width: `${Math.max(2, Math.min(result.deberta_score * 100, 100))}%` }}
          />
        </div>
      </div>

      <div>
        <div className="text-xs text-text-muted mb-3 uppercase tracking-wide">Behavioral Features</div>
        <FeatureBar label="Attack Similarity" value={result.features.attack_pattern_similarity || 0} />
        <FeatureBar label="Probing Similarity" value={result.features.probing_similarity || 0} />
        <FeatureBar label="Role Shift" value={result.features.role_shift_counter || 0} />
        <FeatureBar label="Topic Shift" value={result.features.conversation_trajectory || 0} />
        <FeatureBar label="Repetition" value={result.features.repetition_similarity || 0} />
        <FeatureBar label="Flag Rate" value={result.features.flag_rate || 0} />
      </div>

    </div>
  );
}
