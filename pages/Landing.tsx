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
      <section>
        <div className="mx-auto max-w-7xl px-5 pb-20 pt-10 sm:px-8 sm:pb-24 sm:pt-14 lg:px-10 lg:pb-28 lg:pt-20">
          <div className="grid gap-14 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:gap-20">

            {/* Left Column: Copy */}
            <div className="z-10">

              <h1 className="max-w-4xl text-4xl font-semibold leading-[1.08] tracking-[-0.04em] sm:text-5xl lg:text-6xl text-[var(--text-primary)]">
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
                  className="inline-flex h-12 items-center justify-center rounded-lg bg-[var(--primary)] px-6 text-sm font-semibold text-white transition-colors hover:bg-[var(--primary-hover)] shadow-[0_4px_14px_0_var(--primary-shadow)]"
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

            {/* Right Column: Visual (Exact 596a69.png Match) */}
            <div className="relative w-full h-[450px] sm:h-[550px] hidden lg:flex items-center justify-center mt-8 lg:mt-0">
            
              <div className="absolute w-[340px] h-[340px] bg-[var(--primary-soft)] rounded-[40px] rotate-12 z-0"></div>
            
              <div className="absolute w-[320px] h-[360px] bg-[var(--primary)] opacity-10 rounded-[40px] -rotate-6 z-0"></div>
              <div className="relative z-10 w-[280px] h-[400px] flex items-end justify-center">
                
                <img 
                  src="https://images.unsplash.com/photo-1544717305-2782549b5136?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80" 
                  alt="Student Cutout" 
                  className="w-full h-full object-cover object-top rounded-b-3xl [clip-path:polygon(0_0,100%_0,100%_90%,50%_100%,0_90%)]" 
                
                />
              </div>

              {/* Top Left Card (Review) */}
              <div className="absolute top-[15%] -left-[10%] z-20 bg-[var(--surface)] p-3.5 rounded-2xl shadow-[0_12px_30px_rgba(0,0,0,0.08)] border border-[var(--border)] flex items-center gap-3 transform hover:-translate-y-1 transition-transform">
                <img src="https://i.pravatar.cc/100?img=11" alt="User" className="w-10 h-10 rounded-full" />
                <div>
                  <p className="text-sm font-bold text-[var(--text-primary)]">Sarah Cooper</p>
                  <p className="text-xs text-[var(--text-secondary)]">I loved the OS course!</p>
                </div>
              </div>

              {/* Middle Right Card (Stats) */}
              <div className="absolute top-[35%] -right-[5%] z-20 bg-[var(--surface)] p-5 rounded-2xl shadow-[0_12px_30px_rgba(0,0,0,0.08)] border border-[var(--border)] flex flex-col gap-1 transform hover:-translate-y-1 transition-transform">
                <p className="text-xl font-black text-[var(--primary)] tracking-tight">150+ DSA</p>
                <p className="text-xs font-medium text-[var(--text-secondary)]">Curated Problems</p>
              </div>

              {/* Bottom Center Card (Avatars) */}
              <div className="absolute -bottom-[5%] left-1/2 -translate-x-1/2 z-20 bg-[var(--surface)] p-4 rounded-2xl shadow-[0_12px_30px_rgba(0,0,0,0.08)] border border-[var(--border)] flex flex-col items-center gap-3 transform hover:-translate-y-1 transition-transform">
                <div className="flex -space-x-3">
                  <img src="https://i.pravatar.cc/100?img=41" className="w-9 h-9 rounded-full ring-2 ring-[var(--surface)]" alt="User" />
                  <img src="https://i.pravatar.cc/100?img=12" className="w-9 h-9 rounded-full ring-2 ring-[var(--surface)]" alt="User" />
                  <img src="https://i.pravatar.cc/100?img=33" className="w-9 h-9 rounded-full ring-2 ring-[var(--surface)]" alt="User" />
                  <div className="w-9 h-9 rounded-full bg-[var(--primary-soft)] text-[var(--primary)] flex items-center justify-center text-xs font-bold ring-2 ring-[var(--surface)]">
                    +50
                  </div>
                </div>
                <p className="text-xs font-medium text-[var(--text-secondary)]">Active learners daily</p>
              </div>

            </div>

          </div>
        </div>
      </section>

      {/*Trust*/}
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
      </section>

      {/*Advanced analytics*/}
      <section id="analytics" className="py-20 md:py-32 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto overflow-hidden">
        <div className="flex flex-col lg:flex-row items-center gap-16">
          
          {/* Left Content */}
          <div className="w-full lg:w-1/2 space-y-8">
            <div>
              <span className="text-[var(--primary)] font-semibold tracking-wider text-sm uppercase">Advanced Analytics.</span>
              <h2 className="text-3xl md:text-5xl font-bold mt-2 mb-4">
                Advanced Analytics.
              </h2>
              <p className="text-[var(--text-secondary)] text-lg leading-relaxed">
                Don't just study—measure your progress. Our integrated dashboard provides real-time insights into your skill acquisition, project velocity, and internship success rates.
              </p>
            </div>

            <div className="space-y-8 mt-8">
              <div className="flex gap-4 items-start">
                <div className="w-6 h-6 rounded-full bg-[var(--primary-soft)] flex items-center justify-center shrink-0 mt-1">
                  <div className="w-2.5 h-2.5 rounded-full bg-[var(--primary)]"></div>
                </div>
                <div>
                  <h4 className="text-lg font-bold">Progress Forecasting</h4>
                  <p className="text-sm text-[var(--text-secondary)] mt-1">AI predicts when you'll be job-ready based on current learning velocity.</p>
                </div>
              </div>
              <div className="flex gap-4 items-start">
                <div className="w-6 h-6 rounded-full bg-[var(--border)] flex items-center justify-center shrink-0 mt-1">
                  <div className="w-2.5 h-2.5 rounded-full bg-[var(--text-muted)]"></div>
                </div>
                <div>
                  <h4 className="text-lg font-bold">Skill Gap Analysis</h4>
                  <p className="text-sm text-[var(--text-secondary)] mt-1">Compare your skills against top tech requirements to see what's missing.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Visuals (Figma Overlapping Charts Mockup) */}
          <div className="w-full lg:w-1/2 relative min-h-[450px]">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[140%] h-[140%] bg-[var(--primary-soft)] rounded-full blur-3xl -z-10 opacity-60"></div>
            
            {/* 1. Bar Chart Mockup (Top Right) */}
            <div className="absolute top-0 right-0 w-5/6 bg-[var(--surface)] rounded-2xl border border-[var(--border)] p-6 shadow-lg z-10 transform hover:-translate-y-2 transition-transform duration-500">
              <div className="flex justify-between items-center mb-6">
                <h5 className="font-bold text-sm">Learning Velocity</h5>
                <div className="flex gap-2">
                  <span className="flex items-center gap-1 text-[10px] text-[var(--text-muted)]"><div className="w-2 h-2 bg-[var(--border)] rounded-full"></div> Expected</span>
                  <span className="flex items-center gap-1 text-[10px] text-[var(--text-muted)]"><div className="w-2 h-2 bg-[var(--primary)] rounded-full"></div> Actual</span>
                </div>
              </div>
              
              <div className="flex items-end justify-between gap-3 h-32 mb-2 border-b border-[var(--border)] pb-2">
                {velocityData.map(([expected, actual], index) => (
                  <div key={index} className="w-full flex items-end justify-center gap-1">
                    <div className="w-1/2 bg-[var(--border)] rounded-t-sm" style={{ height: `${expected / 2}%` }}></div>
                    <div className="w-1/2 bg-[var(--primary)] rounded-t-sm" style={{ height: `${actual / 2}%` }}></div>
                  </div>
                ))}
              </div>
              
              <div className="flex justify-between text-[9px] text-[var(--text-muted)] font-medium px-2 uppercase">
                <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span>
              </div>
            </div>

            {/* 2. Line Chart Mockup (Bottom Left) */}
            <div className="absolute bottom-10 left-0 w-3/4 bg-[var(--surface)] rounded-2xl border border-[var(--border)] p-6 shadow-xl z-20 transform hover:-translate-y-2 transition-transform duration-500">
              <div className="flex justify-between items-center mb-6">
                <h5 className="font-bold text-sm">Academic Output</h5>
                <span className="text-[10px] font-semibold text-green-600 bg-green-50 px-2 py-0.5 rounded">Weekly Activity</span>
              </div>
              
              <div className="h-24 w-full relative border-b border-l border-[var(--border)]">
                {/* Horizontal Grid Lines */}
                <div className="absolute inset-0 flex flex-col justify-between">
                  <div className="border-t border-[var(--border)] opacity-50 h-1/4"></div>
                  <div className="border-t border-[var(--border)] opacity-50 h-1/4"></div>
                  <div className="border-t border-[var(--border)] opacity-50 h-1/4"></div>
                </div>

                <svg viewBox="0 0 400 180" className="absolute inset-0 h-full w-full overflow-visible" preserveAspectRatio="none">
                  <polyline 
                    points={activityPoints.map(([x, y]) => `${x},${y}`).join(" ")} 
                    fill="none" 
                    stroke="var(--primary)" 
                    strokeWidth="4" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                  />
                  {activityPoints.map(([x, y], index) => (
                    <circle key={index} cx={x} cy={y} r="5" fill="var(--primary)" stroke="var(--surface)" strokeWidth="2" />
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
      <section className="py-20 bg-[var(--surface-muted)] border-t border-[var(--border)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-3xl mx-auto mb-16">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--primary)] mb-4">
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
                <article key={feature.title} className="bg-[var(--surface)] rounded-3xl p-8 border border-[var(--border)] shadow-sm hover:shadow-md transition-shadow">
                  <div className="w-12 h-12 rounded-2xl flex items-center justify-center mb-6" style={{ backgroundColor: theme.soft, color: theme.strong }}>
                    {index === 0 && <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>}
                    {index === 1 && <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>}
                    {index === 2 && <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>}
                  </div>
                  
                  <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                  <p className="text-[var(--text-secondary)] text-sm mb-6 leading-relaxed">
                    {feature.description}
                  </p>
                  
                  <div className="space-y-3">
                    {feature.points.map((point) => (
                      <div key={point} className="flex items-center gap-3 text-sm text-[var(--text-secondary)] font-medium">
                        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-[var(--surface-alt)] text-[10px] text-green-500 border border-[var(--border)]">
                          ✓
                        </span>
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

      {/*Stats*/}
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
      </section>

      {/*Testimonials section*/}
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
      </section>

      {/*CTA*/}
      <section className="pb-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="bg-[var(--primary)] rounded-[40px] p-12 md:p-20 text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-black/10 rounded-full blur-3xl translate-y-1/3 -translate-x-1/3"></div>
          
          <div className="relative z-10 max-w-2xl mx-auto">
            <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
              Ready to supercharge your career?
            </h2>
            <p className="text-[var(--primary-soft)] text-lg mb-10">
              Join thousands of students who are building their future with the power of UniOS. Start for free today.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/register" className="w-full sm:w-auto px-8 py-4 bg-[var(--surface)] text-[var(--primary)] hover:bg-[var(--surface-alt)] font-bold rounded-xl transition-all shadow-lg hover:-translate-y-0.5">
                Get Started for Free
              </Link>
            </div>
          </div>
        </div>
      </section>

    </main>
  );
}