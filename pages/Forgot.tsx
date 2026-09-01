
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { API_URL } from '@/lib/api';

export default function Forgot() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setError('');
    setSuccess('');

    const trimmedEmail = email.trim();

    if (!trimmedEmail) {
      setError('Email address is required');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(trimmedEmail)) {
      setError('Please enter a valid email address');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/v1/auth/forgot-password`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: trimmedEmail,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : typeof data.message === 'string'
              ? data.message
              : 'Unable to send password reset link.'
        );
      }

      setSuccess(
        'If an account exists with this email, a password reset link has been sent.'
      );
    } catch (error) {
      console.error('Forgot password failed:', error);

      setError(
        error instanceof Error
          ? error.message
          : 'Something went wrong. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="min-h-screen flex items-center justify-center bg-[#eae9e5] p-4 sm:p-8 font-inter">
      <div className="w-full max-w-[480px] bg-white rounded-[24px] shadow-sm border border-gray-100 p-8 sm:p-12">

        {/** Header */}
        <div className="mb-8">
          <img
            className="h-8 w-auto mb-6"
            src="/logo.svg"
            alt="UniOS.ai"
          />

          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Forgot Password?
          </h1>

          <p className="text-sm text-gray-500 leading-relaxed">
            Enter your email address and we'll send you a link to reset your password.
          </p>
        </div>

        {/** Error */}
        {error && (
          <div
            role="alert"
            className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600"
          >
            {error}
          </div>
        )}

        {/** Success */}
        {success && (
          <div
            role="status"
            className="mb-5 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700"
          >
            {success}
          </div>
        )}

        {/** Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700 mb-1.5"
            >
              Email Address
            </label>

            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                setError('');
                setSuccess('');
              }}
              placeholder="name@university.edu"
              className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-[#6366F1] transition-colors ${
                error ? 'border-red-500' : 'border-gray-200'
              }`}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-[#6366F1] hover:bg-indigo-600 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center shadow-[0_4px_14px_0_rgba(99,102,241,0.39)]"
          >
            {isLoading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>

        {/** Back to login */}
        <div className="mt-8 text-center">
          <Link
            href="/login"
            className="text-sm font-semibold text-[#6366F1] hover:text-indigo-600 transition-colors"
          >
            Back to Sign In
          </Link>
        </div>
      </div>
    </section>
  );
}
