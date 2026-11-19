import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'TruthLens – Multimodal Digital Forensics & Deepfake Detection',
  description: 'Explainable digital forensics platform analyzing image, video, audio, and text authenticity with cross-modal correlation.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-cyber-950 text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-black">
        {children}
      </body>
    </html>
  );
}
