import React from 'react';
import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-[var(--surface)] border-t border-[var(--border)] pt-16 pb-8 font-inter">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 mb-16">
          <div className="lg:col-span-2">
            <Link href="/">
              <img className="h-8 w-auto mb-6" src="/logo.svg" alt="UniOS.ai" />
            </Link>
            <p className="text-sm text-[var(--text-secondary)] leading-relaxed mb-6 max-w-xs">
              Empowering the next generation of professionals with AI-driven academic and career management tools. Built for performance.
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-[var(--text-primary)] mb-5 text-sm">Product</h4>
            <ul className="space-y-4 text-sm text-[var(--text-secondary)]">
              <li><Link href="#" className="hover:text-[var(--primary)] transition-colors">AI Roadmaps</Link></li>
              <li><Link href="#" className="hover:text-[var(--primary)] transition-colors">Internship Hub</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-[var(--text-primary)] mb-5 text-sm">Resources</h4>
            <ul className="space-y-4 text-sm text-[var(--text-secondary)]">
              <li><Link href="#" className="hover:text-[var(--primary)] transition-colors">Documentation</Link></li>
              <li><Link href="#" className="hover:text-[var(--primary)] transition-colors">Community</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-[var(--text-primary)] mb-5 text-sm">Company</h4>
            <ul className="space-y-4 text-sm text-[var(--text-secondary)]">
              <li><Link href="#" className="hover:text-[var(--primary)] transition-colors">About Us</Link></li>
              <li><Link href="#" className="hover:text-[var(--primary)] transition-colors">Privacy Policy</Link></li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-[var(--border)] flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-xs text-[var(--text-muted)]">
            © 2026 UniOS Technologies Inc. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}