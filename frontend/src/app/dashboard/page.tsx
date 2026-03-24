"use client";

import { useState } from "react";
import type { OrchestrationResponse, Persona } from "@/types";
import { orchestrate } from "@/lib/api";
import ResumeViewer from "@/components/ResumeViewer";
import CoverLetterViewer from "@/components/CoverLetterViewer";
import InterviewSimulator from "@/components/InterviewSimulator";

const PERSONAS: { value: Persona; label: string }[] = [
  { value: "software_engineering", label: "Software Engineering" },
  { value: "product_management", label: "Product Management" },
  { value: "operations_marketing", label: "Operations & Marketing" },
  { value: "ui_ux_design", label: "UI/UX & Graphic Design" },
];

type Tab = "resume" | "cover_letter" | "interview";

export default function DashboardPage() {
  const [jobDescription, setJobDescription] = useState("");
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [persona, setPersona] = useState<Persona>("software_engineering");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<OrchestrationResponse | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>("resume");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobDescription.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await orchestrate({
        job_description: jobDescription,
        company,
        role,
        persona,
      });
      setResult(response);
      setActiveTab("resume");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400 mt-1 text-sm">
          Paste a job description to run the full CareerFlow pipeline.
        </p>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              Company
            </label>
            <input
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g. Google"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-600"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              Role
            </label>
            <input
              type="text"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. Senior Software Engineer"
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-600"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">
              Persona
            </label>
            <select
              value={persona}
              onChange={(e) => setPersona(e.target.value as Persona)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-600"
            >
              {PERSONAS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">
            Job Description <span className="text-red-400">*</span>
          </label>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            required
            rows={8}
            placeholder="Paste the full job description here…"
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-600 resize-none"
          />
        </div>

        <button
          type="submit"
          disabled={loading || !jobDescription.trim()}
          className="bg-brand-600 hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold px-6 py-2.5 rounded-lg transition-colors text-sm"
        >
          {loading ? "Running pipeline…" : "Run CareerFlow →"}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg p-4 text-sm">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Loading indicator */}
      {loading && (
        <div className="flex items-center gap-3 text-slate-400 text-sm">
          <svg
            className="animate-spin h-5 w-5 text-brand-500"
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          Tailoring resume · Humanising cover letter · Generating interview script…
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Tabs */}
          <div className="flex gap-1 border-b border-slate-800">
            {(
              [
                { key: "resume" as Tab, label: "📄 Tailored Resume" },
                { key: "cover_letter" as Tab, label: "✍️ Cover Letter" },
                { key: "interview" as Tab, label: "🎤 Interview Script" },
              ] as { key: Tab; label: string }[]
            ).map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key)}
                className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
                  activeTab === key
                    ? "border-brand-500 text-brand-400"
                    : "border-transparent text-slate-500 hover:text-slate-300"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            {activeTab === "resume" && (
              <ResumeViewer resume={result.resume} />
            )}
            {activeTab === "cover_letter" && (
              <CoverLetterViewer coverLetter={result.cover_letter} />
            )}
            {activeTab === "interview" && (
              <InterviewSimulator script={result.interview_script} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}
