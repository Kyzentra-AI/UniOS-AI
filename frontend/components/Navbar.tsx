
'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Sun, Moon } from 'lucide-react';
import { getSession, logout } from '@/lib/auth';
import { useTheme } from '@/components/providers/ThemeProvider';

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

const AUTH_LINKS = [
  { label: 'Dashboard', href: '/dashboard' },
  { label: 'Roadmap', href: '/roadmap' },
  { label: 'Build', href: '/build' },
  { label: 'Launch', href: '/launch' },
];

const PUBLIC_MENUS = [
  {
    label: 'Product',
    items: [
      { label: 'AI Study Assistant', href: '/ai-study-assistant' },
      { label: 'Study Resources', href: '/study-resources' },
      { label: 'Smart Study Roadmap', href: '/roadmap' },
      { label: 'Projects & Workspace', href: '/build' },
      { label: 'Career Guidance', href: '/career-guidance' },
      { label: 'Internship Tracker', href: '/internships' },
      { label: 'Coding Workspace', href: '/coding-workspace' },
    ],
  },
  {
    label: 'Solutions',
    items: [
      { label: 'For University Students', href: '/solutions/university-students' },
      { label: 'For Exam Preparation', href: '/solutions/exam-preparation' },
      {
        label: 'For Career & Internship Readiness',
        href: '/solutions/career-readiness',
      },
    ],
  },
  {
    label: 'Resources',
    items: [
      { label: 'Blog', href: '/blog' },
      { label: 'Study Guides', href: '/study-guides' },
      { label: 'Career Guides', href: '/career-guides' },
      { label: 'FAQs', href: '/faqs' },
    ],
  },
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

    const base64 = payloadPart.replace(/-/g, '+').replace(/_/g, '/');
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

    const email = payload.user_metadata?.email || payload.email;
    return email?.trim() ? email.trim()[0].toUpperCase() : 'U';
  } catch {
    return 'U';
  }
}

function Chevron({ open }: { open: boolean }) {
  return (
    <svg
      viewBox="0 0 20 20"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      className={`h-3.5 w-3.5 transition-transform duration-200 ${
        open ? 'rotate-180' : ''
      }`}
      aria-hidden="true"
    >
      <path
        d="m5 7.5 5 5 5-5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function ThemeToggle() {
  const { theme, toggleTheme, mounted } = useTheme();

  if (!mounted) {
    return <div className="h-10 w-10 shrink-0" aria-hidden="true" />;
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
      className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] text-[var(--text-primary)] transition-all duration-200 hover:border-[var(--primary)] hover:bg-[var(--primary-soft)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
    >
      {theme === 'light' ? (
        <Moon size={19} />
      ) : (
        <Sun size={19} />
      )}
    </button>
  );
}

export default function Navbar() {
  const pathname = usePathname() ?? '';
  const router = useRouter();
  const navRef = useRef<HTMLElement>(null);

  const { theme } = useTheme();

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [avatarInitials, setAvatarInitials] = useState('U');
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const [openMobileSection, setOpenMobileSection] = useState<string | null>(
    null
  );

  const syncAuthState = useCallback(() => {
    const token = getSession()?.access_token || null;
    setIsLoggedIn(Boolean(token));
    setAvatarInitials(getAvatarInitials(token));
  }, []);

  useEffect(() => {
    syncAuthState();

    window.addEventListener('auth-change', syncAuthState);
    return () => window.removeEventListener('auth-change', syncAuthState);
  }, [syncAuthState]);

  useEffect(() => {
    setIsMobileMenuOpen(false);
    setOpenDropdown(null);
    setOpenMobileSection(null);
  }, [pathname]);

  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent) => {
      if (
        navRef.current &&
        !navRef.current.contains(event.target as Node)
      ) {
        setOpenDropdown(null);
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpenDropdown(null);
        setOpenMobileSection(null);
        setIsMobileMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleOutsideClick);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
      document.removeEventListener('keydown', handleEscape);
    };
  }, []);

  const closeMenus = () => {
    setIsMobileMenuOpen(false);
    setOpenDropdown(null);
    setOpenMobileSection(null);
  };

  const handleLogout = async () => {
    if (isLoggingOut) return;

    setIsLoggingOut(true);

    try {
      await logout();
    } finally {
      setIsLoggedIn(false);
      setAvatarInitials('U');
      closeMenus();
      router.replace('/login');
      setIsLoggingOut(false);
    }
  };

  const hideNavbar = HIDDEN_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  );

  if (hideNavbar) return null;

  const linkClass = (href: string) =>
    `text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] ${
      pathname === href || (href !== '/' && pathname.startsWith(`${href}/`))
        ? 'text-[var(--primary)]'
        : 'text-[var(--text-secondary)] hover:text-[var(--primary)]'
    }`;

  return (
    <header className="sticky top-0 z-50 w-full border-b border-[var(--border)] bg-[var(--surface)] text-[var(--foreground)] shadow-sm">
      <nav
        ref={navRef}
        aria-label="Main navigation"
        className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8"
      >
        {/* Logo */}
        <Link
          href={isLoggedIn ? '/dashboard' : '/'}
          onClick={closeMenus}
          aria-label="UniOS.AI home"
          className="flex shrink-0 items-center"
        >
          <Image
            src={theme === "dark" ? "/logo1.png" : "/logo.png"}
            alt="UniOS.AI"
            width={120}
            height={150}
            priority
            className="h-16 w-auto"
          />
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden items-center gap-6 md:flex">
          {isLoggedIn ? (
            AUTH_LINKS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={linkClass(item.href)}
              >
                {item.label}
              </Link>
            ))
          ) : (
            <>
              {PUBLIC_MENUS.map((menu) => {
                const isOpen = openDropdown === menu.label;

                return (
                  <div
                    key={menu.label}
                    className="relative"
                    onMouseEnter={() => setOpenDropdown(menu.label)}
                    onMouseLeave={() => setOpenDropdown(null)}
                  >
                    <button
                      type="button"
                      aria-expanded={isOpen}
                      onClick={() =>
                        setOpenDropdown((current) =>
                          current === menu.label ? null : menu.label
                        )
                      }
                      className={`flex items-center gap-1.5 rounded-md py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] ${
                        isOpen
                          ? 'text-[var(--primary)]'
                          : 'text-[var(--text-secondary)] hover:text-[var(--primary)]'
                      }`}
                    >
                      {menu.label}
                      <Chevron open={isOpen} />
                    </button>

                    {isOpen && (
                      <div className="absolute left-1/2 top-full z-50 w-64 -translate-x-1/2 pt-2">
                        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-2 shadow-lg">
                          {menu.items.map((item) => (
                            <Link
                              key={item.href}
                              href={item.href}
                              onClick={closeMenus}
                              className="block rounded-lg px-3 py-2.5 text-sm text-[var(--text-secondary)] transition-colors hover:bg-[var(--primary-soft)] hover:text-[var(--primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                            >
                              {item.label}
                            </Link>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}

              <Link href="/billing" className={linkClass('/billing')}>
                Pricing
              </Link>
            </>
          )}
        </div>

        {/* Desktop Actions */}
        <div className="hidden shrink-0 items-center gap-3 md:flex">
          <ThemeToggle />

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
                className="rounded-lg border border-[var(--border)] px-4 py-2 text-sm font-semibold text-[var(--primary)] transition hover:bg-[var(--primary-soft)] disabled:opacity-60"
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

        {/* Mobile Header Actions */}
        <div className="flex items-center gap-2 md:hidden">
          <ThemeToggle />

          <button
            type="button"
            aria-label={isMobileMenuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={isMobileMenuOpen}
            onClick={() => setIsMobileMenuOpen((open) => !open)}
            className="flex h-10 w-10 items-center justify-center rounded-lg text-[var(--primary)] transition hover:bg-[var(--primary-soft)]"
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
        </div>
      </nav>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="border-t border-[var(--border)] bg-[var(--surface)] px-4 py-4 shadow-md md:hidden">
          <div className="mx-auto flex max-w-7xl flex-col gap-1">

            {/* Appearance */}
            <div className="mb-2 flex items-center justify-between rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] px-3 py-2">
              <div>
                <p className="text-sm font-semibold text-[var(--text-primary)]">
                  Appearance
                </p>
                <p className="text-xs text-[var(--text-secondary)]">
                  {theme === 'light' ? 'Light mode' : 'Dark mode'}
                </p>
              </div>

              <ThemeToggle />
            </div>

            {isLoggedIn ? (
              AUTH_LINKS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={closeMenus}
                  className={`rounded-lg px-3 py-3 ${linkClass(item.href)}`}
                >
                  {item.label}
                </Link>
              ))
            ) : (
              <>
                {PUBLIC_MENUS.map((menu) => {
                  const isOpen = openMobileSection === menu.label;

                  return (
                    <section
                      key={menu.label}
                      className="border-b border-[var(--border)] last:border-0"
                    >
                      <button
                        type="button"
                        aria-expanded={isOpen}
                        onClick={() =>
                          setOpenMobileSection((current) =>
                            current === menu.label ? null : menu.label
                          )
                        }
                        className="flex w-full items-center justify-between rounded-lg px-3 py-3 text-left text-sm font-semibold text-[var(--foreground)] transition hover:bg-[var(--primary-soft)]"
                      >
                        {menu.label}
                        <Chevron open={isOpen} />
                      </button>

                      {isOpen && (
                        <div className="pb-2 pl-2">
                          {menu.items.map((item) => (
                            <Link
                              key={item.href}
                              href={item.href}
                              onClick={closeMenus}
                              className="block rounded-lg px-3 py-2.5 text-sm text-[var(--text-secondary)] transition hover:bg-[var(--primary-soft)] hover:text-[var(--primary)]"
                            >
                              {item.label}
                            </Link>
                          ))}
                        </div>
                      )}
                    </section>
                  );
                })}

                <Link
                  href="/billing"
                  onClick={closeMenus}
                  className={`rounded-lg px-3 py-3 ${linkClass('/billing')}`}
                >
                  Pricing
                </Link>
              </>
            )}

            <div className="my-2 border-t border-[var(--border)]" />

            {isLoggedIn ? (
              <>
                <Link
                  href="/memory"
                  onClick={closeMenus}
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
                  onClick={closeMenus}
                  className="rounded-lg px-3 py-3 text-sm font-semibold text-[var(--text-secondary)] transition hover:bg-[var(--primary-soft)]"
                >
                  Log In
                </Link>

                <Link
                  href="/register"
                  onClick={closeMenus}
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
