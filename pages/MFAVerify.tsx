'use client';

import { API_URL } from '@/lib/api';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface MFAVerifyResponse {
  session?: {
    access_token?: string;
    refresh_token?: string;
    expires_in?: number;
    token_type?: string;
  };
  detail?: string;
  message?: string;
}

export default function MFAVerify() {
  const router = useRouter();

  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleCodeChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 6);

    setCode(value);

    if (error) {
      setError('');
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();

    if (code.length !== 6) {
      setError('Please enter the 6-digit verification code.');
      return;
    }

    const userId = sessionStorage.getItem('mfa_user_id');
    const accessToken = sessionStorage.getItem('mfa_access_token');

    if (!userId || !accessToken) {
      setError(
        'Your MFA session has expired. Please sign in again.'
      );
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(
        `${API_URL}/api/v1/auth/mfa/verify`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            user_id: userId,
            totp_code: code,
          }),
        }
      );

      const data: MFAVerifyResponse = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : typeof data.message === 'string'
              ? data.message
              : 'Invalid verification code.'
        );
      }

      /*
       * MFA successfully verified.
       *
       * Store the final authenticated session returned
       * by the backend for the current frontend architecture.
       */
      if (data.session?.access_token) {
        sessionStorage.setItem(
          'access_token',
          data.session.access_token
        );
      }

      if (data.session?.refresh_token) {
        sessionStorage.setItem(
          'refresh_token',
          data.session.refresh_token
        );
      }

      /*
       * Temporary MFA credentials are no longer needed.
       */
      sessionStorage.removeItem('mfa_user_id');
      sessionStorage.removeItem('mfa_access_token');

      router.push('/dashboard');
    } catch (err) {
      console.error('MFA verification failed:', err);

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to verify MFA code. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="min-h-screen flex items-center justify-center bg-slate-50 p-4 sm:p-8 font-inter">
      <div className="w-full max-w-[520px] bg-white rounded-[24px] shadow-sm border border-slate-200 p-8 sm:p-12">

        {/* Logo */}
        <div className="flex justify-center mb-8">
          <img
            src="/logo.svg"
            alt="UniOS.ai"
            className="h-8 w-auto"
          />
        </div>

        {/* Icon */}
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 rounded-2xl bg-indigo-50 flex items-center justify-center">
            <svg
              className="w-8 h-8 text-indigo-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.7}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v2h8z"
              />
            </svg>
          </div>
        </div>

        {/* Heading */}
        <div className="text-center mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-3">
            Two-Factor Authentication
          </h1>

          <p className="text-sm text-slate-500 leading-relaxed">
            Enter the 6-digit code from your authenticator app
            to continue.
          </p>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-3.5 bg-red-50 border border-red-100 rounded-xl">
            <p className="text-sm font-medium text-red-700">
              {error}
            </p>
          </div>
        )}

        {/* MFA Form */}
        <form onSubmit={handleVerify} className="space-y-6">

          <div>
            <label
              htmlFor="mfa-code"
              className="block text-sm font-medium text-slate-700 mb-2"
            >
              Authentication Code
            </label>

            <input
              id="mfa-code"
              name="mfa-code"
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              value={code}
              onChange={handleCodeChange}
              placeholder="000000"
              className="w-full px-4 py-3 rounded-xl border border-slate-200 text-center text-xl tracking-[0.5em] font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition-colors"
              autoFocus
            />

            <p className="mt-2 text-xs text-slate-400 text-center">
              Open Google Authenticator or your TOTP app to get your code.
            </p>
          </div>

          <button
            type="submit"
            disabled={isLoading || code.length !== 6}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed flex justify-center items-center shadow-[0_4px_14px_0_rgba(79,70,229,0.25)]"
          >
            {isLoading ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />

                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>

                Verifying...
              </>
            ) : (
              'Verify & Continue'
            )}
          </button>
        </form>

        {/* Back */}
        <div className="mt-8 text-center">
          <Link
            href="/login"
            className="text-sm font-semibold text-indigo-600 hover:text-indigo-700 transition-colors"
          >
            Back to Sign In
          </Link>
        </div>

        <p className="text-center text-xs text-slate-400 mt-6">
          Having trouble with your authenticator code? Make sure the
          device time is synchronized.
        </p>
      </div>
    </section>
  );
}