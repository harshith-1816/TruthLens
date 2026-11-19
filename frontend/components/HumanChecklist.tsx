'use client';

import React, { useState } from 'react';
import { HelpCircle, Scale, CheckSquare, Square } from 'lucide-react';

interface HumanChecklistProps {
  assessment: any;
}

export default function HumanChecklist({ assessment }: HumanChecklistProps) {
  if (!assessment) return null;

  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({});

  const toggleCheck = (idx: number) => {
    setCheckedItems(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="space-y-6">
      {/* 2-Column Uncertainty & Alternatives */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Uncertainty Factors */}
        <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-3">
          <h3 className="text-sm font-bold text-amber-400 font-mono flex items-center gap-2 border-b border-slate-800 pb-2">
            <HelpCircle className="w-4 h-4" />
            Known Uncertainty Factors & Sensor Caveats
          </h3>
          <ul className="space-y-2 text-xs text-slate-300 list-disc list-inside">
            {assessment.uncertainty_factors?.map((u: string, idx: number) => (
              <li key={idx} className="leading-relaxed">{u}</li>
            ))}
          </ul>
        </div>

        {/* Alternative Explanations */}
        <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-3">
          <h3 className="text-sm font-bold text-sky-400 font-mono flex items-center gap-2 border-b border-slate-800 pb-2">
            <Scale className="w-4 h-4" />
            Plausible Alternative (Benign) Explanations
          </h3>
          <ul className="space-y-2 text-xs text-slate-300 list-disc list-inside">
            {assessment.alternative_explanations?.map((a: string, idx: number) => (
              <li key={idx} className="leading-relaxed">{a}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* Human-in-the-Loop Checklist */}
      <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-3">
        <h3 className="text-sm font-bold text-emerald-400 font-mono flex items-center gap-2 border-b border-slate-800 pb-2">
          <CheckSquare className="w-4 h-4" />
          Recommended Human Forensic Examiner Verification Checklist
        </h3>
        <p className="text-xs text-slate-400">
          Automated algorithmic scores serve as decision-support aids. Qualified examiners should complete these verification checks prior to issuing a legal evidentiary finding.
        </p>

        <div className="space-y-2 pt-2">
          {assessment.recommended_human_checks?.map((chk: string, idx: number) => {
            const isChecked = !!checkedItems[idx];
            return (
              <div
                key={idx}
                onClick={() => toggleCheck(idx)}
                className={`flex items-start gap-3 p-2.5 rounded-lg border transition cursor-pointer text-xs ${
                  isChecked
                    ? 'bg-emerald-950/30 border-emerald-800/80 text-emerald-200'
                    : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:bg-slate-800/60'
                }`}
              >
                <button type="button" className="mt-0.5 text-cyan-400">
                  {isChecked ? <CheckSquare className="w-4 h-4 text-emerald-400" /> : <Square className="w-4 h-4 text-slate-500" />}
                </button>
                <span className={isChecked ? 'line-through text-slate-400' : ''}>{chk}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
