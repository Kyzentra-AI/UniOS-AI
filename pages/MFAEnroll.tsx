'use client';

import { useRouter } from 'next/navigation';

export default function MFAChoice() {
  const router = useRouter();

  const handleSetupMFA = () => {
    router.push('/mfa-setup');
  };

  const handleSkipMFA = () => {
    router.push('/dashboard');
  };

  return (
    <section className="min-h-screen flex items-center justify-center bg-[var(--auth-bg)] p-4 sm:p-8 font-inter">
      <div className="w-full max-w-[520px] bg-[var(--surface)] rounded-[24px] shadow-sm border border-[var(--border)] p-8 sm:p-12">

        {/* Header */}
        <div className="text-center mb-8">
          <img
            className="h-8 w-auto mx-auto mb-8"
            src="/logo.svg"
            alt="UniOS.ai"
          />

          <div className="mx-auto mb-5 w-14 h-14 rounded-2xl bg-[var(--primary-soft)] flex items-center justify-center">
            <svg
              className="w-7 h-7 text-[var(--primary)]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.7}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-7a2 2 0 00-2-2H6a2 2 0 00-2 2v7a2 2 0 002 2zm10-11V7a4 4 0 10-8 0v1"
              />
            </svg>
          </div>

          <h1 className="text-2xl sm:text-3xl font-bold text-[var(--text-primary)] mb-3">
            Secure your account
          </h1>

          <p className="text-sm leading-6 text-[var(--text-secondary)] max-w-md mx-auto">
            Add an authenticator app to protect your UniOS.ai account
            with an extra layer of security.
          </p>
        </div>

        {/* Benefits */}
        <div className="space-y-3 mb-8">
          <div className="flex items-start gap-3 p-4 rounded-xl bg-[var(--surface-muted)] border border-[var(--border)]">
            <div className="mt-0.5 shrink-0">
              <svg
                className="w-5 h-5 text-[var(--primary)]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.8}
                 
                 
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 3c-2.96 0-5.67 1.072-7.76 2.848A11.953 11.953 0 003 12c0 5.523 4.477 10 10 10s10-4.477 10-10c0-2.206-.714-4.245-1.938-5.922"
                />
              </svg>
            </div>

            <div>
              <p className="text-sm font-semibold text-[var(--text-primary)]">
                Extra account protection
              </p>
              <p className="text-xs text-[var(--text-secondary)] mt-1">
                Protect your account even if your password is compromised.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 rounded-xl bg-[var(--surface-muted)] border border-[var(--border)]">
            <div className="mt-0.5 shrink-0">
              <svg
                className="w-5 h-5 text-[var(--primary)]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.8}
                  
                  d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H6a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
            </div>

            <div>
              <p className="text-sm font-semibold text-[var(--text-primary)]">
                Use your authenticator app
              </p>
              <p className="text-xs text-[var(--text-secondary)] mt-1">
                Works with apps such as Google Authenticator and Authy.
              </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-3">
          <button
            type="button"
            onClick={handleSetupMFA}
            className="w-full bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 shadow-[0_4px_14px_0_var(--primary-shadow)]"
          >
            Set up authenticator
          </button>

          <button
            type="button"
            onClick={handleSkipMFA}
            className="w-full bg-transparent hover:bg-[var(--surface-muted)] text-[var(--text-secondary)] font-medium py-3 px-4 rounded-xl border border-[var(--border)] transition-colors"
          >
            Skip for now
          </button>
        </div>

        <p className="text-center text-xs text-[var(--text-muted)] mt-6">
          You can enable MFA later from your account security settings.
        </p>
      </div>
    </section>
  );
}