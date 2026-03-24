import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center gap-8">
      <h1 className="text-5xl font-bold tracking-tight text-white">
        Your career,{" "}
        <span className="text-brand-500">orchestrated.</span>
      </h1>
      <p className="text-slate-400 max-w-xl text-lg">
        Paste a job description and let CareerFlow tailor your resume, write an
        authentic cover letter, and generate a personalised mock-interview
        script — all in one pipeline.
      </p>
      <Link
        href="/dashboard"
        className="bg-brand-600 hover:bg-brand-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
      >
        Open Dashboard →
      </Link>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-8 w-full max-w-3xl text-left">
        {[
          {
            icon: "📄",
            title: "Resume Tailor",
            desc: "Pulls the right base resume and aligns every impact metric with the job description — no hallucinations.",
          },
          {
            icon: "✍️",
            title: "Cover Letter Humanizer",
            desc: "Uses your past essays as few-shot examples to replicate your authentic voice. No bullets, no jargon.",
          },
          {
            icon: "🎤",
            title: "Interview Simulator",
            desc: "Generates a custom mock-interview script and technical prep questions tailored to the role.",
          },
        ].map((card) => (
          <div
            key={card.title}
            className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col gap-2"
          >
            <span className="text-2xl">{card.icon}</span>
            <h3 className="font-semibold text-white">{card.title}</h3>
            <p className="text-slate-400 text-sm">{card.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
