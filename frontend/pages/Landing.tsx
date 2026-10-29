import Link from "next/link";

import { Node, stagger } from "@/components/roadmap/UI";

const features = [
  {
    number: "01",
    title: "AI Study Partner",
    description:
      "Upload your syllabus and get a week-by-week roadmap. Lessons, a mentor and short assessments sit right next to each mission.",
    points: ["Roadmap from your syllabus", "Lessons, mentor and assessments"],
  },
  {
    number: "02",
    title: "Career Pipeline",
    description:
      "Find internships and competitions worth your time, see the eligibility up front, and keep every application in one list.",
    points: ["Eligibility at a glance", "Application tracking"],
  },
  {
    number: "03",
    title: "Project Lab",
    description:
      "Break a project into milestones and tasks, keep the artifacts and evidence of what you built, and ask the Coach when you get stuck.",
    points: ["Milestones and tasks", "Evidence of learning"],
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
  [105, 150],
  [120, 175],
  [135, 160],
  [150, 190],
  [160, 175],
  [175, 200],
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

const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export default function LandingPage() {
  return (
    <main className="w-full bg-[var(--surface)] font-inter overflow-hidden flex-grow text-[var(--text-primary)]">
      {/*Hero*/}
      <section className="border-b border-[var(--border)]">
        <div className="mx-auto max-w-7xl px-5 pb-16 pt-12 sm:px-8 sm:pb-24 sm:pt-20 lg:px-10 lg:pb-28 lg:pt-24">
          <div className="grid gap-14 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:gap-20">

            {/* Left Column: Copy */}
            <div>
              <h1 className="rise max-w-4xl text-[40px] font-semibold leading-[1.04] tracking-[-0.045em] text-[var(--text-primary)] sm:text-6xl lg:text-7xl">
                The Unified OS for Future-Ready Students
              </h1>

              <p className="rise mt-6 max-w-2xl text-base leading-7 text-[var(--text-secondary)] sm:text-lg sm:leading-8" style={stagger(1)}>
                Turn your syllabus into a weekly plan, build projects you can
                actually show, and find competitions you are eligible for, all
                in one workspace.
              </p>

              <div className="rise mt-9 flex flex-col gap-3 sm:flex-row" style={stagger(2)}>
                <Link
                  href="/register"
                  className="inline-flex h-12 items-center justify-center rounded-xl bg-[var(--primary)] px-6 text-sm font-semibold text-white shadow-[0_4px_14px_0_var(--primary-shadow)] transition duration-200 hover:bg-[var(--primary-hover)] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2"
                >
                  Start Your Journey
                </Link>

                <Link
                  href="#platform"
                  className="inline-flex h-12 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface)] px-6 text-sm font-semibold text-[var(--text-primary)] transition duration-200 hover:bg-[var(--surface-muted)] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                >
                  Watch Demo
                </Link>
              </div>
            </div>

            {/* Right Column: how it works */}
            <div className="rise" style={stagger(2)}>
              <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_12px_40px_rgba(24,52,58,0.07)] sm:p-7">
                <p className="text-sm text-[var(--text-muted)]">How it works</p>
                <p className="mt-0.5 text-lg font-semibold tracking-tight">From syllabus to weekly plan</p>

                <ol className="relative mt-6">
                  <span aria-hidden="true" className="line-grow absolute bottom-8 left-[14px] top-8 w-px bg-[var(--border)]"></span>

                  <li className="relative pb-7 pl-11" style={stagger(2)}>
                    <span className="absolute left-0 top-0"><Node state="idle">1</Node></span>
                    <p className="pt-1 text-sm font-semibold">Upload your syllabus</p>
                    <p className="mt-0.5 text-sm leading-6 text-[var(--text-secondary)]">Drop in the PDF you already have.</p>
                    <div className="mt-3 flex items-center gap-3 rounded-xl border-2 border-dashed border-[var(--border)] px-3 py-2.5">
                      <span className="rounded-md bg-[var(--primary-soft)] px-1.5 py-0.5 text-[10px] font-bold text-[var(--primary)]">PDF</span>
                      <span className="h-2 w-28 rounded-full bg-[var(--border)]"></span>
                    </div>
                  </li>

                  <li className="relative pb-7 pl-11" style={stagger(3)}>
                    <span className="absolute left-0 top-0"><Node state="idle">2</Node></span>
                    <p className="pt-1 text-sm font-semibold">Review what we found</p>
                    <p className="mt-0.5 text-sm leading-6 text-[var(--text-secondary)]">Subjects and topics, ready for you to edit.</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <span className="h-6 w-16 rounded-full bg-[var(--primary-soft)]"></span>
                      <span className="h-6 w-24 rounded-full bg-[var(--primary-soft)]"></span>
                      <span className="h-6 w-12 rounded-full bg-[var(--primary-soft)]"></span>
                      <span className="h-6 w-20 rounded-full bg-[var(--primary-soft)]"></span>
                    </div>
                  </li>

                  <li className="relative pl-11" style={stagger(4)}>
                    <span className="absolute left-0 top-0"><Node state="active" tone="orange">3</Node></span>
                    <p className="pt-1 text-sm font-semibold">Follow your missions</p>
                    <p className="mt-0.5 text-sm leading-6 text-[var(--text-secondary)]">A clear next step, every day.</p>
                    <div className="mt-3 flex gap-[3px]" aria-hidden="true">
                      {[0, 1, 2, 3, 4, 5, 6, 7].map((n) => (
                        <span
                          key={n}
                          className="seg h-2 flex-1 rounded-full"
                          style={{
                            ...stagger(n + 4),
                            backgroundColor: n < 3 ? "var(--primary)" : n === 3 ? "var(--feature-orange)" : "var(--border)",
                          }}
                        ></span>
                      ))}
                    </div>
                  </li>
                </ol>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/*Trust
      <section className="py-10 border-y border-[var(--border)] bg-[var(--surface-alt)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-xs font-bold text-[var(--text-muted)] tracking-[0.16em] uppercase mb-8">
            Trusted by over 50,000 students from elite institutions
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 md:gap-16 opacity-60 grayscale text-[var(--text-secondary)]">
            {["Google", "Microsoft", "Apple", "Amazon", "Meta"].map((company) => (
              <div key={company} className="text-xl md:text-2xl font-bold tracking-tight">
                {company}
              </div>
            ))}
          </div>
        </div>
      </section>*/}

      {/*Advanced analytics*/}
      <section id="analytics" className="mx-auto max-w-7xl px-4 py-20 sm:px-6 md:py-32 lg:px-8">
        <div className="grid items-center gap-14 lg:grid-cols-[0.9fr_1.1fr] lg:gap-20">

          {/* Left Content */}
          <div className="reveal">
            <span className="text-sm font-medium text-[var(--primary)]">Insights</span>
            <h2 className="mt-3 text-4xl font-semibold leading-[1.05] tracking-[-0.035em] md:text-6xl">
              Advanced Analytics.
            </h2>
            <p className="mt-5 text-lg leading-relaxed text-[var(--text-secondary)]">
              Studying hard is not the same as studying on plan. See how your week compares with what you set out to do, and where your skills and projects stand.
            </p>

            <div className="mt-10 divide-y divide-[var(--border)] border-y border-[var(--border)]">
              <div className="group flex gap-4 py-5">
                <span aria-hidden="true" className="mt-3 h-0.5 w-5 shrink-0 rounded-full bg-[var(--primary)] transition-all duration-300 group-hover:w-8"></span>
                <div>
                  <h4 className="text-lg font-semibold">Progress Forecasting</h4>
                  <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">AI predicts when you'll be job-ready based on current learning velocity.</p>
                </div>
              </div>
              <div className="group flex gap-4 py-5">
                <span aria-hidden="true" className="mt-3 h-0.5 w-5 shrink-0 rounded-full bg-[var(--text-muted)] transition-all duration-300 group-hover:w-8 group-hover:bg-[var(--primary)]"></span>
                <div>
                  <h4 className="text-lg font-semibold">Skill Gap Analysis</h4>
                  <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">Compare your skills against top tech requirements to see what's missing.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Visuals: one dashboard panel */}
          <div className="reveal overflow-hidden rounded-3xl border border-[var(--border)] bg-[var(--surface)] shadow-[0_12px_40px_rgba(24,52,58,0.07)]">

            {/* 1. Bar chart */}
            <div className="p-5 sm:p-7">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h5 className="text-sm font-semibold">Learning Velocity</h5>
                <div className="flex gap-3">
                  <span className="flex items-center gap-1.5 text-[11px] text-[var(--text-muted)]"><span className="h-2 w-2 rounded-full bg-[var(--border)]"></span> Expected</span>
                  <span className="flex items-center gap-1.5 text-[11px] text-[var(--text-muted)]"><span className="h-2 w-2 rounded-full bg-[var(--primary)]"></span> Actual</span>
                </div>
              </div>

              <div className="mt-6 flex h-36 items-end justify-between gap-2 border-b border-[var(--border)] sm:gap-4">
                {velocityData.map(([expected, actual], index) => (
                  <div key={index} className="flex h-full w-full items-end justify-center gap-1">
                    <div className="w-1/2 rounded-t-md bg-[var(--border)]" style={{ height: `${expected / 2}%` }}></div>
                    <div className="w-1/2 rounded-t-md bg-[var(--primary)]" style={{ height: `${actual / 2}%` }}></div>
                  </div>
                ))}
              </div>

              <div className="mt-2 flex justify-between gap-2 text-[11px] font-medium text-[var(--text-muted)] sm:gap-4">
                {days.map((day) => (
                  <span key={day} className="w-full text-center">{day}</span>
                ))}
              </div>
            </div>

            {/* 2. Line chart */}
            <div className="border-t border-[var(--border)] bg-[var(--surface-alt)] p-5 sm:p-7">
              <div className="flex items-center justify-between gap-2">
                <h5 className="text-sm font-semibold">Academic Output</h5>
                <span className="rounded-md bg-green-50 px-2 py-0.5 text-[11px] font-semibold text-green-600">Weekly Activity</span>
              </div>

              <div className="relative mt-6 h-28 w-full border-b border-l border-[var(--border)]">
                <div className="absolute inset-0 flex flex-col justify-between">
                  <div className="h-1/4 border-t border-[var(--border)] opacity-60"></div>
                  <div className="h-1/4 border-t border-[var(--border)] opacity-60"></div>
                  <div className="h-1/4 border-t border-[var(--border)] opacity-60"></div>
                </div>

                <svg viewBox="0 0 400 180" className="absolute inset-0 h-full w-full overflow-visible" preserveAspectRatio="none">
                  <polyline
                    points={activityPoints.map(([x, y]) => `${x},${y}`).join(" ")}
                    fill="none"
                    stroke="var(--primary)"
                    strokeWidth="4"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    vectorEffect="non-scaling-stroke"
                  />
                  {activityPoints.map(([x, y], index) => (
                    <circle key={index} cx={x} cy={y} r="5" fill="var(--primary)" stroke="var(--surface-alt)" strokeWidth="2" />
                  ))}
                </svg>
              </div>

              <div className="mt-2 flex justify-between pt-2 text-[11px] font-medium text-[var(--text-muted)]">
                <span>Week 1</span><span>Week 2</span><span>Week 3</span><span>Week 4</span>
              </div>
            </div>

            <p className="border-t border-[var(--border)] px-5 py-3 text-xs text-[var(--text-muted)] sm:px-7">Illustrative data for preview.</p>
          </div>

        </div>
      </section>

      {/*Features*/}
      <section id="platform" className="border-t border-[var(--border)] bg-[var(--surface-muted)] py-20 md:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

          <div className="reveal grid gap-6 md:grid-cols-2 md:items-end md:gap-16">
            <div>
              <p className="text-sm font-medium text-[var(--primary)]">The Platform</p>
              <h2 className="mt-3 text-3xl font-semibold leading-[1.08] tracking-[-0.03em] md:text-5xl">
                Everything you need to accelerate your career.
              </h2>
            </div>
            <p className="text-lg leading-relaxed text-[var(--text-secondary)]">
              A comprehensive ecosystem designed to manage your academic journey and professional growth in one place.
            </p>
          </div>

          <ol className="mt-14 divide-y divide-[var(--border)] border-y border-[var(--border)] md:mt-20">
            {features.map((feature, index) => {
              const colors = [
                { soft: 'var(--feature-purple-soft)', strong: 'var(--feature-purple)' },
                { soft: 'var(--feature-orange-soft)', strong: 'var(--feature-orange)' },
                { soft: 'var(--feature-blue-soft)', strong: 'var(--feature-blue)' },
              ];
              const theme = colors[index % colors.length];

              return (
                <li
                  key={feature.title}
                  className="reveal group grid gap-5 py-9 transition-colors duration-300 hover:bg-[var(--surface)] md:grid-cols-[8rem_1.1fr_1fr] md:items-start md:gap-10 md:px-6 md:py-12"
                >
                  <span
                    className="text-5xl font-semibold leading-none tracking-tight transition-transform duration-300 group-hover:translate-x-1 md:text-6xl"
                    style={{ color: theme.strong }}
                  >
                    {feature.number}
                  </span>

                  <div>
                    <h3 className="text-2xl font-semibold tracking-tight">{feature.title}</h3>
                    <p className="mt-3 max-w-md text-[15px] leading-7 text-[var(--text-secondary)]">
                      {feature.description}
                    </p>
                  </div>

                  <ul className="space-y-3 md:pt-2">
                    {feature.points.map((point) => (
                      <li key={point} className="flex items-center gap-3 text-sm font-medium text-[var(--text-secondary)]">
                        <span aria-hidden="true" className="h-0.5 w-4 shrink-0 rounded-full" style={{ backgroundColor: theme.strong }}></span>
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                </li>
              );
            })}
          </ol>
        </div>
      </section>

      {/*Stats
      <section className="py-16 border-y border-[var(--border)] bg-[var(--surface)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center divide-x divide-[var(--border)]">
            {stats.map(([value, label]) => (
              <div key={label}>
                <div className="text-3xl md:text-4xl font-black mb-2">{value}</div>
                <div className="text-xs text-[var(--text-muted)] font-medium uppercase tracking-wider">{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>*/}

      {/*Testimonials section*
      <section className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-12">
          <span className="text-[var(--primary)] font-semibold tracking-wider text-sm uppercase">Success Stories</span>
          <h2 className="text-3xl md:text-4xl font-bold mt-2">
            Built by students, <br /> for the future of work.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {testimonials.map((testimonial) => (
            <article key={testimonial.name} className="bg-[var(--surface)] p-8 rounded-3xl shadow-sm border border-[var(--border)] flex flex-col justify-between">
              <div>
                <div className="flex gap-1 mb-5">
                  {[...Array(5)].map((_, i) => (
                    <svg key={i} className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
                  ))}
                </div>
                <p className="text-[var(--text-secondary)] text-sm leading-relaxed mb-8">
                  "{testimonial.text}"
                </p>
              </div>
              
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[var(--surface-muted)] overflow-hidden">
                  <img src={testimonial.avatar} alt={testimonial.name} className="w-full h-full object-cover" />
                </div>
                <div>
                  <h4 className="font-bold text-sm">{testimonial.name}</h4>
                  <p className="text-xs text-[var(--text-muted)]">{testimonial.role}</p>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>*/}

      {/* CTA */}
      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6 md:py-28 lg:px-8">
        <div className="reveal rounded-3xl bg-[var(--primary)] px-6 py-14 sm:px-12 md:px-16 md:py-20">
          <div className="grid gap-10 md:grid-cols-[1.3fr_1fr] md:items-end md:gap-16">
            <h2 className="text-4xl font-semibold leading-[1.05] tracking-[-0.035em] text-white md:text-6xl">
              Start with your syllabus.
            </h2>

            <div>
              <p className="text-lg leading-relaxed text-white/80">
                Upload it, check what we found, and get your first week of missions. Free to start.
              </p>

              <Link
                href="/register"
                className="mt-8 inline-flex h-12 w-full items-center justify-center rounded-xl bg-[var(--surface)] px-7 text-sm font-semibold text-[var(--text-primary)] transition duration-200 hover:-translate-y-0.5 hover:shadow-[0_10px_24px_rgba(0,0,0,0.18)] active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--primary)] sm:w-auto"
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