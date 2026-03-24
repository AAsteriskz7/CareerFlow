"use client";

import type { InterviewScript } from "@/types";

const CATEGORY_COLOURS: Record<string, string> = {
  Behavioural: "bg-purple-900 text-purple-300",
  Technical: "bg-cyan-900 text-cyan-300",
  "System Design": "bg-amber-900 text-amber-300",
  "Product Sense": "bg-green-900 text-green-300",
};

function categoryClass(category: string): string {
  return (
    CATEGORY_COLOURS[category] ??
    "bg-slate-800 text-slate-300"
  );
}

interface InterviewSimulatorProps {
  script: InterviewScript;
}

export default function InterviewSimulator({ script }: InterviewSimulatorProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <p className="text-slate-400 text-sm">
          Mock interview for{" "}
          <span className="font-medium text-white">{script.role}</span> at{" "}
          <span className="font-medium text-white">{script.company}</span>
        </p>
        <p className="text-xs text-slate-500 mt-0.5">
          {script.questions.length} questions · est.{" "}
          {script.estimated_duration_minutes} min
        </p>
      </div>

      {/* Questions */}
      <div className="space-y-4">
        {script.questions.map((q, i) => (
          <div
            key={i}
            className="bg-slate-900 border border-slate-700 rounded-lg p-4 space-y-2"
          >
            <div className="flex items-start justify-between gap-3">
              <p className="text-white text-sm font-medium leading-snug">
                {i + 1}. {q.question}
              </p>
              <span
                className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${categoryClass(
                  q.category
                )}`}
              >
                {q.category}
              </span>
            </div>
            {q.hint && (
              <p className="text-xs text-slate-400 italic border-t border-slate-800 pt-2">
                💡 {q.hint}
              </p>
            )}
          </div>
        ))}
      </div>

      {/* Prep resources */}
      {script.prep_resources.length > 0 && (
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-4">
          <h4 className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3">
            Prep Resources
          </h4>
          <ul className="space-y-1">
            {script.prep_resources.map((r, i) => (
              <li key={i} className="text-sm text-slate-300 flex gap-2">
                <span className="text-brand-500">→</span>
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
