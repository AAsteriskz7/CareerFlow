"use client";

import type { Resume } from "@/types";

interface ResumeViewerProps {
  resume: Resume;
}

export default function ResumeViewer({ resume }: ResumeViewerProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white">{resume.name}</h2>
        <div className="flex flex-wrap gap-3 mt-1 text-sm text-slate-400">
          {resume.email && <span>{resume.email}</span>}
          {resume.phone && <span>{resume.phone}</span>}
          {resume.linkedin && (
            <a href={resume.linkedin} className="text-brand-500 hover:underline" target="_blank" rel="noreferrer">
              LinkedIn
            </a>
          )}
          {resume.github && (
            <a href={resume.github} className="text-brand-500 hover:underline" target="_blank" rel="noreferrer">
              GitHub
            </a>
          )}
        </div>
        {resume.persona && (
          <span className="inline-block mt-2 text-xs bg-brand-900 text-brand-300 px-2 py-0.5 rounded-full">
            {resume.persona.replace(/_/g, " ")}
          </span>
        )}
      </div>

      {/* Summary */}
      {resume.summary && (
        <section>
          <SectionHeading>Summary</SectionHeading>
          <p className="text-slate-300 text-sm leading-relaxed">{resume.summary}</p>
        </section>
      )}

      {/* Experience */}
      {resume.experience.length > 0 && (
        <section>
          <SectionHeading>Experience</SectionHeading>
          <div className="space-y-4">
            {resume.experience.map((exp, i) => (
              <div key={i} className="border-l-2 border-brand-600 pl-4">
                <div className="flex justify-between items-start flex-wrap gap-1">
                  <span className="font-semibold text-white">{exp.title}</span>
                  <span className="text-xs text-slate-500">
                    {exp.start_date} – {exp.end_date}
                  </span>
                </div>
                <p className="text-sm text-slate-400">{exp.company}</p>
                {exp.bullets.length > 0 && (
                  <ul className="mt-2 space-y-1">
                    {exp.bullets.map((b, j) => (
                      <li key={j} className="text-sm text-slate-300 flex gap-2">
                        <span className="text-brand-500 mt-0.5 shrink-0">•</span>
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Projects */}
      {resume.projects.length > 0 && (
        <section>
          <SectionHeading>Projects</SectionHeading>
          <div className="space-y-3">
            {resume.projects.map((proj, i) => (
              <div key={i}>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-white">{proj.name}</span>
                  {proj.url && (
                    <a href={proj.url} className="text-xs text-brand-500 hover:underline" target="_blank" rel="noreferrer">
                      ↗
                    </a>
                  )}
                </div>
                <p className="text-sm text-slate-400">{proj.description}</p>
                {proj.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1">
                    {proj.technologies.map((t) => (
                      <span key={t} className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Education */}
      {resume.education.length > 0 && (
        <section>
          <SectionHeading>Education</SectionHeading>
          {resume.education.map((edu, i) => (
            <div key={i}>
              <p className="text-white font-semibold">{edu.institution}</p>
              <p className="text-sm text-slate-400">
                {edu.degree} in {edu.field_of_study} · {edu.graduation_year}
                {edu.gpa ? ` · GPA ${edu.gpa}` : ""}
              </p>
            </div>
          ))}
        </section>
      )}

      {/* Skills */}
      {resume.skills.length > 0 && (
        <section>
          <SectionHeading>Skills</SectionHeading>
          <div className="flex flex-wrap gap-2">
            {resume.skills.map((skill) => (
              <span key={skill} className="text-xs bg-slate-800 border border-slate-700 text-slate-300 px-2 py-1 rounded">
                {skill}
              </span>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3 border-b border-slate-800 pb-1">
      {children}
    </h3>
  );
}
