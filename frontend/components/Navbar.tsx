
'use client';

import { useCallback, useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

import { getSession, logout } from '@/lib/auth';

const HIDDEN_ROUTES = [
  '/login',
  '/register',
  '/mfa-verify',
  '/mfa-enroll',
  '/mfa-setup',
  '/reset-password',
  '/forgot-password',
  '/verify-email',
  '/onboarding',
  '/syllabus',
];

const PUBLIC_LINKS = [
  { label: 'Product', href: '/#product' },
  { label: 'Solutions', href: '/#solutions' },
  { label: 'Resources', href: '/#resources' },
  { label: 'Pricing', href: '/billing' },
];

const AUTH_LINKS = [
  { label: 'Dashboard', href: '/dashboard' },
  { label: 'Roadmap', href: '/roadmap' },
  { label: 'Build', href: '/build' },
  { label: 'Launch', href: '/launch' },
  { label: 'Compete', href: '/compete' },
];

interface JwtPayload {
  email?: string;
  name?: string;
  full_name?: string;
  user_metadata?: {
    name?: string;
    full_name?: string;
    email?: string;
  };
}

function getAvatarInitials(token: string | null): string {
  if (!token) return 'U';

  try {
    const payloadPart = token.split('.')[1];

    if (!payloadPart) return 'U';

    const base64 = payloadPart
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const decoded = atob(
      base64.padEnd(Math.ceil(base64.length / 4) * 4, '=')
    );

    const payload = JSON.parse(decoded) as JwtPayload;

    const name =
      payload.user_metadata?.full_name ||
      payload.user_metadata?.name ||
      payload.full_name ||
      payload.name;

    if (name?.trim()) {
      const parts = name.trim().split(/\s+/);

      return parts.length > 1
        ? `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
        : parts[0].slice(0, 2).toUpperCase();
    }

    const email =
      payload.user_metadata?.email || payload.email;

    return email?.trim()
      ? email.trim()[0].toUpperCase()
      : 'U';
  } catch {
    return 'U';
  }
}

export default function Navbar() {
  const pathname = usePathname() ?? '';
  const router = useRouter();

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [avatarInitials, setAvatarInitials] = useState('U');

  const syncAuthState = useCallback(() => {
    const session = getSession();
    const token = session?.access_token || null;

    setIsLoggedIn(Boolean(token));
    setAvatarInitials(getAvatarInitials(token));
  }, []);

  useEffect(() => {
    syncAuthState();

    window.addEventListener('auth-change', syncAuthState);

    return () => {
      window.removeEventListener('auth-change', syncAuthState);
    };
  }, [syncAuthState]);

  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [pathname]);

  const handleLogout = async () => {
    if (isLoggingOut) return;

    setIsLoggingOut(true);

    try {
      await logout();
    } finally {
      setIsLoggedIn(false);
      setAvatarInitials('U');
      setIsMobileMenuOpen(false);
      router.replace('/login');
      setIsLoggingOut(false);
    }
  };

  const hideNavbar = HIDDEN_ROUTES.some(
    (route) =>
      pathname === route || pathname.startsWith(`${route}/`)
  );

  if (hideNavbar) return null;

  const linkClass = (href: string) =>
    `text-sm font-medium transition-colors ${
      pathname === href
        ? 'text-[var(--primary)]'
        : 'text-[var(--text-secondary)] hover:text-[var(--primary)]'
    }`;

  return (
    <header className="sticky top-0 z-50 w-full border-b border-[var(--border)] bg-[var(--surface)] text-[var(--foreground)] shadow-sm">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Logo */}
        <Link
          href={isLoggedIn ? '/dashboard' : '/'}
          className="flex shrink-0 items-center"
          aria-label="UniOS.AI home"
        >
          <Image
            src="/logo.svg"
            alt="UniOS.AI"
            width={120}
            height={150}
            priority
            className="h-16 w-auto"
          />
        </Link>

        {/* Desktop navigation */}
        <div className="hidden items-center gap-7 md:flex">
          {(isLoggedIn ? AUTH_LINKS : PUBLIC_LINKS).map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className={linkClass(item.href)}
            >
              {item.label}
            </Link>
          ))}
        </div>

        {/* Desktop actions */}
        <div className="hidden items-center gap-3 md:flex">
          {isLoggedIn ? (
            <>
              <Link
                href="/memory"
                aria-label="Open profile"
                title="Profile"
                className="flex h-10 w-10 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--primary-soft)] text-sm font-semibold text-[var(--primary)] transition hover:border-[var(--primary)]"
              >
                {avatarInitials}
              </Link>

              <button
                type="button"
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm font-semibold text-[var(--primary)] transition hover:bg-[var(--primary-soft)] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isLoggingOut ? 'Signing out...' : 'Sign Out'}
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="px-3 py-2 text-sm font-semibold text-[var(--text-secondary)] transition hover:text-[var(--primary)]"
              >
                Log In
              </Link>

              <Link
                href="/register"
                className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-semibold text-[var(--surface)] transition hover:bg-[var(--primary-hover)]"
              >
                Get Started
              </Link>
            </>
          )}
        </div>

        {/* Mobile menu toggle */}
        <button
          type="button"
          aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={isMobileMenuOpen}
          onClick={() => setIsMobileMenuOpen((open) => !open)}
          className="flex h-10 w-10 items-center justify-center rounded-lg text-[var(--primary)] transition hover:bg-[var(--primary-soft)] md:hidden"
        >
          {isMobileMenuOpen ? (
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="h-6 w-6"
              aria-hidden="true"
            >
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          ) : (
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="h-6 w-6"
              aria-hidden="true"
            >
              <path d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          )}
        </button>
      </nav>

      {/* Mobile navigation */}
      {isMobileMenuOpen && (
        <div className="border-t border-[var(--border)] bg-[var(--surface)] px-4 py-4 shadow-md md:hidden">
          <div className="flex flex-col gap-1">
            {(isLoggedIn ? AUTH_LINKS : PUBLIC_LINKS).map((item) => (
              <Link
                key={item.label}
                href={item.href}
                onClick={() => setIsMobileMenuOpen(false)}
                className="rounded-lg px-3 py-3 text-sm font-medium text-[var(--text-secondary)] transition hover:bg-[var(--primary-soft)] hover:text-[var(--primary)]"
              >
                {item.label}
              </Link>
            ))}

            <div className="my-2 border-t border-[var(--border)]" />

            {isLoggedIn ? (
              <>
                <Link
                  href="/memory"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium text-[var(--foreground)] transition hover:bg-[var(--primary-soft)]"
                >
                  <span className="flex h-9 w-9 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--primary-soft)] font-semibold text-[var(--primary)]">
                    {avatarInitials}
                  </span>
                  Profile
                </Link>

                <button
                  type="button"
                  onClick={handleLogout}
                  disabled={isLoggingOut}
                  className="rounded-lg px-3 py-3 text-left text-sm font-semibold text-[var(--danger-text)] transition hover:bg-[var(--danger-soft)] disabled:opacity-60"
                >
                  {isLoggingOut ? 'Signing out...' : 'Sign Out'}
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="rounded-lg px-3 py-3 text-sm font-medium text-[var(--text-secondary)] transition hover:bg-[var(--primary-soft)]"
                >
                  Log In
                </Link>

                <Link
                  href="/register"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="rounded-lg bg-[var(--primary)] px-3 py-3 text-center text-sm font-semibold text-[var(--surface)] transition hover:bg-[var(--primary-hover)]"
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
