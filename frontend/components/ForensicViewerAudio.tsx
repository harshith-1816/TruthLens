'use client';

import React from 'react';
import { Mic, Waves, AlertCircle, Volume2, UserCheck, ShieldAlert } from 'lucide-react';

interface ForensicViewerAudioProps {
  audioResult: any;
}

export default function ForensicViewerAudio({ audioResult }: ForensicViewerAudioProps) {
  if (!audioResult) {
    return <div className="text-sm text-slate-500 p-4">No audio evidence submitted for this case.</div>;
  }

  const metrics = audioResult.metrics || {};
  const spec = metrics.spectral_forensics || {};
  const pitch = metrics.pitch_stability || {};
  const cadence = metrics.cadence_and_breathing || {};
  const splice = metrics.audio_splicing || {};
  const speaker = metrics.speaker_verification || {};
  const viz = audioResult.visualizations || {};

  return (
    <div className="space-y-6">
      {/* Top Audio KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs font-mono">
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">AUDIO DURATION & SR</span>
          <div className="text-base font-bold text-slate-100 mt-0.5">{metrics.duration_seconds}s @ {metrics.sample_rate_hz} Hz</div>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">VOCODER CUTOFF</span>
          <div className={`text-base font-bold mt-0.5 ${
            spec.brickwall_filter_detected ? 'text-rose-400' : 'text-emerald-400'
          }`}>
            {spec.brickwall_filter_detected ? `Cutoff @ ${spec.rolloff_frequency_hz} Hz` : 'Natural High Frequency'}
          </div>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">PITCH JITTER (F0)</span>
          <div className={`text-base font-bold mt-0.5 ${
            pitch.pitch_jitter_hz < 0.6 ? 'text-rose-400' : 'text-emerald-400'
          }`}>
            {pitch.pitch_jitter_hz ? `${pitch.pitch_jitter_hz} Hz` : 'N/A'} (Norm &gt; 1.2 Hz)
          </div>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">DEAD DIGITAL SILENCE</span>
          <div className="text-base font-bold text-slate-100 mt-0.5">
            {((cadence.zero_amplitude_ratio || 0) * 100).toFixed(1)}% Zero Amps
          </div>
        </div>
      </div>

      {/* Spectrogram Viewer */}
      {viz.spectrogram && (
        <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <Waves className="w-4 h-4 text-emerald-400" />
              Acoustic Spectrogram & High-Frequency Energy Distribution
            </h3>
            <span className="text-xs font-mono text-slate-400">Low Frequencies (Bottom) to High Frequencies (Top)</span>
          </div>
          <div className="bg-slate-950 p-2 rounded-lg border border-slate-800 flex justify-center">
            <img
              src={viz.spectrogram}
              alt="Acoustic Spectrogram"
              className="max-h-48 w-full object-contain rounded"
            />
          </div>
        </div>
      )}

      {/* Audio Splicing & Speaker Identity */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Splicing & Noise Discontinuity */}
        <div className="glass-card rounded-xl p-4 border border-slate-800 space-y-2">
          <div className="flex items-center gap-2 text-sm font-bold text-slate-100 border-b border-slate-800 pb-2">
            <AlertCircle className="w-4 h-4 text-amber-400" />
            Acoustic Splicing & Ambient Discontinuity
          </div>
          <p className="text-xs text-slate-300">
            Ambient Noise Floor Shift Ratio: <strong className="font-mono text-cyan-300">{splice.max_ambient_noise_shift_ratio || '1.0'}x</strong>
          </p>
          <div className="text-[11px] font-mono text-slate-400">
            Mean Room Acoustic Floor: <code>{splice.mean_ambient_noise_floor || 'N/A'}</code>
          </div>
        </div>

        {/* Voice Identity Verification */}
        <div className="glass-card rounded-xl p-4 border border-slate-800 space-y-2">
          <div className="flex items-center gap-2 text-sm font-bold text-slate-100 border-b border-slate-800 pb-2">
            <UserCheck className="w-4 h-4 text-cyan-400" />
            Speaker Voiceprint Verification
          </div>
          <div className="text-xs text-slate-300">
            {speaker.reference_provided ? (
              <>Spectral Cosine Similarity: <strong className="font-mono text-cyan-300">{speaker.speaker_similarity}</strong></>
            ) : (
              <span className="text-slate-500 italic">No reference voice sample provided for 1-to-1 biometric matching.</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
