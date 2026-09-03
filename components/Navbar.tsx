'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavbarProps {
  isLoggedIn?: boolean; 
}

export default function Navbar({ isLoggedIn = false }: NavbarProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  return (
    <nav className="sticky top-0 z-50 w-full bg-[var(--surface)]/90 backdrop-blur-md border-b border-[var(--border)] font-inter">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
          <div className="flex-shrink-0 flex items-center">
            <Link href="/">
              <img className="h-7 w-auto" src="/logo.svg" alt="UniOS.ai" />
            </Link>
          </div>

          <div className="hidden md:flex md:items-center md:space-x-8">
            {!isLoggedIn ? (
              <>
                <Link href="#product" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors">Product</Link>
                <Link href="#solutions" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors">Solutions</Link>
                <Link href="#resources" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors">Resources</Link>
                <Link href="#pricing" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors">Pricing</Link>
              </>
            ) : (
              <>
                <Link href="/dashboard" className={`text-sm font-medium transition-colors ${isActive('/dashboard') ? 'text-[var(--primary)]' : 'text-[var(--text-secondary)] hover:text-[var(--primary)]'}`}>Dashboard</Link>
                <Link href="/roadmaps" className={`text-sm font-medium transition-colors ${isActive('/roadmaps') ? 'text-[var(--primary)]' : 'text-[var(--text-secondary)] hover:text-[var(--primary)]'}`}>Roadmaps</Link>
                <Link href="/projects" className={`text-sm font-medium transition-colors ${isActive('/projects') ? 'text-[var(--primary)]' : 'text-[var(--text-secondary)] hover:text-[var(--primary)]'}`}>Projects</Link>
                <Link href="/jobs" className={`text-sm font-medium transition-colors ${isActive('/jobs') ? 'text-[var(--primary)]' : 'text-[var(--text-secondary)] hover:text-[var(--primary)]'}`}>Jobs</Link>
              </>
            )}
          </div>

          <div className="hidden md:flex items-center space-x-4">
            {!isLoggedIn ? (
              <>
                <Link href="/login" className="text-sm font-semibold text-[var(--text-primary)] hover:text-[var(--primary)] transition-colors">
                  Log in
                </Link>
                <Link href="/register" className="text-sm font-semibold bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white px-5 py-2.5 rounded-xl transition-all shadow-[0_4px_14px_0_var(--primary-shadow)] hover:-translate-y-0.5">
                  Get Started Free
                </Link>
              </>
            ) : (
              <>
                <button className="p-2 text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors relative">
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
                  <span className="absolute top-2 right-2 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-white"></span>
                </button>
                <div className="w-9 h-9 rounded-full bg-[var(--surface-muted)] border-2 border-[var(--surface)] shadow-sm overflow-hidden cursor-pointer">
                  <img src="https://i.pravatar.cc/150?img=11" alt="Profile" className="w-full h-full object-cover" />
                </div>
              </>
            )}
          </div>

          <div className="flex items-center md:hidden">
            <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="text-[var(--text-muted)] p-2">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {isMobileMenuOpen ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /> : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {isMobileMenuOpen && (
        <div className="md:hidden bg-[var(--surface)] border-t border-[var(--border)] p-4 absolute w-full shadow-lg">
          <div className="flex flex-col space-y-4">
            {!isLoggedIn ? (
              <>
                <Link href="#product" className="text-base font-medium text-[var(--text-primary)]">Product</Link>
                <Link href="#pricing" className="text-base font-medium text-[var(--text-primary)]">Pricing</Link>
                <div className="h-px bg-[var(--border)] my-2"></div>
                <Link href="/login" className="text-base font-semibold text-[var(--text-primary)]">Log in</Link>
                <Link href="/register" className="text-base text-center font-semibold bg-[var(--primary)] text-white px-5 py-3 rounded-xl">Get Started Free</Link>
              </>
            ) : (
              <>
                <Link href="/dashboard" className="text-base font-medium text-[var(--text-primary)]">Dashboard</Link>
                <Link href="/roadmaps" className="text-base font-medium text-[var(--text-primary)]">Roadmaps</Link>
                <div className="h-px bg-[var(--border)] my-2"></div>
                <button className="text-left text-base font-semibold text-[var(--danger)]">Sign Out</button>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}