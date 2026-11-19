'use client';

import React, { useState } from 'react';
import { Image as ImageIcon, Cpu, Sparkles, MapPin, AlertTriangle, Layers } from 'lucide-react';

interface ForensicViewerImageProps {
  imageResult: any;
}

export default function ForensicViewerImage({ imageResult }: ForensicViewerImageProps) {
  if (!imageResult) {
    return <div className="text-sm text-slate-500 p-4">No image evidence submitted for this case.</div>;
  }

  const [activeLayer, setActiveLayer] = useState<'ela' | 'fft' | 'noise' | 'attribution'>('ela');
  const metrics = imageResult.metrics || {};
  const meta = metrics.metadata || {};
  const viz = imageResult.visualizations || {};

  return (
    <div className="space-y-6">
      {/* Top Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 text-xs font-mono">
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">DIMENSIONS</span>
          <div className="text-base font-bold text-slate-100 mt-0.5">{metrics.dimensions} ({metrics.megapixels} MP)</div>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">FORMAT / MODE</span>
          <div className="text-base font-bold text-slate-100 mt-0.5">{metrics.format} ({metrics.mode})</div>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">CAMERA PROVENANCE</span>
          <div className="text-base font-bold text-slate-100 mt-0.5 truncate">
            {meta.camera_make_model || 'Unknown / Stripped'}
          </div>
        </div>
        <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
          <span className="text-slate-400">IMAGE RISK VERDICT</span>
          <div className={`text-base font-bold mt-0.5 ${
            imageResult.manipulation_probability >= 0.7 ? 'text-rose-400' : 'text-emerald-400'
          }`}>
            {(imageResult.manipulation_probability * 100).toFixed(0)}% Risk
          </div>
        </div>
      </div>

      {/* Visual Forensics Inspection Station */}
      <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-100">Multi-Layer Forensic Spectrum Analysis</h3>
          </div>
          {/* Layer Switcher Buttons */}
          <div className="flex items-center gap-1.5 text-xs font-mono">
            {viz.ela_map && (
              <button
                onClick={() => setActiveLayer('ela')}
                className={`px-2.5 py-1 rounded transition ${
                  activeLayer === 'ela' ? 'bg-cyan-500 text-black font-bold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                Error Level Analysis (ELA)
              </button>
            )}
            {viz.fft_spectrum && (
              <button
                onClick={() => setActiveLayer('fft')}
                className={`px-2.5 py-1 rounded transition ${
                  activeLayer === 'fft' ? 'bg-cyan-500 text-black font-bold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                2D FFT Spectrum
              </button>
            )}
            {viz.noise_heatmap && (
              <button
                onClick={() => setActiveLayer('noise')}
                className={`px-2.5 py-1 rounded transition ${
                  activeLayer === 'noise' ? 'bg-cyan-500 text-black font-bold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                Sensor Noise Heatmap
              </button>
            )}
            {viz.attribution_heatmap && (
              <button
                onClick={() => setActiveLayer('attribution')}
                className={`px-2.5 py-1 rounded transition ${
                  activeLayer === 'attribution' ? 'bg-cyan-500 text-black font-bold' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                AI Attribution Mask
              </button>
            )}
          </div>
        </div>

        {/* Display Active Map */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
          <div className="relative bg-black rounded-lg border border-slate-800 p-2 flex items-center justify-center min-h-[260px]">
            {activeLayer === 'ela' && viz.ela_map && (
              <img src={viz.ela_map} alt="Error Level Analysis" className="max-h-72 w-auto object-contain rounded" />
            )}
            {activeLayer === 'fft' && viz.fft_spectrum && (
              <img src={viz.fft_spectrum} alt="2D FFT Spectrum" className="max-h-72 w-auto object-contain rounded" />
            )}
            {activeLayer === 'noise' && viz.noise_heatmap && (
              <img src={viz.noise_heatmap} alt="Noise Variance Heatmap" className="max-h-72 w-auto object-contain rounded" />
            )}
            {activeLayer === 'attribution' && viz.attribution_heatmap && (
              <img src={viz.attribution_heatmap} alt="AI Attribution Heatmap" className="max-h-72 w-auto object-contain rounded" />
            )}
          </div>

          <div className="space-y-3 text-xs text-slate-300">
            <div className="bg-slate-900/90 p-3 rounded-lg border border-slate-800 space-y-1 font-mono">
              <span className="text-cyan-400 font-bold">ANALYZER EXPLANATION:</span>
              {activeLayer === 'ela' && (
                <p>
                  Error Level Analysis highlights compression discrepancy ratios. Spliced or digitally modified patches exhibit bright error hotspots against the uniform resaved background.
                </p>
              )}
              {activeLayer === 'fft' && (
                <p>
                  2D Fast Fourier Transform shifts the image to frequency domain. Generative models (GANs, Latent Diffusion) leave periodic high-frequency grid deconvolution peaks.
                </p>
              )}
              {activeLayer === 'noise' && (
                <p>
                  Sensor Noise Variance computes local Laplacian noise standard score (Z-score). Disparate sensor noise patterns indicate composite elements pasted from external sources.
                </p>
              )}
              {activeLayer === 'attribution' && (
                <p>
                  Multivariate synthetic feature attribution maps the spatial areas contributing most heavily to the artificial generation probability score.
                </p>
              )}
            </div>

            {/* Metrics Breakdown */}
            <div className="grid grid-cols-2 gap-2 font-mono text-[11px]">
              <div className="bg-slate-900/50 p-2 rounded border border-slate-800">
                <span className="text-slate-500">ELA MEAN DIFF:</span>
                <span className="text-slate-200 font-bold ml-1">{metrics.ela_mean_difference}</span>
              </div>
              <div className="bg-slate-900/50 p-2 rounded border border-slate-800">
                <span className="text-slate-500">PEAK SPECTRAL RATIO:</span>
                <span className="text-slate-200 font-bold ml-1">
                  {metrics.frequency_analysis?.high_freq_peak_to_mean_ratio || 'N/A'}
                </span>
              </div>
              <div className="bg-slate-900/50 p-2 rounded border border-slate-800">
                <span className="text-slate-500">PEAK NOISE Z-SCORE:</span>
                <span className="text-slate-200 font-bold ml-1">
                  {metrics.noise_consistency?.max_z_score || 'N/A'}
                </span>
              </div>
              <div className="bg-slate-900/50 p-2 rounded border border-slate-800">
                <span className="text-slate-500">EXIF SOFTWARE:</span>
                <span className="text-slate-200 font-bold ml-1 truncate">
                  {meta.software || 'None'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
