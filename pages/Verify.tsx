'use client';
import { API_URL } from '@/lib/api';
import { useState } from 'react';
import Link from 'next/link';

interface VerifyProps {
  email?: string;
}

export default function Verify({ email = '' }: VerifyProps) {
  const [isResending, setIsResending] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleResend = async () => {
    if (!email) {
      setError('Email address is missing. Please register again.');
      return;
    }

    setIsResending(true);
    setMessage('');
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/resend-verification`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to resend verification email.');
      }

      setMessage(
        data.message || 'Verification email sent successfully. Please check your inbox.'
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to resend verification email. Please try again.'
      );
    } finally {
      setIsResending(false);
    }
  };

  return (
    <section className="min-h-screen flex items-center justify-center bg-[#eae9e5] p-4 sm:p-8 font-inter">
      <div className="w-full max-w-[520px] bg-white rounded-[24px] shadow-sm border border-gray-100 p-8 sm:p-12">

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
               
                d="M3 8l9 6 9-6M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
        </div>

        {/* Heading */}
        <div className="text-center mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-3">
            Check your email
          </h1>

          <p className="text-sm text-gray-500 leading-relaxed">
            We&apos;ve sent a verification link to
          </p>

          {email ? (
            <p className="text-sm font-semibold text-gray-800 mt-1 break-all">
              {email}
            </p>
          ) : (
            <p className="text-sm font-semibold text-gray-800 mt-1">
              your email address
            </p>
          )}
        </div>

        {/* Info */}
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-3">
            <svg
              className="w-5 h-5 text-slate-400 shrink-0 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.7}
                d="M13 16h-1v-4h-1m1-4h.01M12 22a10 10 0 100-20 10 10 0 000 20z"
              />
            </svg>

            <p className="text-xs text-slate-500 leading-relaxed">
              Open the verification link in your email to activate your
              account. If you don&apos;t see it, check your spam or junk
              folder.
            </p>
          </div>
        </div>

        {/* Success */}
        {message && (
          <div className="mb-5 p-3.5 bg-green-50 border border-green-100 rounded-xl">
            <p className="text-sm font-medium text-green-700">
              {message}
            </p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mb-5 p-3.5 bg-red-50 border border-red-100 rounded-xl">
            <p className="text-sm font-medium text-red-700">
              {error}
            </p>
          </div>
        )}

        {/* Resend */}
        <button
          type="button"
          onClick={handleResend}
          disabled={isResending || !email}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed flex justify-center items-center shadow-[0_4px_14px_0_rgba(79,70,229,0.25)]"
        >
          {isResending ? (
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
              Sending...
            </>
          ) : (
            'Resend Verification Email'
          )}
        </button>

        {/* Login */}
        <div className="mt-6 text-center">
          <Link
            href="/login"
            className="text-sm font-semibold text-indigo-600 hover:text-indigo-700 transition-colors"
          >
            Back to Sign In
          </Link>
        </div>

        {/* Help */}
        <p className="text-center text-xs text-gray-400 mt-8">
          Didn&apos;t receive the email? Make sure the address is correct and
          check your spam folder.
        </p>
      </div>
    </section>
  );
}