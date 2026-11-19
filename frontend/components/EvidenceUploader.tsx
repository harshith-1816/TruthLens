'use client';

import React, { useState } from 'react';
import { UploadCloud, Image as ImageIcon, Video, Mic, FileText, CheckCircle2, ShieldCheck, Sparkles } from 'lucide-react';

interface EvidenceUploaderProps {
  onAnalyze: (formData: FormData) => void;
  isLoading: boolean;
}

export default function EvidenceUploader({ onAnalyze, isLoading }: EvidenceUploaderProps) {
  const [caseTitle, setCaseTitle] = useState('Cyber-Forensics Authenticity Review');
  const [investigator, setInvestigator] = useState('Senior Digital Forensics Examiner');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [refAudioFile, setRefAudioFile] = useState<File | null>(null);
  const [textContent, setTextContent] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const fd = new FormData();
    fd.append('case_title', caseTitle);
    fd.append('investigator', investigator);
    if (imageFile) fd.append('image', imageFile);
    if (videoFile) fd.append('video', videoFile);
    if (audioFile) fd.append('audio', audioFile);
    if (refAudioFile) fd.append('reference_audio', refAudioFile);
    if (textContent.trim()) fd.append('text_content', textContent.trim());

    onAnalyze(fd);
  };

  return (
    <div className="glass-card rounded-xl p-6 border border-slate-800 shadow-2xl">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-6">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <UploadCloud className="w-5 h-5 text-cyan-400" />
            Multimodal Evidence Ingestion & Cryptographic Registration
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Original files are stored in MinIO/S3 and indexed with SHA-256 hashes and MIME types.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono text-cyan-400 bg-cyan-950/60 px-3 py-1.5 rounded border border-cyan-800/80">
          <ShieldCheck className="w-4 h-4" />
          <span>CHAIN-OF-CUSTODY ENABLED</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Case Title</label>
            <input
              type="text"
              value={caseTitle}
              onChange={(e) => setCaseTitle(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
              required
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Examiner Identity</label>
            <input
              type="text"
              value={investigator}
              onChange={(e) => setInvestigator(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
              required
            />
          </div>
        </div>

        {/* 4 Modality Upload Zones */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Image */}
          <div className="border border-dashed border-slate-700 rounded-xl p-4 bg-slate-900/60 hover:border-cyan-500/60 transition group flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
                  <ImageIcon className="w-4 h-4 text-cyan-400" /> Image File
                </span>
                <span className="text-[10px] font-mono text-slate-500">JPG, PNG, TIFF</span>
              </div>
              <p className="text-[11px] text-slate-400 mb-3">Inspects EXIF, ELA, 2D FFT, and sensor noise patches.</p>
            </div>
            <div>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setImageFile(e.target.files?.[0] || null)}
                className="text-xs text-slate-400 file:mr-2 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-xs file:bg-slate-800 file:text-cyan-300 hover:file:bg-slate-700 w-full cursor-pointer"
              />
              {imageFile && (
                <div className="mt-2 text-[10px] font-mono text-cyan-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" /> {imageFile.name} ({(imageFile.size / 1024).toFixed(1)} KB)
                </div>
              )}
            </div>
          </div>

          {/* Video */}
          <div className="border border-dashed border-slate-700 rounded-xl p-4 bg-slate-900/60 hover:border-blue-500/60 transition group flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
                  <Video className="w-4 h-4 text-blue-400" /> Video File
                </span>
                <span className="text-[10px] font-mono text-slate-500">MP4, MOV, GIF</span>
              </div>
              <p className="text-[11px] text-slate-400 mb-3">Analyzes temporal consistency, blinking, and landmark jitter.</p>
            </div>
            <div>
              <input
                type="file"
                accept="video/*,image/gif"
                onChange={(e) => setVideoFile(e.target.files?.[0] || null)}
                className="text-xs text-slate-400 file:mr-2 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-xs file:bg-slate-800 file:text-blue-300 hover:file:bg-slate-700 w-full cursor-pointer"
              />
              {videoFile && (
                <div className="mt-2 text-[10px] font-mono text-blue-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" /> {videoFile.name} ({(videoFile.size / 1024).toFixed(1)} KB)
                </div>
              )}
            </div>
          </div>

          {/* Audio */}
          <div className="border border-dashed border-slate-700 rounded-xl p-4 bg-slate-900/60 hover:border-emerald-500/60 transition group flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
                  <Mic className="w-4 h-4 text-emerald-400" /> Audio File
                </span>
                <span className="text-[10px] font-mono text-slate-500">WAV, MP3, OGG</span>
              </div>
              <p className="text-[11px] text-slate-400 mb-3">Inspects vocoder cutoffs, pitch jitter, and silence gaps.</p>
            </div>
            <div>
              <input
                type="file"
                accept="audio/*"
                onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
                className="text-xs text-slate-400 file:mr-2 file:py-1 file:px-2.5 file:rounded-md file:border-0 file:text-xs file:bg-slate-800 file:text-emerald-300 hover:file:bg-slate-700 w-full cursor-pointer"
              />
              {audioFile && (
                <div className="mt-2 text-[10px] font-mono text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" /> {audioFile.name} ({(audioFile.size / 1024).toFixed(1)} KB)
                </div>
              )}
            </div>
          </div>

          {/* Text Context */}
          <div className="border border-dashed border-slate-700 rounded-xl p-4 bg-slate-900/60 hover:border-amber-500/60 transition group flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-amber-400" /> Accompanying Text
                </span>
                <span className="text-[10px] font-mono text-slate-500">Claims / Caption</span>
              </div>
              <textarea
                rows={3}
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                placeholder="Paste caption, claimed location, or spoken transcript..."
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500 resize-none"
              />
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={isLoading || (!imageFile && !videoFile && !audioFile && !textContent.trim())}
            className="px-6 py-2.5 bg-gradient-to-r from-cyan-600 via-sky-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg font-semibold text-sm shadow-lg shadow-cyan-600/30 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Executing Forensic Pipeline...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Launch Multimodal Forensic Analysis
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
