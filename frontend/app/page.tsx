'use client';

import React, { useState, useEffect } from 'react';
import {
  Fingerprint,
  Layers,
  Activity,
  GitMerge,
  ShieldAlert,
  ShieldCheck,
  HelpCircle,
  FileText,
  Video,
  Mic,
  Image as ImageIcon,
  CheckCircle2,
  ChevronRight,
  ExternalLink,
  BookOpen
} from 'lucide-react';
import EvidenceUploader from '@/components/EvidenceUploader';
import CaseSummaryCard from '@/components/CaseSummaryCard';
import ForensicViewerImage from '@/components/ForensicViewerImage';
import ForensicViewerVideo from '@/components/ForensicViewerVideo';
import ForensicViewerAudio from '@/components/ForensicViewerAudio';
import ForensicViewerText from '@/components/ForensicViewerText';
import CrossModalGraph from '@/components/CrossModalGraph';
import ChainOfCustodyTable from '@/components/ChainOfCustodyTable';
import HumanChecklist from '@/components/HumanChecklist';
import { fetchSampleCases, analyzeSampleCase, submitEvidence, SampleCaseMeta } from '@/services/api';

export default function Home() {
  const [sampleCases, setSampleCases] = useState<Record<string, SampleCaseMeta>>({});
  const [activeReport, setActiveReport] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('');
  const [activeTab, setActiveTab] = useState<'indicators' | 'image' | 'video' | 'audio' | 'text' | 'crossmodal' | 'uncertainty' | 'custody'>('indicators');

  useEffect(() => {
    fetchSampleCases()
      .then(setSampleCases)
      .catch((err) => console.error('Failed to load sample cases', err));
  }, []);

  const handleRunSample = async (caseKey: string) => {
    setIsLoading(true);
    setLoadingText(`Ingesting test evidence and executing analysis on ${caseKey}...`);
    try {
      const report = await analyzeSampleCase(caseKey);
      setActiveReport(report);
      setActiveTab('indicators');
    } catch (err: any) {
      alert(`Execution Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCustomSubmit = async (formData: FormData) => {
    setIsLoading(true);
    setLoadingText('Ingesting multimodal evidence, computing SHA-256, and initiating forensic pipelines...');
    try {
      const report = await submitEvidence(formData);
      setActiveReport(report);
      setActiveTab('indicators');
    } catch (err: any) {
      alert(`Forensic Pipeline Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-cyber-950 text-slate-100">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-cyber-900/90 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/20">
              <Fingerprint className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-300 bg-clip-text text-transparent">
                TruthLens
              </span>
              <span className="text-[11px] ml-2 px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/80 font-mono">
                CYBER-FORENSICS v1.0
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 text-xs font-mono text-slate-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>POSTGRESQL & MINIO OBJECT STORE ONLINE</span>
            </div>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 flex items-center gap-1.5 transition"
            >
              <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
              REST API Docs
            </a>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Banner / 5-step Workflow */}
        <div className="glass-card rounded-2xl p-6 relative overflow-hidden border border-slate-800">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                Multimodal Digital Forensics & Deepfake Detection Engine
              </h1>
              <p className="text-sm text-slate-400 mt-1 max-w-2xl leading-relaxed">
                Inspects image, video, audio, and text evidence; flags synthesis & editing indicators; cross-correlates orthogonal signals; and produces an explainable, calibrated forensic report.
              </p>
            </div>

            {/* Workflow steps */}
            <div className="flex items-center space-x-1.5 text-xs font-mono bg-slate-900/90 p-2.5 rounded-xl border border-slate-800">
              <span className="px-2 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">1. INGEST</span>
              <span className="text-slate-600">→</span>
              <span className="px-2 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">2. ANALYZE</span>
              <span className="text-slate-600">→</span>
              <span className="px-2 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">3. CORRELATE</span>
              <span className="text-slate-600">→</span>
              <span className="px-2 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">4. CALIBRATE</span>
              <span className="text-slate-600">→</span>
              <span className="px-2 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">5. REPORT</span>
            </div>
          </div>
        </div>

        {/* Pre-Packaged Sample Verification Cases */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold tracking-wider uppercase text-cyan-400 font-mono flex items-center gap-2">
              <Layers className="w-4 h-4" /> Pre-Configured Forensic Verification Packages
            </h2>
            <span className="text-xs text-slate-400">Click to execute end-to-end multi-modal pipeline</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {Object.entries(sampleCases).map(([key, data]) => (
              <div
                key={key}
                onClick={() => handleRunSample(key)}
                className="glass-card p-4 rounded-xl cursor-pointer hover:border-cyan-500/80 transition group flex flex-col justify-between border border-slate-800 hover:shadow-cyan-950/20 hover:shadow-lg"
              >
                <div>
                  <div className="text-xs font-bold text-slate-100 group-hover:text-cyan-300 transition mb-1.5">
                    {data.title}
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-3 mb-3 leading-relaxed">
                    {data.description}
                  </p>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                  <div className="flex gap-1">
                    {data.has_image && <span className="px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 text-[10px] font-mono">IMG</span>}
                    {data.has_video && <span className="px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 text-[10px] font-mono">VID</span>}
                    {data.has_audio && <span className="px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10px] font-mono">AUD</span>}
                    {data.has_text && <span className="px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800 text-[10px] font-mono">TXT</span>}
                  </div>
                  <span className="text-xs font-mono text-cyan-400 group-hover:translate-x-1 transition flex items-center gap-1">
                    Run <ChevronRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Custom Ingestion Panel */}
        <EvidenceUploader onAnalyze={handleCustomSubmit} isLoading={isLoading} />

        {/* Loading Spinner */}
        {isLoading && (
          <div className="glass-card rounded-2xl p-8 text-center space-y-4 border border-slate-800">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-400"></div>
            <div className="font-mono text-sm text-cyan-300">{loadingText}</div>
            <div className="text-xs text-slate-500">
              Transforming signals across Fourier spectrum, temporal flicker frames, acoustic roll-off, and cross-modal correlations...
            </div>
          </div>
        )}

        {/* Active Report View */}
        {activeReport && !isLoading && (
          <div className="space-y-6">
            {/* Case Summary Card */}
            <CaseSummaryCard report={activeReport} />

            {/* Navigation Tabs */}
            <div className="border-b border-slate-800 flex space-x-6 text-sm font-medium overflow-x-auto">
              <button
                onClick={() => setActiveTab('indicators')}
                className={`py-3 px-1 flex items-center gap-2 border-b-2 transition whitespace-nowrap ${
                  activeTab === 'indicators'
                    ? 'border-cyan-400 text-cyan-400 font-bold'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <ShieldAlert className="w-4 h-4" />
                Flagged Indicators ({activeReport.all_indicators?.length || 0})
              </button>

              <button
                onClick={() => setActiveTab('crossmodal')}
                className={`py-3 px-1 flex items-center gap-2 border-b-2 transition whitespace-nowrap ${
                  activeTab === 'crossmodal'
                    ? 'border-cyan-400 text-cyan-400 font-bold'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <GitMerge className="w-4 h-4" />
                Cross-Modal Correlation ({activeReport.cross_modal_findings?.length || 0})
              </button>

              {activeReport.modality_results?.image && (
                <button
                  onClick={() => setActiveTab('image')}
                  className={`py-3 px-1 flex items-center gap-2 border-b-2 transition whitespace-nowrap ${
                    activeTab === 'image'
                      ? 'border-cyan-400 text-cyan-400 font-bold'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <ImageIcon className="w-4 h-4 text-cyan-400" />
                  Image Forensics
                </button>
              )}

              {activeReport.modality_results?.video && (
                <button
                  onClick={() => setActiveTab('video')}
                  className={`py-3 px-1 flex items-center gap-2 border-b-2 transition whitespace-nowrap ${
                    activeTab === 'video'
                      ? 'border-cyan-400 text-cyan-400 font-bold'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Video className="w-4 h-4 text-blue-400" />
                  Video Forensics
                </button>
              )}

              {activeReport.modality_results?.audio && (
                <button
                  onClick={() => setActiveTab('audio')}
                  className={`py-3 px-1 flex items-center gap-2 border-b-2 transition whitespace-nowrap ${
                    activeTab === 'audio'
                      ? 'border-cyan-400 text-cyan-400 font-bold'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Mic className="w-4 h-4 text-emerald-400" />
                  Audio Forensics
                </button>
              )}

              {activeReport.modality_results?.text && (
                <button
                  onClick={() => setActiveTab('text')}
                  className={`py-3 px-1 flex items-center gap-2 border-b-2 transition whitespace-nowrap ${
                    activeTab === 'text'
                      ? 'border-cyan-400 text-cyan-400 font-bold'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <FileText className="w-4 h-4 text-amber-400" />
                  Text Context
                </button>
              )}

              <button
                onClick={() => setActiveTab('uncertainty')}
                className={`py-3 px-1 flex items-center gap-2 border-b-2 transition whitespace-nowrap ${
                  activeTab === 'uncertainty'
                    ? 'border-cyan-400 text-cyan-400 font-bold'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <HelpCircle className="w-4 h-4" />
                Uncertainty & Checklist
              </button>

              <button
                onClick={() => setActiveTab('custody')}
                className={`py-3 px-1 flex items-center gap-2 border-b-2 transition whitespace-nowrap ${
                  activeTab === 'custody'
                    ? 'border-cyan-400 text-cyan-400 font-bold'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <ShieldCheck className="w-4 h-4" />
                Chain of Custody
              </button>
            </div>

            {/* Tab 1: Indicators */}
            {activeTab === 'indicators' && (
              <div className="space-y-3">
                {activeReport.all_indicators?.map((ind: any) => {
                  const sevColor = {
                    CRITICAL: 'bg-rose-950 text-rose-300 border-rose-800',
                    HIGH: 'bg-orange-950 text-orange-300 border-orange-800',
                    MEDIUM: 'bg-amber-950 text-amber-300 border-amber-800',
                    LOW: 'bg-blue-950 text-blue-300 border-blue-800',
                    INFO: 'bg-slate-800 text-slate-300 border-slate-700',
                  }[ind.severity] || 'bg-slate-800 text-slate-300';

                  return (
                    <div key={ind.indicator_id} className="glass-card p-4 rounded-xl border border-slate-800 space-y-2">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${sevColor}`}>
                            {ind.severity}
                          </span>
                          <span className="text-xs font-mono text-cyan-400">[{ind.modality.toUpperCase()}]</span>
                          <strong className="text-sm text-slate-100">{ind.title}</strong>
                        </div>
                        <div className="text-xs font-mono text-slate-400">
                          Suspicion: <strong className="text-slate-200">{Math.round(ind.suspicion_score * 100)}%</strong> | Conf: <strong className="text-slate-200">{Math.round(ind.confidence * 100)}%</strong>
                        </div>
                      </div>

                      <p className="text-xs text-slate-300">{ind.description}</p>

                      <div className="bg-slate-900/90 p-2.5 rounded-lg text-xs text-cyan-200/90 font-mono border border-slate-800/80">
                        <span className="text-slate-500 font-bold">TECH DETAIL:</span> {ind.technical_details}
                      </div>

                      {ind.evidence_ref && (
                        <div className="mt-2 pt-2 border-t border-slate-800/60 text-[11px] font-mono text-slate-400 flex flex-wrap gap-x-4">
                          <span>File: <code className="text-slate-200">{ind.evidence_ref.source_filename}</code></span>
                          <span>Target: <code className="text-slate-200">{ind.evidence_ref.location_type}</code></span>
                          <span>Value: <code className="text-slate-200">{JSON.stringify(ind.evidence_ref.location_value)}</code></span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Tab 2: Cross Modal */}
            {activeTab === 'crossmodal' && <CrossModalGraph findings={activeReport.cross_modal_findings} />}

            {/* Tab 3: Image Forensics */}
            {activeTab === 'image' && <ForensicViewerImage imageResult={activeReport.modality_results?.image} />}

            {/* Tab 4: Video Forensics */}
            {activeTab === 'video' && <ForensicViewerVideo videoResult={activeReport.modality_results?.video} />}

            {/* Tab 5: Audio Forensics */}
            {activeTab === 'audio' && <ForensicViewerAudio audioResult={activeReport.modality_results?.audio} />}

            {/* Tab 6: Text Forensics */}
            {activeTab === 'text' && <ForensicViewerText textResult={activeReport.modality_results?.text} />}

            {/* Tab 7: Uncertainty */}
            {activeTab === 'uncertainty' && <HumanChecklist assessment={activeReport.assessment} />}

            {/* Tab 8: Custody */}
            {activeTab === 'custody' && <ChainOfCustodyTable records={activeReport.chain_of_custody} />}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-6 bg-cyber-900 mt-16">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-500 font-mono">
          TruthLens Digital Forensics & Deepfake Detection Engine • Decision-Support Tool • Grounded Evidentiary Review
        </div>
      </footer>
    </div>
  );
}
