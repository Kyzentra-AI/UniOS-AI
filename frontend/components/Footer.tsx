'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Footer() {
  const pathname = usePathname();

if (
  pathname &&
  (pathname === '/onboarding' || pathname.startsWith('/onboarding/'))
) {
  return null;
}
  return (
    <footer className="bg-[var(--surface)] border-t border-[var(--border)] pt-16 pb-8 font-inter">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Main Footer */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 mb-16">

          {/* Brand */}
          <div className="lg:col-span-2">
            <Link href="/" className="inline-block">
              <img
                className="h-8 w-auto mb-6"
                src="/logo.svg"
                alt="UniOS.ai"
              />
            </Link>

            <p className="text-sm text-[var(--text-secondary)] leading-relaxed mb-6 max-w-xs">
              Empowering the next generation of professionals with AI-driven
              academic and career management tools. Built for performance,
              designed for you.
            </p>

            {/* Social Links */}
            <div className="flex items-center gap-3">

              {/* Instagram */}
              <Link
                href="#"
                aria-label="Instagram"
                className="w-9 h-9 rounded-lg border border-[var(--border)] flex items-center justify-center text-[var(--text-secondary)] hover:text-[var(--primary)] hover:border-[var(--primary)] transition-colors"
              >
                <svg
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <rect x="3" y="3" width="18" height="18" rx="5" />
                  <circle cx="12" cy="12" r="4" />
                  <circle cx="17.5" cy="6.5" r="0.8" fill="currentColor" stroke="none" />
                </svg>
              </Link>

              {/* LinkedIn */}
              <Link
                href="#"
                aria-label="LinkedIn"
                className="w-9 h-9 rounded-lg border border-[var(--border)] flex items-center justify-center text-[var(--text-secondary)] hover:text-[var(--primary)] hover:border-[var(--primary)] transition-colors"
              >
                <svg
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M6.5 8.2H3.2V20h3.3V8.2ZM4.85 3C3.82 3 3 3.82 3 4.85S3.82 6.7 4.85 6.7 6.7 5.88 6.7 4.85 5.88 3 4.85 3ZM20.8 13.25c0-3.55-1.9-5.2-4.45-5.2-2.05 0-2.97 1.13-3.48 1.93V8.2H9.57V20h3.3v-5.83c0-1.54.29-3.03 2.2-3.03 1.88 0 1.9 1.76 1.9 3.13V20h3.3l.01-6.75Z" />
                </svg>
              </Link>

              {/* GitHub */}
              <Link
                href="#"
                aria-label="GitHub"
                className="w-9 h-9 rounded-lg border border-[var(--border)] flex items-center justify-center text-[var(--text-secondary)] hover:text-[var(--primary)] hover:border-[var(--primary)] transition-colors"
              >
                <svg
                  width="17"
                  height="17"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M12 2C6.48 2 2 6.58 2 12.25c0 4.52 2.87 8.35 6.84 9.7.5.1.68-.22.68-.49v-1.7c-2.78.62-3.37-1.2-3.37-1.2-.46-1.2-1.11-1.52-1.11-1.52-.91-.64.07-.63.07-.63 1.01.07 1.54 1.07 1.54 1.07.9 1.58 2.35 1.12 2.92.86.09-.67.35-1.12.63-1.38-2.22-.26-4.56-1.14-4.56-5.06 0-1.12.39-2.04 1.03-2.76-.1-.26-.45-1.3.1-2.71 0 0 .84-.28 2.75 1.05A9.2 9.2 0 0 1 12 7.15c.85 0 1.7.12 2.5.36 1.9-1.33 2.74-1.05 2.74-1.05.55 1.41.2 2.45.1 2.71.64.72 1.03 1.64 1.03 2.76 0 3.93-2.34 4.79-4.57 5.05.36.32.68.95.68 1.92v2.84c0 .28.18.6.69.49A10.25 10.25 0 0 0 22 12.25C22 6.58 17.52 2 12 2Z" />
                </svg>
              </Link>

              {/* X / Twitter */}
              <Link
                href="#"
                aria-label="X"
                className="w-9 h-9 rounded-lg border border-[var(--border)] flex items-center justify-center text-[var(--text-secondary)] hover:text-[var(--primary)] hover:border-[var(--primary)] transition-colors"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M18.9 2H22l-6.77 7.74L23.2 22h-6.24l-4.89-6.39L6.49 22H3.38l7.24-8.28L2.8 2h6.4l4.42 5.84L18.9 2Zm-1.1 17.85h1.73L8.28 4.02H6.42L17.8 19.85Z" />
                </svg>
              </Link>

            </div>
          </div>

          {/* Product */}
          <div>
            <h4 className="font-semibold text-[var(--text-primary)] mb-5 text-sm">
              Product
            </h4>

            <ul className="space-y-4 text-sm text-[var(--text-secondary)]">
              <li>
                <Link
                  href="#"
                  className="hover:text-[var(--primary)] transition-colors"
                >
                  AI Roadmaps
                </Link>
              </li>

              <li>
                <Link
                  href="#"
                  className="hover:text-[var(--primary)] transition-colors"
                >
                  Internship Hub
                </Link>
              </li>

              <li>
                <Link
                  href="#"
                  className="hover:text-[var(--primary)] transition-colors"
                >
                  Lab Workspace
                </Link>
              </li>

              <li>
                <Link
                  href="#"
                  className="hover:text-[var(--primary)] transition-colors"
                >
                  Integrations
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="font-semibold text-[var(--text-primary)] mb-5 text-sm">
              Resources
            </h4>

            <ul className="space-y-4 text-sm text-[var(--text-secondary)]">
              <li>
                <Link
                  href="#"
                  className="hover:text-[var(--primary)] transition-colors"
                >
                  Documentation
                </Link>
              </li>

              <li>
                <Link
                  href="#"
                  className="hover:text-[var(--primary)] transition-colors"
                >
                  Community
                </Link>
              </li>

              <li>
                <Link
                  href="#"
                  className="hover:text-[var(--primary)] transition-colors"
                >
                  Success Stories
                </Link>
              </li>

              <li>
                <Link
                  href="#"
                  className="hover:text-[var(--primary)] transition-colors"
                >
                  API Reference
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-semibold text-[var(--text-primary)] mb-5 text-sm">
              Company
            </h4>

            <ul className="space-y-4 text-sm text-[var(--text-secondary)]">
              <li>
                <Link
                  href="#"
                  className="hover:text-[var(--primary)] transition-colors"
                >
                  About Us
                </Link>
              </li>

              <li>
                <Link
                  href="#"
                  className="hover:text-[var(--primary)] transition-colors"
                >
                  Careers
                </Link>
              </li>

              <li>
                <Link
                  href="#"
                  className="hover:text-[var(--primary)] transition-colors"
                >
                  Privacy Policy
                </Link>
              </li>

              <li>
                <Link
                  href="#"
                  className="hover:text-[var(--primary)] transition-colors"
                >
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-[var(--border)] flex flex-col md:flex-row justify-between items-center gap-4">

          <p className="text-xs text-[var(--text-muted)]">
            © 2026 UniOS Technologies Inc. All rights reserved.
          </p>

          <div className="flex items-center gap-6 text-xs text-[var(--text-muted)]">
            <span>English (US)</span>

            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              Status: Healthy
            </span>
          </div>

        </div>

      </div>
    </footer>
  );
}
