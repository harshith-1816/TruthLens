'use client';

import React from 'react';
import { FileText, Bot, AlertTriangle, MapPin, Calendar, Hash } from 'lucide-react';

interface ForensicViewerTextProps {
  textResult: any;
}

export default function ForensicViewerText({ textResult }: ForensicViewerTextProps) {
  if (!textResult) {
    return <div className="text-sm text-slate-500 p-4">No text or context notes submitted for this case.</div>;
  }

  const metrics = textResult.metrics || {};
  const stylometry = metrics.stylometry || {};
  const llm = metrics.llm_lexicon || {};
  const disinfo = metrics.disinfo_framing || {};
  const claims = metrics.extracted_claims || {};

  return (
    <div className="space-y-6">
      {/* Top Text KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs font-mono">
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">WORD & SENTENCE COUNT</span>
          <div className="text-base font-bold text-slate-100 mt-0.5">{metrics.word_count} Words ({metrics.sentence_count} Sentences)</div>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">BURSTINESS CV (VARIANCE)</span>
          <div className={`text-base font-bold mt-0.5 ${
            stylometry.burstiness_cv < 0.25 ? 'text-amber-400' : 'text-emerald-400'
          }`}>
            {stylometry.burstiness_cv || 'N/A'} (Human &gt; 0.40)
          </div>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">LLM BOILERPLATE PHRASES</span>
          <div className={`text-base font-bold mt-0.5 ${
            llm.llm_hedge_occurrences > 2 ? 'text-rose-400' : 'text-slate-200'
          }`}>
            {llm.llm_hedge_occurrences || 0} Matches
          </div>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">DISINFO VIRAL HOOKS</span>
          <div className={`text-base font-bold mt-0.5 ${
            disinfo.contains_viral_hooks ? 'text-rose-400' : 'text-emerald-400'
          }`}>
            {disinfo.urgency_triggers_count || 0} Triggers
          </div>
        </div>
      </div>

      {/* Extracted Claims and Linguistic Markers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Extracted Factual Claims */}
        <div className="glass-card rounded-xl p-4 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-slate-100 border-b border-slate-800 pb-2">
            <MapPin className="w-4 h-4 text-cyan-400" />
            Extracted Entities & Geographic/Temporal Claims
          </div>
          <div className="space-y-2 text-xs">
            <div>
              <span className="font-mono text-slate-400">Mentioned Entities: </span>
              <span className="text-slate-200">{claims.key_entities?.join(', ') || 'None detected'}</span>
            </div>
            <div>
              <span className="font-mono text-slate-400">Mentioned Dates: </span>
              <span className="text-slate-200">{claims.mentioned_dates?.join(', ') || 'None detected'}</span>
            </div>
            <div>
              <span className="font-mono text-slate-400">Mentioned Years: </span>
              <span className="text-slate-200">{claims.mentioned_years?.join(', ') || 'None detected'}</span>
            </div>
          </div>
        </div>

        {/* LLM Clichés & Phrases */}
        <div className="glass-card rounded-xl p-4 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-slate-100 border-b border-slate-800 pb-2">
            <Bot className="w-4 h-4 text-purple-400" />
            LLM Idiom Signatures & Clichés
          </div>
          <div className="flex flex-wrap gap-1.5">
            {llm.unique_llm_phrases && llm.unique_llm_phrases.length > 0 ? (
              llm.unique_llm_phrases.map((phrase: string, idx: number) => (
                <span key={idx} className="px-2 py-0.5 rounded bg-purple-950/80 text-purple-300 border border-purple-800 text-[11px] font-mono">
                  "{phrase}"
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-500 italic">No stereotypical LLM idiom clusters detected.</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
