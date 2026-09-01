
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { API_URL } from '@/lib/api';

export default function ResetPassword() {
  const searchParams = useSearchParams();
  const resetToken = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const passwordRegex =
    /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setError('');
    setSuccess('');

    if (!resetToken) {
      setError('Invalid or missing password reset token.');
      return;
    }

    if (!password) {
      setError('Password is required.');
      return;
    }

    if (!passwordRegex.test(password)) {
      setError(
        'Password must contain at least 8 characters, 1 uppercase letter, 1 number, and 1 special character.'
      );
      return;
    }

    if (!confirmPassword) {
      setError('Please confirm your password.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/api/v1/auth/reset-password`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            reset_token: resetToken,
            new_password: password,
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
              : 'Unable to reset password.'
        );
      }

      setSuccess(
        'Your password has been reset successfully. You can now sign in with your new password.'
      );

      setPassword('');
      setConfirmPassword('');
    } catch (error) {
      console.error('Password reset failed:', error);

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
            Reset Password
          </h1>

          <p className="text-sm text-gray-500 leading-relaxed">
            Create a new password for your UniOS.ai account.
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
        {success ? (
          <div>
            <div
              role="status"
              className="mb-6 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700"
            >
              {success}
            </div>

            <Link
              href="/login"
              className="w-full bg-[#6366F1] hover:bg-indigo-600 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 flex justify-center items-center"
            >
              Back to Sign In
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">

            {/** Password */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-1.5"
              >
                New Password
              </label>

              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setError('');
                  }}
                  placeholder="••••••••"
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-[#6366F1] transition-colors pr-10"
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>

              <p className="mt-1.5 text-xs text-gray-500">
                Minimum 8 characters with 1 uppercase letter, 1 number, and 1 special character.
              </p>
            </div>

            {/** Confirm Password */}
            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-gray-700 mb-1.5"
              >
                Confirm Password
              </label>

              <div className="relative">
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  autoComplete="new-password"
                  value={confirmPassword}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value);
                    setError('');
                  }}
                  placeholder="••••••••"
                  className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-[#6366F1] transition-colors pr-10"
                />

                <button
                  type="button"
                  onClick={() =>
                    setShowConfirmPassword(!showConfirmPassword)
                  }
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
                  aria-label={
                    showConfirmPassword
                      ? 'Hide password'
                      : 'Show password'
                  }
                >
                  {showConfirmPassword ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>

            {/** Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-[#6366F1] hover:bg-indigo-600 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center shadow-[0_4px_14px_0_rgba(99,102,241,0.39)]"
            >
              {isLoading ? 'Resetting Password...' : 'Reset Password'}
            </button>
          </form>
        )}

        {/** Back to login */}
        {!success && (
          <div className="mt-8 text-center">
            <Link
              href="/login"
              className="text-sm font-semibold text-[#6366F1] hover:text-indigo-600 transition-colors"
            >
              Back to Sign In
            </Link>
          </div>
        )}
      </div>
    </section>
  );
}
