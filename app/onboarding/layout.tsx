'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';

const steps = [
  {
    id: 1,
    name: 'Education',
    path: '/onboarding/education',
  },
  {
    id: 2,
    name: 'Career Goals',
    path: '/onboarding/career-goals',
  },
  {
    id: 3,
    name: 'Skills',
    path: '/onboarding/skills',
  },
  {
    id: 4,
    name: 'Preferences',
    path: '/onboarding/preferences',
  },
  {
    id: 5,
    name: 'Profile',
    path: '/onboarding/profile',
  },
  {
    id: 6,
    name: 'First Mission',
    path: '/onboarding/first-mission',
  },
];

export default function OnboardingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

const currentStep =
  steps.find((step) => pathname?.startsWith(step.path))?.id ?? 1;

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--text-primary)]">
      {/* Onboarding Header */}
      <header className="border-b border-[var(--border)] bg-[var(--surface)]">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          {/* Logo */}
          <Link href="/" className="flex items-center">
            <Image
              src="/logo.svg"
              alt="UniOS"
              width={60}
              height={20}
              priority
              className="h-7 w-auto"
            />
          </Link>

          {/* Desktop Progress */}
          <div className="hidden items-center md:flex">
            {steps.map((step, index) => {
              const isCurrent = step.id === currentStep;
              const isCompleted = step.id < currentStep;

              return (
                <div key={step.id} className="flex items-center">
                  {/* Step */}
                  <div className="flex items-center gap-2">
                    <div
                      className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold transition-colors ${
                        isCurrent || isCompleted
                          ? 'bg-[var(--primary)] text-white'
                          : 'bg-[var(--surface-muted)] text-[var(--text-muted)]'
                      }`}
                    >
                      {step.id}
                    </div>

                    <span
                      className={`whitespace-nowrap text-sm font-medium ${
                        isCurrent
                          ? 'text-[var(--text-primary)]'
                          : isCompleted
                            ? 'text-[var(--primary)]'
                            : 'text-[var(--text-muted)]'
                      }`}
                    >
                      {step.name}
                    </span>
                  </div>

                  {/* Connector */}
                  {index < steps.length - 1 && (
                    <div
                      className={`mx-3 h-px w-8 ${
                        step.id < currentStep
                          ? 'bg-[var(--primary)]'
                          : 'bg-[var(--border)]'
                      }`}
                    />
                  )}
                </div>
              );
            })}
          </div>

          {/* Mobile Progress */}
          <div className="text-sm font-medium text-[var(--text-secondary)] md:hidden">
            Step {currentStep} of {steps.length}
          </div>
        </div>
      </header>

      {/* Page Content */}
      <main>{children}</main>
    </div>
  );
}