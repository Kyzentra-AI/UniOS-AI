import React from 'react';
import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="w-full bg-[var(--surface)] font-inter overflow-hidden flex-grow">
      
      {/* 1. HERO SECTION */}
      <section className="relative pt-20 pb-16 md:pt-32 md:pb-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center">
        
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--primary-soft)] border border-[var(--border)] text-[var(--primary)] text-xs font-semibold mb-6">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--primary)] opacity-50"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--primary)]"></span>
          </span>
          UniOS v2.0 is now live
        </div>
        
        <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-[var(--text-primary)] tracking-tight mb-6 max-w-4xl mx-auto leading-tight">
          The Unified OS for <br className="hidden md:block" />
          <span className="text-[var(--primary)]">Future-Ready Students</span>
        </h1>
        
        <p className="text-base md:text-lg text-[var(--text-secondary)] mb-10 max-w-2xl mx-auto leading-relaxed">
          UniOS integrates project management, internship tracking, and personalized roadmaps into one AI-powered workspace. Built for high-performers.
        </p>
        
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link href="/register" className="w-full sm:w-auto px-8 py-4 bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white font-semibold rounded-xl transition-all shadow-[0_4px_14px_0_var(--primary-shadow)] hover:-translate-y-0.5">
            Start Your Journey
          </Link>
          <button className="w-full sm:w-auto px-8 py-4 bg-[var(--surface)] border border-[var(--border)] hover:bg-[var(--surface-alt)] text-[var(--text-primary)] font-semibold rounded-xl transition-all flex items-center justify-center gap-2">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            Watch Demo
          </button>
        </div>
      </section>

      {/* 2. TRUSTED BY LOGOS */}
      <section className="py-10 border-y border-[var(--border)] bg-[var(--surface-alt)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-xs font-bold text-[var(--text-muted)] tracking-widest uppercase mb-8">
            Trusted by over 50,000 students from elite institutions
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 md:gap-16 opacity-60 grayscale text-[var(--text-secondary)]">
            <svg className="h-6" viewBox="0 0 100 30" fill="currentColor"><text x="0" y="22" fontSize="24" fontWeight="bold">Google</text></svg>
            <svg className="h-6" viewBox="0 0 100 30" fill="currentColor"><text x="0" y="22" fontSize="24" fontWeight="bold">Microsoft</text></svg>
            <svg className="h-6" viewBox="0 0 100 30" fill="currentColor"><text x="0" y="22" fontSize="24" fontWeight="bold">Apple</text></svg>
            <svg className="h-6" viewBox="0 0 100 30" fill="currentColor"><text x="0" y="22" fontSize="24" fontWeight="bold">Amazon</text></svg>
            <svg className="h-6 hidden md:block" viewBox="0 0 100 30" fill="currentColor"><text x="0" y="22" fontSize="24" fontWeight="bold">Meta</text></svg>
          </div>
        </div>
      </section>

      {/* 3. ANALYTICS SHOWCASE */}
      <section className="py-20 md:py-32 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="flex flex-col lg:flex-row items-center gap-16">
          <div className="w-full lg:w-1/2 space-y-8">
            <div>
              <span className="text-[var(--primary)] font-semibold tracking-wider text-sm uppercase">Platform Preview</span>
              <h2 className="text-3xl md:text-4xl font-bold text-[var(--text-primary)] mt-2 mb-4">
                Master your metrics with <br /> Advanced Analytics.
              </h2>
              <p className="text-[var(--text-secondary)] leading-relaxed">
                See exactly how you'll grow. Once inside, our integrated dashboard provides real-time insights into your skill acquisition, project velocity, and internship success rates.
              </p>
            </div>

            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="w-10 h-10 rounded-lg bg-[var(--primary-soft)] flex items-center justify-center shrink-0">
                  <svg className="w-5 h-5 text-[var(--primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
                </div>
                <div>
                  <h4 className="text-lg font-bold text-[var(--text-primary)]">Progress Forecasting</h4>
                  <p className="text-sm text-[var(--text-secondary)] mt-1">AI predicts when you'll be job-ready based on current learning velocity.</p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="w-10 h-10 rounded-lg bg-[var(--feature-purple-soft)] flex items-center justify-center shrink-0">
                  <svg className="w-5 h-5 text-[var(--feature-purple)]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                </div>
                <div>
                  <h4 className="text-lg font-bold text-[var(--text-primary)]">Skill Gap Analysis</h4>
                  <p className="text-sm text-[var(--text-secondary)] mt-1">Compare your skills against top tech requirements to see what's missing.</p>
                </div>
              </div>
            </div>
          </div>

          <div className="w-full lg:w-1/2 relative">
            <div className="bg-[var(--surface)] rounded-2xl border border-[var(--border)] p-6 md:p-8 relative transform transition-transform hover:-translate-y-2 duration-500 shadow-sm hover:shadow-md">
              <div className="flex justify-between items-center mb-8">
                <h5 className="font-bold text-[var(--text-primary)]">Your Activity Preview</h5>
                <span className="text-xs font-semibold bg-[var(--primary-soft)] text-[var(--primary)] px-2.5 py-1 rounded-md">Top 5% Trajectory</span>
              </div>
              <div className="flex items-end justify-between gap-2 h-48 mb-6 border-b border-[var(--border)] pb-2">
                {[40, 70, 45, 90, 65, 80, 55].map((height, i) => (
                  <div key={i} className="w-full flex flex-col justify-end group">
                    <div 
                      className="w-full bg-[var(--primary)] rounded-t-md transition-all duration-500 hover:bg-[var(--primary-hover)] relative"
                      style={{ height: `${height}%` }}
                    >
                    </div>
                  </div>
                ))}
              </div>
              <div className="flex justify-between text-[10px] text-[var(--text-muted)] font-medium px-1">
                <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. FEATURES GRID */}
      <section className="py-20 bg-[var(--surface-muted)] border-t border-[var(--border)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--text-primary)] mb-4">
              Everything you need to <span className="text-[var(--primary)]">accelerate your career.</span>
            </h2>
            <p className="text-[var(--text-secondary)] text-lg">
              A comprehensive ecosystem designed to manage your academic journey and professional growth in one place.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-[var(--surface)] rounded-3xl p-8 border border-[var(--border)] shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-2xl bg-[var(--feature-purple-soft)] flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-[var(--feature-purple)]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
              </div>
              <h3 className="text-xl font-bold text-[var(--text-primary)] mb-3">AI Study Partner</h3>
              <p className="text-[var(--text-secondary)] text-sm mb-6 leading-relaxed">
                Personalized roadmap generator that adapts to your learning pace and professional goals.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-[var(--surface)] rounded-3xl p-8 border border-[var(--border)] shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-2xl bg-[var(--feature-orange-soft)] flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-[var(--feature-orange)]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
              </div>
              <h3 className="text-xl font-bold text-[var(--text-primary)] mb-3">Career Pipeline</h3>
              <p className="text-[var(--text-secondary)] text-sm mb-6 leading-relaxed">
                Curated internship listings and application tracking system to land your dream role.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-[var(--surface)] rounded-3xl p-8 border border-[var(--border)] shadow-sm hover:shadow-md transition-shadow">
              <div className="w-12 h-12 rounded-2xl bg-[var(--feature-blue-soft)] flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-[var(--feature-blue)]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
              </div>
              <h3 className="text-xl font-bold text-[var(--text-primary)] mb-3">Collaborative Lab</h3>
              <p className="text-[var(--text-secondary)] text-sm mb-6 leading-relaxed">
                Manage student projects, share feedback, and build a portfolio that stands out to recruiters.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. STATS SECTION */}
      <section className="py-16 border-y border-[var(--border)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center divide-x divide-[var(--border)]">
            <div>
              <div className="text-3xl md:text-4xl font-black text-[var(--text-primary)] mb-2">92%</div>
              <div className="text-xs text-[var(--text-muted)] font-medium uppercase tracking-wider">Placements within 6mo</div>
            </div>
            <div>
              <div className="text-3xl md:text-4xl font-black text-[var(--text-primary)] mb-2">500+</div>
              <div className="text-xs text-[var(--text-muted)] font-medium uppercase tracking-wider">Partner Companies</div>
            </div>
            <div>
              <div className="text-3xl md:text-4xl font-black text-[var(--text-primary)] mb-2">1.2M</div>
              <div className="text-xs text-[var(--text-muted)] font-medium uppercase tracking-wider">Tasks Completed</div>
            </div>
            <div>
              <div className="text-3xl md:text-4xl font-black text-[var(--text-primary)] mb-2">4.9/5</div>
              <div className="text-xs text-[var(--text-muted)] font-medium uppercase tracking-wider">User Satisfaction</div>
            </div>
          </div>
        </div>
      </section>

      {/* 6. TESTIMONIALS SECTION */}
      <section className="py-24 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-12">
          <span className="text-[var(--primary)] font-semibold tracking-wider text-sm uppercase">Success Stories</span>
          <h2 className="text-3xl md:text-4xl font-bold text-[var(--text-primary)] mt-2">
            Built by students, <br /> for the future of work.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-[var(--surface)] p-8 rounded-3xl shadow-sm border border-[var(--border)]">
            <p className="text-[var(--text-secondary)] text-sm leading-relaxed mb-6">
              "UniOS transformed how I approach my engineering projects. The AI roadmap actually understood my goals and provided resources I couldn't find anywhere else."
            </p>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[var(--surface-muted)] overflow-hidden">
                <img src="https://i.pravatar.cc/150?img=47" alt="Sarah Chen" className="w-full h-full object-cover" />
              </div>
              <div>
                <h4 className="font-bold text-[var(--text-primary)] text-sm">Sarah Chen</h4>
                <p className="text-xs text-[var(--text-muted)]">CS Student at Stanford</p>
              </div>
            </div>
          </div>

          <div className="bg-[var(--surface)] p-8 rounded-3xl shadow-sm border border-[var(--border)]">
            <p className="text-[var(--text-secondary)] text-sm leading-relaxed mb-6">
              "Managing internship applications used to be a nightmare. Now I have a centralized hub that tracks everything and gives me feedback on my CV in real-time."
            </p>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[var(--surface-muted)] overflow-hidden">
                <img src="https://i.pravatar.cc/150?img=11" alt="Marcus Rodriguez" className="w-full h-full object-cover" />
              </div>
              <div>
                <h4 className="font-bold text-[var(--text-primary)] text-sm">Marcus Rodriguez</h4>
                <p className="text-xs text-[var(--text-muted)]">Software Eng. Intern</p>
              </div>
            </div>
          </div>

          <div className="bg-[var(--surface)] p-8 rounded-3xl shadow-sm border border-[var(--border)]">
            <p className="text-[var(--text-secondary)] text-sm leading-relaxed mb-6">
              "The best tool for student teams. We built our entire final year project using UniOS labs. The collaborative features are smoother than any Enterprise tool we tried."
            </p>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[var(--surface-muted)] overflow-hidden">
                <img src="https://i.pravatar.cc/150?img=5" alt="Laila Ahmed" className="w-full h-full object-cover" />
              </div>
              <div>
                <h4 className="font-bold text-[var(--text-primary)] text-sm">Laila Ahmed</h4>
                <p className="text-xs text-[var(--text-muted)]">Design at NYU</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 7. CTA BANNER */}
      <section className="pb-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="bg-[var(--primary)] rounded-[40px] p-12 md:p-20 text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
          
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

    </div>
  );
}