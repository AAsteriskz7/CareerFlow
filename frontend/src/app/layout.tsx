import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CareerFlow — AI Career Orchestration",
  description:
    "Personalised AI dashboard for tailored resumes, humanised cover letters, and mock interview preparation.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen">
        <header className="border-b border-slate-800 px-6 py-4 flex items-center gap-3">
          <span className="text-brand-500 font-bold text-xl tracking-tight">
            CareerFlow
          </span>
          <span className="text-slate-500 text-sm">
            Context-Aware Career Orchestration Engine
          </span>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
