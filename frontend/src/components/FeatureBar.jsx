import React from 'react';

export default function FeatureBar({ label, value }) {
  let colorClass = "bg-allow";
  if (value >= 0.40) colorClass = "bg-warn";
  if (value >= 0.70) colorClass = "bg-block";

  return (
    <div className="mb-2">
      <div className="flex justify-between text-xs mb-1">
        <span>{label}</span>
        <span>{value.toFixed(2)}</span>
      </div>
      <div className="h-1 bg-[#1e1e1e] w-full mt-1">
        <div 
          className={`h-full transition-all duration-400 ease-out ${colorClass}`} 
          style={{ width: `${Math.min(value * 100, 100)}%` }}
        />
      </div>
    </div>
  );
}
