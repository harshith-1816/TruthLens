'use client';

import React from 'react';
import { GitMerge, ArrowRight, ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

interface CrossModalGraphProps {
  findings: any[];
}

export default function CrossModalGraph({ findings }: CrossModalGraphProps) {
  if (!findings || findings.length === 0) {
    return (
      <div className="glass-card rounded-xl p-6 text-center text-slate-400 text-sm">
        No cross-modal findings established for this evidence set.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="glass-card rounded-xl p-4 border border-slate-800 text-xs text-slate-300 flex items-center gap-2">
        <GitMerge className="w-4 h-4 text-cyan-400 flex-shrink-0" />
        <span>
          <strong>Cross-Modal Correlation Engine:</strong> Synthesizes findings across image, video, audio, and text sources.
          Corroborating indicators across multiple modalities increase confidence, while contextual contradictions reveal fabricated media narratives.
        </span>
      </div>

      <div className="space-y-3">
        {findings.map((f: any) => {
          const isRisk = f.risk_impact === 'INCREASES_RISK';
          const isContradiction = f.status === 'CONTRADICTION';
          const borderClass = isContradiction
            ? 'border-amber-500/80 bg-amber-950/10'
            : isRisk
            ? 'border-rose-500/80 bg-rose-950/10'
            : 'border-emerald-500/80 bg-emerald-950/10';

          const statusBadge = isContradiction
            ? 'bg-amber-950 text-amber-300 border-amber-800'
            : isRisk
            ? 'bg-rose-950 text-rose-300 border-rose-800'
            : 'bg-emerald-950 text-emerald-300 border-emerald-800';

          return (
            <div key={f.finding_id} className={`glass-card rounded-xl p-5 border-l-4 ${borderClass} space-y-3 shadow-lg`}>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${statusBadge}`}>
                    {f.status}
                  </span>
                  <strong className="text-sm text-slate-100">{f.description}</strong>
                </div>
                <div className="text-xs font-mono">
                  <span className={isRisk ? 'text-rose-400 font-bold' : 'text-emerald-400 font-bold'}>
                    {f.risk_impact}
                  </span>
                  <span className="text-slate-400 ml-2">({Math.round(f.confidence * 100)}% Certainty)</span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">{f.details}</p>

              {/* Modalities & Evidence Trace References */}
              <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono text-slate-400">
                <div className="flex items-center gap-2">
                  <span className="text-slate-500">MODALITIES INVOLVED:</span>
                  <div className="flex gap-1">
                    {f.modalities_involved?.map((m: string) => (
                      <span key={m} className="px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700 uppercase">
                        {m}
                      </span>
                    ))}
                  </div>
                </div>

                {f.evidence_references && f.evidence_references.length > 0 && (
                  <div className="text-slate-400">
                    Linked to <span className="text-cyan-400">{f.evidence_references.length} evidence trace(s)</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
