'use client';

import React from 'react';
import { Video, Film, Eye, Activity, ShieldAlert, Cpu } from 'lucide-react';

interface ForensicViewerVideoProps {
  videoResult: any;
}

export default function ForensicViewerVideo({ videoResult }: ForensicViewerVideoProps) {
  if (!videoResult) {
    return <div className="text-sm text-slate-500 p-4">No video evidence submitted for this case.</div>;
  }

  const metrics = videoResult.metrics || {};
  const temp = metrics.temporal_consistency || {};
  const landmarks = metrics.facial_landmarks || {};
  const bio = metrics.biological_signals || {};
  const flow = metrics.optical_flow || {};
  const container = metrics.container_forensics || {};
  const viz = videoResult.visualizations || {};

  return (
    <div className="space-y-6">
      {/* Top Video KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs font-mono">
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">FRAMES ANALYZED</span>
          <div className="text-base font-bold text-slate-100 mt-0.5">{metrics.frames_analyzed} Frames (~{metrics.estimated_duration_sec}s)</div>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">TEMPORAL FLICKER SPIKES</span>
          <div className={`text-base font-bold mt-0.5 ${
            temp.temporal_spike_frames_count > 0 ? 'text-rose-400' : 'text-emerald-400'
          }`}>
            {temp.temporal_spike_frames_count || 0} Anomalous Jumps
          </div>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">JAWLINE JITTER RATIO</span>
          <div className="text-base font-bold text-slate-100 mt-0.5">
            {landmarks.jawline_instability_ratio || '1.0'}x (Norm &lt; 2.5)
          </div>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">OPTICAL FLOW RATIO</span>
          <div className="text-base font-bold text-slate-100 mt-0.5">
            {flow.optical_flow_discrepancy_ratio || '1.0'}x
          </div>
        </div>
      </div>

      {/* Temporal Timeline Scrubber Plot */}
      {viz.temporal_variance_timeline && (
        <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              Inter-Frame Temporal Variance Timeline (MSE Scrubbing)
            </h3>
            <span className="text-xs font-mono text-slate-400">Red markers indicate anomalous frame flicker</span>
          </div>
          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 flex justify-center">
            <img
              src={viz.temporal_variance_timeline}
              alt="Temporal Variance Plot"
              className="max-h-40 w-full object-contain"
            />
          </div>
        </div>
      )}

      {/* Biological & Optical Flow Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Biological Signal Card */}
        <div className="glass-card rounded-xl p-4 border border-slate-800 space-y-2">
          <div className="flex items-center gap-2 text-sm font-bold text-slate-100 border-b border-slate-800 pb-2">
            <Eye className="w-4 h-4 text-cyan-400" />
            Biological-Signal Consistency (Blink & Gaze)
          </div>
          <p className="text-xs text-slate-300">
            Detected Spontaneous Eyelid Blinks: <strong className="font-mono text-cyan-300">{bio.detected_blink_events ?? 0}</strong>
          </p>
          <div className="text-[11px] font-mono text-slate-400">
            Eye Region Luminance Variance: <code>{bio.eye_region_variance || 'N/A'}</code>
          </div>
        </div>

        {/* Container Atoms & Tool Signatures */}
        <div className="glass-card rounded-xl p-4 border border-slate-800 space-y-2">
          <div className="flex items-center gap-2 text-sm font-bold text-slate-100 border-b border-slate-800 pb-2">
            <Cpu className="w-4 h-4 text-blue-400" />
            Container Structure & Tool Signatures
          </div>
          <div className="text-xs text-slate-300">
            Detected Tools: <span className="font-mono text-rose-300">{container.detected_software_signatures?.join(', ') || 'Standard Camera Encoding'}</span>
          </div>
          <div className="text-[11px] font-mono text-slate-400">
            MP4 Atoms: <code>{container.top_level_atoms?.join(' • ') || 'ftyp, moov, mdat'}</code>
          </div>
        </div>
      </div>
    </div>
  );
}
