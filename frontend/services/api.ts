/**
 * TruthLens API Client Service
 * Connects Next.js Frontend with the FastAPI Multimodal Forensics Backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface SampleCaseMeta {
  title: string;
  description: string;
  has_image: boolean;
  has_video: boolean;
  has_audio: boolean;
  has_text: boolean;
}

export async function fetchSampleCases(): Promise<Record<string, SampleCaseMeta>> {
  const res = await fetch(`${API_BASE_URL}/api/sample-cases`);
  if (!res.ok) throw new Error('Failed to fetch sample cases');
  return res.json();
}

export async function analyzeSampleCase(caseKey: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/analyze-sample/${caseKey}`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Failed to analyze sample: ${caseKey}`);
  return res.json();
}

export async function submitEvidence(formData: FormData): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(errorData.detail || 'Failed to submit evidence');
  }
  return res.json();
}

export async function fetchHistoricalCases(): Promise<any[]> {
  const res = await fetch(`${API_BASE_URL}/api/cases`);
  if (!res.ok) return [];
  return res.json();
}
