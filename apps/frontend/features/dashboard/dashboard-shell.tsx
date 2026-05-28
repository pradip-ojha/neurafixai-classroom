"use client";

import {
  BarChart3,
  BookOpen,
  BrainCircuit,
  Building2,
  ClipboardCheck,
  FileText,
  GraduationCap,
  ShieldCheck,
  Users
} from "lucide-react";
import { StatusPill } from "@/components/status-pill";

const roleCards = [
  {
    title: "Institution Admin",
    description: "Manage users, academic setup, settings, security posture, and approvals.",
    icon: Building2,
    status: "Phase 4"
  },
  {
    title: "Teacher",
    description: "Prepare content, question banks, exams, reviews, and class analytics.",
    icon: BookOpen,
    status: "Phase 4"
  },
  {
    title: "Student",
    description: "Access study plans, AI tutor, mock tests, results, reports, and feedback.",
    icon: GraduationCap,
    status: "Phase 9"
  },
  {
    title: "Parent",
    description: "View linked child progress, reports, notifications, and school updates.",
    icon: Users,
    status: "Phase 4"
  }
];

const foundationItems = [
  { label: "Main Backend", value: "FastAPI", icon: ShieldCheck },
  { label: "AI Service", value: "Provider-ready", icon: BrainCircuit },
  { label: "Workers", value: "Celery queues", icon: ClipboardCheck },
  { label: "Frontend", value: "Next.js shell", icon: BarChart3 },
  { label: "Database", value: "PostgreSQL", icon: FileText }
];

export function DashboardShell() {
  return (
    <main className="min-h-screen bg-paper">
      <header className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <div>
            <p className="text-xs font-extrabold uppercase text-forest">NeuraFix School OS</p>
            <h1 className="mt-1 text-2xl font-extrabold text-ink sm:text-3xl">Production foundation</h1>
          </div>
          <StatusPill tone="good">Phase 1</StatusPill>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[280px_minmax(0,1fr)] lg:px-8">
        <aside className="rounded-lg border border-line bg-white p-4 shadow-panel">
          <nav className="grid gap-2" aria-label="Dashboard sections">
            {["Overview", "Admin", "Teacher", "Student", "Parent"].map((item, index) => (
              <button
                key={item}
                type="button"
                className={`flex min-h-11 items-center justify-between rounded-md px-3 text-left text-sm font-bold ${
                  index === 0 ? "bg-forest text-white" : "text-muted hover:bg-slate-50 hover:text-ink"
                }`}
              >
                {item}
                {index === 0 ? <ShieldCheck className="h-4 w-4" /> : null}
              </button>
            ))}
          </nav>
        </aside>

        <div className="grid gap-6">
          <section className="rounded-lg border border-line bg-white p-5 shadow-panel">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-xl font-extrabold text-ink">System foundation</h2>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-muted">
                  Phase 1 establishes deployable service boundaries, health checks, local infrastructure,
                  structured logging, and queue wiring. Business modules are intentionally staged for later phases.
                </p>
              </div>
              <StatusPill>Local stack ready</StatusPill>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
              {foundationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <article key={item.label} className="rounded-lg border border-line bg-slate-50 p-4">
                    <Icon className="h-5 w-5 text-forest" />
                    <h3 className="mt-3 text-sm font-extrabold text-ink">{item.label}</h3>
                    <p className="mt-1 text-sm text-muted">{item.value}</p>
                  </article>
                );
              })}
            </div>
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            {roleCards.map((card) => {
              const Icon = card.icon;
              return (
                <article key={card.title} className="rounded-lg border border-line bg-white p-5 shadow-panel">
                  <div className="flex items-start justify-between gap-3">
                    <Icon className="h-6 w-6 text-copper" />
                    <StatusPill tone="warn">{card.status}</StatusPill>
                  </div>
                  <h3 className="mt-4 text-lg font-extrabold text-ink">{card.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-muted">{card.description}</p>
                </article>
              );
            })}
          </section>
        </div>
      </section>
    </main>
  );
}

