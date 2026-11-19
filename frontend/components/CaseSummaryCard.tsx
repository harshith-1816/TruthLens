'use client';

import React from 'react';
import { ShieldAlert, ShieldCheck, HelpCircle, Activity, Download, FileText, Code } from 'lucide-react';

interface CaseSummaryCardProps {
  report: any;
}

export default function CaseSummaryCard({ report }: CaseSummaryCardProps) {
  const assessment = report.assessment;
  const verdict = assessment.overall_verdict;
  const score = assessment.overall_manipulation_score;
  const confidence = assessment.calibrated_confidence;

  const isManipulation = verdict.includes('MANIPULATION');
  const isSuspicious = verdict.includes('SUSPICIOUS');

  const borderClass = isManipulation
    ? 'border-rose-500/80 shadow-rose-950/20'
    : isSuspicious
    ? 'border-amber-500/80 shadow-amber-950/20'
    : 'border-emerald-500/80 shadow-emerald-950/20';

  const textClass = isManipulation
    ? 'text-rose-400'
    : isSuspicious
    ? 'text-amber-400'
    : 'text-emerald-400';

  return (
    <div className={`glass-card rounded-xl p-6 border-l-4 ${borderClass} shadow-2xl space-y-6`}>
      {/* Header Info Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="text-xs font-mono text-cyan-400">
            CASE: <span className="text-slate-200">{report.case_id}</span> | REPORT: <span className="text-slate-200">{report.report_id}</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-0.5">{report.case_title}</h2>
          <div className="text-xs text-slate-400 mt-1">
            Examiner: <span className="text-slate-200">{report.investigator}</span> • Generated: {new Date(report.created_at).toLocaleString()}
          </div>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center gap-2">
          <a
            href={`/api/reports/${report.report_id}/html`}
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-mono flex items-center gap-1.5 border border-slate-700 transition"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" /> Standalone Dossier
          </a>
          <a
            href={`/api/reports/${report.report_id}/markdown`}
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-mono flex items-center gap-1.5 border border-slate-700 transition"
          >
            <FileText className="w-3.5 h-3.5 text-amber-400" /> Markdown
          </a>
          <a
            href={`/api/reports/${report.report_id}`}
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-mono flex items-center gap-1.5 border border-slate-700 transition"
          >
            <Code className="w-3.5 h-3.5 text-emerald-400" /> JSON
          </a>
        </div>
      </div>

      {/* Triad Metrics Banner */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
        {/* Calibrated Verdict */}
        <div className="space-y-1">
          <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Calibrated Verdict</span>
          <div className={`text-2xl font-black tracking-tight ${textClass} flex items-center gap-2`}>
            {isManipulation ? (
              <ShieldAlert className="w-7 h-7 flex-shrink-0" />
            ) : isSuspicious ? (
              <HelpCircle className="w-7 h-7 flex-shrink-0" />
            ) : (
              <ShieldCheck className="w-7 h-7 flex-shrink-0" />
            )}
            <span>{verdict}</span>
          </div>
          <p className="text-xs text-slate-300 mt-2 leading-relaxed">
            {assessment.evidential_summary}
          </p>
        </div>

        {/* Center Gauges */}
        <div className="flex items-center justify-center gap-8 py-3 border-y lg:border-y-0 lg:border-x border-slate-800">
          <div className="text-center">
            <div className={`text-3xl font-extrabold font-mono ${textClass}`}>
              {score.toFixed(1)}
            </div>
            <div className="text-[11px] font-mono uppercase text-slate-400 mt-0.5">Composite Risk (0-100)</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-extrabold font-mono text-cyan-400">
              {confidence.toFixed(1)}%
            </div>
            <div className="text-[11px] font-mono uppercase text-slate-400 mt-0.5">Calibrated Certainty</div>
          </div>
        </div>

        {/* Modality Risk Breakdown */}
        <div className="space-y-2">
          <span className="text-xs font-mono uppercase text-slate-400 flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-cyan-400" /> Modality Risk Breakdown
          </span>
          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            {Object.entries(assessment.modality_breakdown).map(([mod, sc]: [string, any]) => (
              <div key={mod} className="bg-slate-900/80 p-2 rounded border border-slate-800">
                <div className="flex justify-between text-slate-400 mb-1 text-[11px]">
                  <span>{mod.toUpperCase()}</span>
                  <span className="font-bold text-slate-200">{sc}/100</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      sc >= 70 ? 'bg-rose-500' : sc >= 40 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${sc}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
