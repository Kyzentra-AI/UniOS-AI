
import React from "react";
import Link from "next/link";

const features = [
  {
    number: "01",
    title: "AI Study Partner",
    description:
      "Personalized roadmap generator that adapts to your learning pace and professional goals.",
    points: ["Adaptive Curriculum", "Smart Scheduling"],
  },
  {
    number: "02",
    title: "Career Pipeline",
    description:
      "Curated internship listings and application tracking system to land your dream role.",
    points: ["1-Click Applications", "Application Analytics"],
  },
  {
    number: "03",
    title: "Collaborative Lab",
    description:
      "Manage student projects, share feedback, and build a portfolio that stands out to recruiters.",
    points: ["Real-time Feedback", "Portfolio Export"],
  },
];

const testimonials = [
  {
    name: "Sarah Chen",
    role: "CS Student at Stanford",
    text: "UniOS transformed how I approach my engineering projects. The AI roadmap actually understood my goals and provided resources I couldn't find anywhere else.",
    avatar: "https://i.pravatar.cc/100?img=47",
  },
  {
    name: "Marcus Rodriguez",
    role: "Software Eng. Intern",
    text: "Managing internship applications used to be a nightmare. Now I have a centralized hub that tracks everything and gives me feedback on my CV in real-time.",
    avatar: "https://i.pravatar.cc/100?img=12",
  },
  {
    name: "Laila Ahmed",
    role: "Design at NYU",
    text: "The best tool for student teams. We built our entire final year project using UniOS labs. The collaborative features are smoother than any Enterprise tool we tried.",
    avatar: "https://i.pravatar.cc/100?img=32",
  },
];

const stats = [
  ["92%", "Placements within 6mo"],
  ["500+", "Partner Companies"],
  ["1.2M", "Tasks Completed"],
  ["4.9/5", "User Satisfaction"],
];

const velocityData = [
  [150, 105],
  [175, 120],
  [160, 135],
  [190, 150],
  [175, 160],
  [200, 175],
];

const activityPoints = [
  [0, 150],
  [65, 128],
  [130, 138],
  [195, 92],
  [260, 106],
  [325, 62],
  [400, 38],
];

export default function LandingPage() {
  return (
    <main className="min-h-screen overflow-x-hidden bg-[var(--background)] text-[var(--foreground)]">

      {/* =====================================================
          HERO
      ====================================================== */}
      <section>
        <div className="mx-auto max-w-7xl px-5 pb-20 pt-10 sm:px-8 sm:pb-24 sm:pt-14 lg:px-10 lg:pb-28 lg:pt-20">
          <div className="grid gap-14 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:gap-20">

            <div>
              <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-xs font-medium shadow-sm">
                <span className="h-1.5 w-1.5 rounded-full bg-[var(--primary)]" />
                UniOS v2.0 is now live
              </div>

              <h1 className="max-w-4xl text-4xl font-semibold leading-[1.08] tracking-[-0.04em] sm:text-5xl lg:text-6xl">
                The Unified OS for Future-Ready Students
              </h1>

              <p className="mt-6 max-w-2xl text-base leading-7 text-[var(--text-secondary)] sm:text-lg sm:leading-8">
                UniOS integrates project management, internship tracking, and
                personalized roadmaps into one AI-powered workspace. Built for
                high-performers.
              </p>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link
                  href="/register"
                  className="inline-flex h-12 items-center justify-center rounded-lg bg-[var(--primary)] px-6 text-sm font-semibold text-white transition-colors hover:bg-[var(--primary-hover)]"
                >
                  Start Your Journey
                </Link>

                <Link
                  href="#analytics"
                  className="inline-flex h-12 items-center justify-center rounded-lg border border-[var(--border)] bg-[var(--surface)] px-6 text-sm font-semibold text-[var(--text-primary)] shadow-sm transition-colors hover:bg-[var(--surface-muted)]"
                >
                  Watch Demo
                </Link>
              </div>
            </div>

            {/* Product Preview */}
            <div>
              <div className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface)] shadow-[0_12px_40px_rgba(0,0,0,0.06)]">

                

                <div className="grid grid-cols-2 gap-3 p-5">
                  <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                    <p className="text-xs text-[var(--text-secondary)]">
                      Current focus
                    </p>

                    <p className="mt-2 text-sm font-semibold text-[var(--text-primary)]">
                      Learning & Projects
                    </p>
                  </div>

                  <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                    <p className="text-xs text-[var(--text-secondary)]">
                      Workspace
                    </p>

                    <p className="mt-2 text-sm font-semibold text-[var(--text-primary)]">
                      Career Planning
                    </p>
                  </div>
                </div>

                <div className="px-5 pb-5">
                  <div className="rounded-xl border border-[var(--border)] p-5">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-[var(--text-primary)]">
                          Learning Velocity
                        </p>

                        <p className="mt-1 text-xs text-[var(--text-secondary)]">
                          Weekly overview
                        </p>
                      </div>

                      <div className="rounded-md border border-[var(--border)] px-2 py-1 text-[10px] text-[var(--text-secondary)]">
                        Overview
                      </div>
                    </div>

                    <div className="mt-7 flex h-40 items-end gap-2 border-b border-l border-[var(--border)] px-3">
                      {[35, 52, 44, 66, 57, 76, 63, 84].map(
                        (height, index) => (
                          <div
                            key={index}
                            className="flex-1 rounded-t-sm bg-[var(--primary)] opacity-70"
                            style={{ height: `${height}%` }}
                          />
                        )
                      )}
                    </div>

                    <div className="mt-3 flex justify-between text-[10px] text-[var(--text-muted)]">
                      <span>Week 1</span>
                      <span>Week 2</span>
                      <span>Week 3</span>
                      <span>Week 4</span>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3 px-5 pb-5">
                  <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                    <p className="text-[10px] uppercase tracking-wide text-[var(--text-muted)]">
                      Projects
                    </p>

                    <p className="mt-1 text-sm font-semibold">
                      Organized
                    </p>
                  </div>

                  <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                    <p className="text-[10px] uppercase tracking-wide text-[var(--text-muted)]">
                      Internships
                    </p>

                    <p className="mt-1 text-sm font-semibold">
                      Tracked
                    </p>
                  </div>

                  <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                    <p className="text-[10px] uppercase tracking-wide text-[var(--text-muted)]">
                      Roadmaps
                    </p>

                    <p className="mt-1 text-sm font-semibold">
                      Personalized
                    </p>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          TRUSTED BY
      ====================================================== */}
      <section>
        <div className="mx-auto max-w-7xl px-5 pb-16 sm:px-8 lg:px-10 lg:pb-20">

          <p className="text-center text-xs font-medium uppercase tracking-[0.16em] text-[var(--text-secondary)]">
            Trusted by over 50,000 students from elite institutions
          </p>

          <div className="mt-7 grid grid-cols-2 gap-3 sm:grid-cols-6">
            {["Google", "Microsoft", "Apple", "Amazon", "Meta", "Facebook"].map(
              (company) => (
                <div
                  key={company}
                  className="flex h-16 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface)] text-sm font-semibold text-[var(--text-secondary)] shadow-sm"
                >
                  {company}
                </div>
              )
            )}
          </div>
        </div>
      </section>

      {/* =====================================================
          ANALYTICS
      ====================================================== */}
      <section id="analytics" className="bg-[var(--surface-alt)]">
        <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-24 lg:px-10 lg:py-28">

          <div className="grid gap-14 lg:grid-cols-[0.8fr_1.2fr] lg:items-start lg:gap-20">

            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--primary)]">
                Advanced Analytics.
              </p>

              <h2 className="mt-4 text-3xl font-semibold tracking-[-0.03em] sm:text-4xl">
                Advanced Analytics.
              </h2>

              <p className="mt-5 max-w-xl text-base leading-7 text-[var(--text-secondary)]">
                Don't just study—measure your progress. Our integrated
                dashboard provides real-time insights into your skill
                acquisition, project velocity, and internship success rates.
              </p>

              <div className="mt-9 space-y-7">

                <div className="flex gap-4">
                  <div className="mt-1 h-8 w-1 shrink-0 rounded-full bg-[var(--primary)]" />

                  <div>
                    <h3 className="text-sm font-semibold">
                      Progress Forecasting
                    </h3>

                    <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                      AI predicts when you'll be job-ready based on current
                      learning velocity.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="mt-1 h-8 w-1 shrink-0 rounded-full bg-[var(--border)]" />

                  <div>
                    <h3 className="text-sm font-semibold">
                      Skill Gap Analysis
                    </h3>

                    <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                      Compare your skills against top tech requirements to see
                      what's missing.
                    </p>
                  </div>
                </div>

              </div>
            </div>

            <div className="grid gap-5 sm:grid-cols-2">

              {/* Expected vs Actual */}
              <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-sm">

                <div>
                  <p className="text-xs text-[var(--text-secondary)]">
                    Learning Velocity
                  </p>

                  <p className="mt-1 text-lg font-semibold text-[var(--text-primary)]">
                    Expected vs Actual
                  </p>
                </div>

                <div className="mt-8">

                  <div className="relative h-52 border-b border-l border-[var(--border)] px-4">

                    <div className="absolute inset-x-4 bottom-0 top-0 flex items-end justify-between gap-3">

                      {velocityData.map(
                        ([expected, actual], index) => (
                          <div
                            key={index}
                            className="flex h-full flex-1 items-end justify-center"
                          >
                            <div className="flex items-end gap-1.5">

                              <div
                                className="w-3 rounded-t-sm"
                                style={{
                                  height: `${expected}px`,
                                  minHeight: "4px",
                                  backgroundColor:
                                    "var(--border)",
                                }}
                              />

                              <div
                                className="w-3 rounded-t-sm"
                                style={{
                                  height: `${actual}px`,
                                  minHeight: "4px",
                                  backgroundColor:
                                    "var(--primary)",
                                }}
                              />

                            </div>
                          </div>
                        )
                      )}

                    </div>
                  </div>

                  <div className="mt-3 grid grid-cols-6 text-center text-[10px] text-[var(--text-muted)]">
                    <span>Mon</span>
                    <span>Tue</span>
                    <span>Wed</span>
                    <span>Thu</span>
                    <span>Fri</span>
                    <span>Sat</span>
                  </div>
                </div>

                <div className="mt-5 flex gap-5 text-[10px] text-[var(--text-secondary)]">

                  <span className="flex items-center gap-2">
                    <span
                      className="h-2 w-2 rounded-sm"
                      style={{
                        backgroundColor: "var(--border)",
                      }}
                    />
                    Expected
                  </span>

                  <span className="flex items-center gap-2">
                    <span
                      className="h-2 w-2 rounded-sm"
                      style={{
                        backgroundColor: "var(--primary)",
                      }}
                    />
                    Actual
                  </span>

                </div>
              </div>

              {/* Academic Output */}
              <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-sm">

                <div>
                  <p className="text-xs text-[var(--text-secondary)]">
                    Academic Output
                  </p>

                  <p className="mt-1 text-lg font-semibold text-[var(--text-primary)]">
                    Weekly Activity
                  </p>
                </div>

                <div className="relative mt-8 h-52 border-b border-l border-[var(--border)]">

                  <div className="absolute inset-0">

                    <div className="absolute left-0 right-0 top-1/4 border-t border-[var(--border)] opacity-50" />

                    <div className="absolute left-0 right-0 top-1/2 border-t border-[var(--border)] opacity-50" />

                    <div className="absolute left-0 right-0 top-3/4 border-t border-[var(--border)] opacity-50" />

                  </div>

                  <svg
                    viewBox="0 0 400 180"
                    className="absolute inset-0 h-full w-full"
                    preserveAspectRatio="none"
                  >

                    <polyline
                      points={activityPoints
                        .map(([x, y]) => `${x},${y}`)
                        .join(" ")}
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                      className="text-[var(--primary)]"
                    />

                    {activityPoints.map(([x, y], index) => (
                      <circle
                        key={index}
                        cx={x}
                        cy={y}
                        r="4"
                        fill="currentColor"
                        className="text-[var(--primary)]"
                      />
                    ))}

                  </svg>
                </div>

                <div className="mt-3 flex justify-between text-[10px] text-[var(--text-muted)]">
                  <span>Week 1</span>
                  <span>Week 2</span>
                  <span>Week 3</span>
                  <span>Week 4</span>
                </div>

              </div>

            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          FEATURES
      ====================================================== */}
      <section>
        <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-24 lg:px-10 lg:py-28">

          <div className="max-w-2xl">

            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--primary)]">
              The Platform
            </p>

            <h2 className="mt-4 text-3xl font-semibold tracking-[-0.03em] sm:text-4xl">
              Everything you need to accelerate your career.
            </h2>

            <p className="mt-5 text-base leading-7 text-[var(--text-secondary)]">
              A comprehensive ecosystem designed to manage your academic
              journey and professional growth in one place.
            </p>

          </div>

          <div className="mt-12 grid gap-5 md:grid-cols-3">

            {features.map((feature) => (
              <article
                key={feature.title}
                className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm transition-shadow hover:shadow-md sm:p-8"
              >

                <div className="flex items-center justify-between">

                  <span className="text-xs font-medium text-[var(--text-muted)]">
                    {feature.number}
                  </span>

                  <span className="text-lg text-[var(--primary)]">
                    ↗
                  </span>

                </div>

                <h3 className="mt-12 text-xl font-semibold">
                  {feature.title}
                </h3>

                <p className="mt-4 text-sm leading-6 text-[var(--text-secondary)]">
                  {feature.description}
                </p>

                <div className="mt-7 space-y-3">

                  {feature.points.map((point) => (
                    <div
                      key={point}
                      className="flex items-center gap-3 text-sm"
                    >

                      <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-[var(--surface-alt)] text-[10px] text-[var(--primary)]">
                        ✓
                      </span>

                      <span>{point}</span>

                    </div>
                  ))}

                </div>

              </article>
            ))}

          </div>
        </div>
      </section>

      {/* =====================================================
          STATS
      ====================================================== */}
      <section className="bg-[var(--surface-alt)]">
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 lg:px-10 lg:py-20">

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

            {stats.map(([value, label]) => (
              <div
                key={label}
                className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm sm:p-7"
              >

                <p className="text-3xl font-semibold tracking-[-0.04em] sm:text-4xl">
                  {value}
                </p>

                <p className="mt-2 max-w-[140px] text-xs leading-5 text-[var(--text-secondary)] sm:text-sm">
                  {label}
                </p>

              </div>
            ))}

          </div>
        </div>
      </section>

      {/* =====================================================
          TESTIMONIALS
      ====================================================== */}
      <section>
        <div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 sm:py-24 lg:px-10 lg:py-28">

          <div className="max-w-2xl">

            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--primary)]">
              Success Stories
            </p>

            <h2 className="mt-4 text-3xl font-semibold tracking-[-0.03em] sm:text-4xl">
              Built by students, for the future of work.
            </h2>

          </div>

          <div className="mt-12 grid gap-5 md:grid-cols-3">

            {testimonials.map((testimonial) => (
              <article
                key={testimonial.name}
                className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm sm:p-8"
              >

                <div className="flex items-center gap-3">

                  <img
                    src={testimonial.avatar}
                    alt={testimonial.name}
                    className="h-10 w-10 rounded-full object-cover"
                  />

                  <div>

                    <p className="text-sm font-semibold">
                      {testimonial.name}
                    </p>

                    <p className="mt-0.5 text-xs text-[var(--text-secondary)]">
                      {testimonial.role}
                    </p>

                  </div>
                </div>

                <p className="mt-7 text-sm leading-7 text-[var(--text-secondary)]">
                  “{testimonial.text}”
                </p>

              </article>
            ))}

          </div>
        </div>
      </section>

      {/* =====================================================
          CTA
      ====================================================== */}
      <section>
        <div className="mx-auto max-w-7xl px-5 pb-20 sm:px-8 sm:pb-24 lg:px-10 lg:pb-28">

          <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-alt)] px-6 py-14 shadow-sm sm:px-10 sm:py-16">

            <div className="mx-auto max-w-3xl text-center">

              <h2 className="text-3xl font-semibold tracking-[-0.04em] sm:text-4xl lg:text-5xl">
                Ready to supercharge your career?
              </h2>

              <p className="mx-auto mt-5 max-w-2xl text-sm leading-7 text-[var(--text-secondary)] sm:text-base">
                Join thousands of students who are building their future with
                the power of UniOS. Start for free today.
              </p>

              <Link
                href="/register"
                className="mt-8 inline-flex h-12 items-center justify-center rounded-lg bg-[var(--primary)] px-7 text-sm font-semibold text-white transition-colors hover:bg-[var(--primary-hover)]"
              >
                Get Started for Free
              </Link>

            </div>
          </div>
        </div>
      </section>

    </main>
  );
}
