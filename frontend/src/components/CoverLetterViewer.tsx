"use client";

import type { CoverLetter } from "@/types";

interface CoverLetterViewerProps {
  coverLetter: CoverLetter;
}

export default function CoverLetterViewer({ coverLetter }: CoverLetterViewerProps) {
  const handleCopy = () => {
    navigator.clipboard.writeText(coverLetter.prose);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-sm">
            <span className="font-medium text-white">{coverLetter.role}</span> at{" "}
            <span className="font-medium text-white">{coverLetter.company}</span>
          </p>
          <p className="text-xs text-slate-500 mt-0.5">
            {coverLetter.word_count} words
          </p>
        </div>
        <button
          onClick={handleCopy}
          className="text-xs text-brand-500 hover:text-brand-400 border border-brand-700 px-3 py-1 rounded transition-colors"
        >
          Copy to clipboard
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-700 rounded-lg p-5">
        {coverLetter.prose.split("\n\n").map((paragraph, i) => (
          <p key={i} className="text-slate-200 text-sm leading-relaxed mb-4 last:mb-0">
            {paragraph}
          </p>
        ))}
      </div>
    </div>
  );
}
