'use client';

import React, { useState } from 'react';
import { ShieldCheck, Copy, Check } from 'lucide-react';

interface ChainOfCustodyTableProps {
  records: any[];
}

export default function ChainOfCustodyTable({ records }: ChainOfCustodyTableProps) {
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  const handleCopy = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(hash);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  if (!records || records.length === 0) {
    return (
      <div className="glass-card rounded-xl p-6 text-center text-slate-400 text-sm">
        No chain of custody records found.
      </div>
    );
  }

  return (
    <div className="glass-card rounded-xl overflow-hidden border border-slate-800 shadow-xl">
      <div className="p-4 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
        <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          Cryptographic Chain of Custody & Audit Trail
        </h3>
        <span className="text-xs font-mono text-slate-400">SHA-256 Evidentiary Hashes</span>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-800 text-left text-xs font-mono">
          <thead className="bg-slate-900 text-slate-400 uppercase tracking-wider text-[11px]">
            <tr>
              <th className="px-4 py-3">Timestamp (UTC)</th>
              <th className="px-4 py-3">Event Action</th>
              <th className="px-4 py-3">Evidence File</th>
              <th className="px-4 py-3">SHA-256 Hash</th>
              <th className="px-4 py-3">Investigator</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-300">
            {records.map((rec: any, idx: number) => {
              const shortHash =
                rec.sha256.length > 20
                  ? `${rec.sha256.slice(0, 10)}...${rec.sha256.slice(-8)}`
                  : rec.sha256;

              return (
                <tr key={idx} className="hover:bg-slate-800/40 transition">
                  <td className="px-4 py-2.5 text-slate-400 whitespace-nowrap">
                    {rec.timestamp ? rec.timestamp.replace('T', ' ').slice(0, 19) : 'N/A'}
                  </td>
                  <td className="px-4 py-2.5 text-cyan-300 font-bold whitespace-nowrap">
                    {rec.event}
                  </td>
                  <td className="px-4 py-2.5 whitespace-nowrap">
                    <span className="text-slate-100">{rec.file_name}</span>
                    {rec.notes && <div className="text-[10px] text-slate-500 font-sans">{rec.notes}</div>}
                  </td>
                  <td className="px-4 py-2.5 whitespace-nowrap">
                    <div className="flex items-center gap-1.5">
                      <code className="text-slate-400 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800">
                        {shortHash}
                      </code>
                      {rec.sha256.length > 20 && (
                        <button
                          onClick={() => handleCopy(rec.sha256)}
                          className="text-slate-500 hover:text-cyan-400 p-1"
                          title="Copy Full SHA-256"
                        >
                          {copiedHash === rec.sha256 ? (
                            <Check className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </button>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-2.5 text-slate-400 whitespace-nowrap">
                    {rec.performed_by}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
