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
    <main className="w-full bg-[var(--surface)] font-inter overflow-hidden flex-grow text-[var(--text-primary)]">
      {/*Hero*/}
      <section className="relative">
        {/* Subtle Ambient Background Glow for Glassmorphism */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[600px] bg-gradient-to-b from-[var(--primary-soft)] to-transparent opacity-30 blur-3xl -z-10 pointer-events-none"></div>

        <div className="mx-auto max-w-7xl px-5 pb-20 pt-10 sm:px-8 sm:pb-24 sm:pt-14 lg:px-10 lg:pb-28 lg:pt-20">
          <div className="grid gap-14 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:gap-20">
            
            {/* Left Column: Copy */}
            <div className="z-10">
              <h1 className="max-w-4xl text-4xl font-semibold leading-[1.08] tracking-[-0.04em] sm:text-5xl lg:text-6xl text-[var(--text-primary)] drop-shadow-sm">
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
                  className="inline-flex h-12 items-center justify-center rounded-xl bg-[var(--primary)] px-6 text-sm font-semibold text-white transition-all duration-300 hover:bg-[var(--primary-hover)] shadow-[0_8px_20px_-6px_var(--primary)] hover:shadow-[0_12px_24px_-6px_var(--primary)] hover:-translate-y-0.5"
                >
                  Start Your Journey
                </Link>

                <Link
                  href="#analytics"
                  className="inline-flex h-12 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface)]/80 backdrop-blur-md px-6 text-sm font-semibold text-[var(--text-primary)] shadow-[0_4px_12px_rgba(0,0,0,0.03)] transition-all duration-300 hover:bg-[var(--surface-muted)] hover:shadow-[0_6px_16px_rgba(0,0,0,0.06)] hover:-translate-y-0.5"
                >
                  Watch Demo
                </Link>
              </div>
            </div>

            {/* Right Column: Visual */}
            <div className="relative w-full h-[450px] sm:h-[550px] hidden lg:flex items-center justify-center mt-8 lg:mt-0">
              
              {/* Blurred glowing orbs for backdrop */}
              <div className="absolute w-[340px] h-[340px] bg-[var(--primary-soft)] rounded-full blur-3xl opacity-60 z-0"></div>
              <div className="absolute w-[280px] h-[280px] bg-[var(--primary)] rounded-full blur-3xl opacity-20 translate-x-10 translate-y-10 z-0"></div>
              
              <div className="relative z-10 w-[280px] h-[400px] flex items-end justify-center rounded-b-3xl shadow-[0_20px_40px_rgba(0,0,0,0.1)] transition-transform duration-500 hover:scale-[1.02]">
                <img 
                  src="https://images.unsplash.com/photo-1544717305-2782549b5136?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" 
                  alt="Student Cutout" 
                  className="w-full h-full object-cover object-top rounded-b-3xl [clip-path:polygon(0_0,100%_0,100%_90%,50%_100%,0_90%)]" 
                />
              </div>

              {/* Top Left Card - Glassmorphism */}
              <div className="absolute top-[15%] -left-[10%] z-20 flex gap-3 rounded-2xl border border-[var(--border)]/50 bg-[var(--surface)]/80 backdrop-blur-xl py-3.5 pl-4 pr-5 shadow-[0_8px_32px_rgba(0,0,0,0.08)] transform hover:-translate-y-1 transition-all duration-300">
                <span aria-hidden="true" className="w-1 self-stretch rounded-full bg-gradient-to-b from-[var(--primary)] to-[var(--primary-soft)] shadow-[0_0_8px_var(--primary-soft)]"></span>
                <div>
                  <p className="text-sm font-bold text-[var(--text-primary)]">Syllabus to roadmap</p>
                  <p className="text-xs text-[var(--text-secondary)]">Built around your goals</p>
                </div>
              </div>

              {/* Middle Right Card - Glassmorphism */}
              <div className="absolute top-[35%] -right-[5%] z-20 bg-[var(--surface)]/80 backdrop-blur-xl p-5 rounded-2xl shadow-[0_8px_32px_rgba(0,0,0,0.08)] border border-[var(--border)]/50 flex flex-col gap-1 transform hover:-translate-y-1 transition-all duration-300">
                <p className="text-xl font-black text-[var(--primary)] tracking-tight drop-shadow-sm">Weekly missions</p>
                <p className="text-xs font-medium text-[var(--text-secondary)]">A clear next step, every day</p>
              </div>

              {/* Bottom Center Card - Glassmorphism */}
              <div className="absolute -bottom-[5%] left-1/2 -translate-x-1/2 z-20 bg-[var(--surface)]/80 backdrop-blur-xl p-4 rounded-2xl shadow-[0_12px_40px_rgba(0,0,0,0.1)] border border-[var(--border)]/50 flex flex-col items-center gap-3 transform hover:-translate-y-1 transition-all duration-300">
                <div className="flex gap-1.5">
                  {[
                    ["Study", "--feature-purple"],
                    ["Internships", "--feature-orange"],
                    ["Projects", "--feature-blue"],
                  ].map(([label, token]) => (
                    <span
                      key={label}
                      className="rounded-full px-3 py-1 text-xs font-semibold shadow-sm"
                      style={{ backgroundColor: `var(${token}-soft)`, color: `var(${token})` }}
                    >
                      {label}
                    </span>
                  ))}
                </div>
                <p className="text-xs font-medium text-[var(--text-secondary)]">All in one workspace</p>
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
      <section id="analytics" className="py-20 md:py-32 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto overflow-hidden relative">
        <div className="flex flex-col lg:flex-row items-center gap-16">
          
          {/* Left Content */}
          <div className="w-full lg:w-1/2 space-y-8 z-10">
            <div>
              <span className="text-[var(--primary)] font-semibold tracking-wider text-sm uppercase">Insights</span>
              <h2 className="text-3xl md:text-5xl font-bold mt-2 mb-4">
                Advanced Analytics.
              </h2>
              <p className="text-[var(--text-secondary)] text-lg leading-relaxed">
                Don't just study—measure your progress. Our integrated dashboard provides real-time insights into your skill acquisition, project velocity, and internship success rates.
              </p>
            </div>

            <div className="space-y-8 mt-8">
              <div className="flex gap-4 items-start group">
                <div className="w-8 h-8 rounded-xl bg-[var(--primary-soft)]/50 shadow-[inset_0_2px_4px_rgba(255,255,255,0.3),0_2px_8px_rgba(0,0,0,0.05)] flex items-center justify-center shrink-0 transition-transform group-hover:scale-110">
                  <div className="w-3 h-3 rounded-full bg-[var(--primary)] shadow-[0_0_8px_var(--primary)]"></div>
                </div>
                <div>
                  <h4 className="text-lg font-bold">Progress Forecasting</h4>
                  <p className="text-sm text-[var(--text-secondary)] mt-1">AI predicts when you'll be job-ready based on current learning velocity.</p>
                </div>
              </div>
              <div className="flex gap-4 items-start group">
                <div className="w-8 h-8 rounded-xl bg-[var(--surface)] border border-[var(--border)] shadow-[inset_0_2px_4px_rgba(255,255,255,0.5),0_2px_8px_rgba(0,0,0,0.03)] flex items-center justify-center shrink-0 transition-transform group-hover:scale-110">
                  <div className="w-3 h-3 rounded-full bg-[var(--text-muted)]"></div>
                </div>
                <div>
                  <h4 className="text-lg font-bold">Skill Gap Analysis</h4>
                  <p className="text-sm text-[var(--text-secondary)] mt-1">Compare your skills against top tech requirements to see what's missing.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Visuals (Glassmorphic Mockups) */}
          <div className="w-full lg:w-1/2 relative min-h-[450px]">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[140%] h-[140%] bg-[var(--primary-soft)] rounded-full blur-3xl -z-10 opacity-50"></div>
            
            {/* 1. Bar Chart Mockup (Top Right) */}
            <div className="absolute top-0 right-0 w-5/6 bg-[var(--surface)]/70 backdrop-blur-2xl rounded-3xl border border-[var(--border)]/40 p-6 shadow-[0_16px_40px_-8px_rgba(0,0,0,0.1)] z-10 transform hover:-translate-y-2 transition-transform duration-500">
              <div className="flex justify-between items-center mb-6">
                <h5 className="font-bold text-sm">Learning Velocity</h5>
                <div className="flex gap-2">
                  <span className="flex items-center gap-1 text-[10px] text-[var(--text-muted)]"><div className="w-2 h-2 bg-[var(--border)] rounded-full"></div> Expected</span>
                  <span className="flex items-center gap-1 text-[10px] text-[var(--text-muted)]"><div className="w-2 h-2 bg-[var(--primary)] shadow-[0_0_6px_var(--primary)] rounded-full"></div> Actual</span>
                </div>
              </div>
              
              <div className="flex items-end justify-between gap-3 h-32 mb-2 border-b border-[var(--border)]/50 pb-2">
                {velocityData.map(([expected, actual], index) => (
                  <div key={index} className="w-full flex items-end justify-center gap-1">
                    <div className="w-1/2 bg-[var(--border)]/70 rounded-t-md transition-all hover:bg-[var(--border)]" style={{ height: `${expected / 2}%` }}></div>
                    <div className="w-1/2 bg-gradient-to-t from-[var(--primary)] to-[var(--primary-hover)] rounded-t-md shadow-[0_4px_12px_rgba(0,0,0,0.1)]" style={{ height: `${actual / 2}%` }}></div>
                  </div>
                ))}
              </div>
              
              <div className="flex justify-between text-[9px] text-[var(--text-muted)] font-medium px-2 uppercase">
                <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span>
              </div>
            </div>

            {/* 2. Line Chart Mockup (Bottom Left) */}
            <div className="absolute bottom-10 left-0 w-3/4 bg-[var(--surface)]/70 backdrop-blur-2xl rounded-3xl border border-[var(--border)]/40 p-6 shadow-[0_24px_50px_-12px_rgba(0,0,0,0.12)] z-20 transform hover:-translate-y-2 transition-transform duration-500">
              <div className="flex justify-between items-center mb-6">
                <h5 className="font-bold text-sm">Academic Output</h5>
                <span className="text-[10px] font-semibold text-green-600 bg-green-50/80 backdrop-blur-sm px-2.5 py-1 rounded-lg border border-green-100">Weekly Activity</span>
              </div>
              
              <div className="h-24 w-full relative border-b border-l border-[var(--border)]/50">
                <div className="absolute inset-0 flex flex-col justify-between">
                  <div className="border-t border-[var(--border)] opacity-30 h-1/4"></div>
                  <div className="border-t border-[var(--border)] opacity-30 h-1/4"></div>
                  <div className="border-t border-[var(--border)] opacity-30 h-1/4"></div>
                </div>

                <svg viewBox="0 0 400 180" className="absolute inset-0 h-full w-full overflow-visible drop-shadow-md" preserveAspectRatio="none">
                  <polyline 
                    points={activityPoints.map(([x, y]) => `${x},${y}`).join(" ")} 
                    fill="none" 
                    stroke="var(--primary)" 
                    strokeWidth="4" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                  />
                  {activityPoints.map(([x, y], index) => (
                    <circle key={index} cx={x} cy={y} r="6" fill="var(--surface)" stroke="var(--primary)" strokeWidth="3" className="shadow-sm" />
                  ))}
                </svg>
              </div>
              
              <div className="flex justify-between text-[9px] text-[var(--text-muted)] font-medium mt-2 uppercase pt-2">
                <span>Week 1</span><span>Week 2</span><span>Week 3</span><span>Week 4</span>
              </div>
            </div>
            
          </div>
        </div>
      </section>

      {/*Features*/}
      <section className="py-20 bg-[var(--surface-muted)]/30 border-t border-[var(--border)]/60 relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-3xl mx-auto mb-16">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-[var(--primary)] mb-4">
              The Platform
            </p>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Everything you need to accelerate your career.
            </h2>
            <p className="text-[var(--text-secondary)] text-lg">
              A comprehensive ecosystem designed to manage your academic journey and professional growth in one place.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const colors = [
                { soft: 'var(--feature-purple-soft)', strong: 'var(--feature-purple)' },
                { soft: 'var(--feature-orange-soft)', strong: 'var(--feature-orange)' },
                { soft: 'var(--feature-blue-soft)', strong: 'var(--feature-blue)' },
              ];
              const theme = colors[index % colors.length];

              return (
                <article key={feature.title} className="group relative bg-[var(--surface)]/60 backdrop-blur-lg rounded-[2rem] p-8 border border-[var(--border)]/50 shadow-[0_8px_24px_rgba(0,0,0,0.03),inset_0_1px_1px_rgba(255,255,255,0.4)] hover:shadow-[0_20px_40px_rgba(0,0,0,0.06),inset_0_1px_1px_rgba(255,255,255,0.5)] hover:-translate-y-1 transition-all duration-300">
                  {/* Neumorphic Inner Glow Layer */}
                  <div className="absolute inset-0 rounded-[2rem] bg-gradient-to-br from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>

                  <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-2xl text-base font-bold tracking-tight shadow-[inset_0_2px_4px_rgba(255,255,255,0.4),0_4px_12px_rgba(0,0,0,0.05)] transition-transform group-hover:scale-110" style={{ backgroundColor: theme.soft, color: theme.strong }}>
                    {feature.number}
                  </div>
                  
                  <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                  <p className="text-[var(--text-secondary)] text-sm mb-6 leading-relaxed">
                    {feature.description}
                  </p>
                  
                  <div className="space-y-3">
                    {feature.points.map((point) => (
                      <div key={point} className="flex items-center gap-3 text-sm text-[var(--text-secondary)] font-medium">
                        <span aria-hidden="true" className="h-0.5 w-4 shrink-0 rounded-full bg-[var(--primary)] shadow-[0_0_4px_var(--primary)]"></span>
                        <span>{point}</span>
                      </div>
                    ))}
                  </div>
                </article>
              );
            })}
          </div>
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

      {/* CTA - Glassmorphic Pane */}
      <section className="pb-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto mt-10">
        <div className="bg-[var(--surface)]/60 backdrop-blur-2xl border border-[var(--border)] shadow-[0_16px_40px_-12px_rgba(0,0,0,0.1),inset_0_1px_1px_rgba(255,255,255,0.2)] rounded-[3rem] p-12 md:p-20 text-center relative overflow-hidden">

          {/* Visible dark circle - top right blurred for ambient feel */}
          <div className="absolute -top-20 -right-20 w-64 h-64 bg-[var(--primary)]/10 blur-3xl rounded-full pointer-events-none"></div>

          {/* Subtle circle - bottom left blurred */}
          <div className="absolute -bottom-24 -left-20 w-64 h-64 bg-[var(--primary)]/5 blur-3xl rounded-full pointer-events-none"></div>

          <div className="relative z-10 max-w-2xl mx-auto">
            <h2 className="text-3xl md:text-5xl font-bold text-[var(--text-primary)] mb-6 drop-shadow-sm">
              Ready to supercharge your career?
            </h2>

            <p className="text-[var(--text-secondary)] text-lg mb-10">
              Join thousands of students who are building their future with the power of UniOS. Start for free today.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/register"
                className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-[var(--primary)] to-[var(--primary-hover)] text-white font-bold rounded-2xl transition-all duration-300 shadow-[0_8px_20px_-6px_var(--primary)] hover:shadow-[0_12px_24px_-6px_var(--primary)] hover:-translate-y-1"
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