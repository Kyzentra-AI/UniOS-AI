
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

import { useMutation } from '@tanstack/react-query';

import {
  useForm,
  type FieldErrors,
} from 'react-hook-form';

import { zodResolver } from '@hookform/resolvers/zod';

import { resetPassword } from '@/lib/api';

import {
  resetPasswordSchema,
  type ResetPasswordFormData,
} from '@/app/validations/auth';

export default function ResetPassword() {
  const [resetToken, setResetToken] =
    useState<string | null>(null);

  const [showPassword, setShowPassword] =
    useState(false);

  const [
    showConfirmPassword,
    setShowConfirmPassword,
  ] = useState(false);

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const hash = window.location.hash;

    if (!hash) {
      setError(
        'Invalid or missing password reset link.'
      );
      return;
    }

    const params = new URLSearchParams(
      hash.substring(1)
    );

    const accessToken =
      params.get('access_token');

    const recoveryError =
      params.get('error_description');

    if (recoveryError) {
      setError(
        decodeURIComponent(
          recoveryError.replace(/\+/g, ' ')
        )
      );
      return;
    }

    if (!accessToken) {
      setError(
        'Invalid or missing password reset link.'
      );
      return;
    }

    setResetToken(accessToken);
  }, []);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(
      resetPasswordSchema
    ),
    mode: 'onChange',
    defaultValues: {
      password: '',
      confirmPassword: '',
    },
  });

  const resetPasswordMutation =
    useMutation({
      mutationFn: resetPassword,

      onSuccess: () => {
        setError('');

        setSuccess(
          'Your password has been reset successfully. You can now sign in with your new password.'
        );

        setResetToken(null);

        window.history.replaceState(
          null,
          '',
          window.location.pathname
        );

        reset();
      },

      onError: (error) => {
        setSuccess('');

        setError(
          error instanceof Error
            ? error.message
            : 'Something went wrong. Please try again.'
        );
      },
    });

  const handleSubmitForm = (
    formData: ResetPasswordFormData
  ) => {
    setError('');
    setSuccess('');

    if (!resetToken) {
      setError(
        'Invalid or missing password reset link.'
      );
      return;
    }

    resetPasswordMutation.mutate({
      access_token: resetToken,
      new_password: formData.password,
    });
  };

  const handleInvalid = (
    formErrors: FieldErrors<ResetPasswordFormData>
  ) => {
    setSuccess('');

    setError(
      formErrors.password?.message ||
        formErrors.confirmPassword?.message ||
        'Please check your password details.'
    );
  };

  const isLoading =
    resetPasswordMutation.isPending;

  return (
    <section className="min-h-screen flex items-center justify-center bg-[var(--surface-alt)] p-4 sm:p-8 font-inter">
      <div className="w-full max-w-[480px] bg-[var(--surface)] rounded-[24px] shadow-sm border border-[var(--border)] p-8 sm:p-12">

        {/* Header */}
        <div className="mb-8">
          <img
            className="h-8 w-auto mb-6"
            src="/logo.svg"
            alt="UniOS.ai"
          />

          <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">
            Reset Password
          </h1>

          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
            Create a new password for your UniOS.ai account.
          </p>
        </div>

        {/* Error */}
        {error && (
          <div
            role="alert"
            className="mb-5 rounded-xl border border-[var(--danger-border)] bg-[var(--danger-soft)] px-4 py-3 text-sm text-[var(--danger-text)]"
          >
            {error}
          </div>
        )}

        {/* Success */}
        {success ? (
          <div>
            <div
              role="status"
              className="mb-6 rounded-xl border border-[var(--border)] bg-[var(--primary-soft)] px-4 py-3 text-sm text-[var(--text-primary)]"
            >
              {success}
            </div>

            <Link
              href="/login"
              className="w-full bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 flex justify-center items-center"
            >
              Back to Sign In
            </Link>
          </div>
        ) : (
          <form
            onSubmit={handleSubmit(
              handleSubmitForm,
              handleInvalid
            )}
            className="space-y-5"
          >

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-[var(--text-label)] mb-1.5"
              >
                New Password
              </label>

              <div className="relative">
                <input
                  id="password"
                  type={
                    showPassword
                      ? 'text'
                      : 'password'
                  }
                  autoComplete="new-password"
                  {...register('password', {
                    onChange: () => {
                      setError('');
                      setSuccess('');
                    },
                  })}
                  placeholder="••••••••"
                  className={`w-full px-4 py-2.5 rounded-xl border bg-[var(--surface)] text-[var(--text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/20 focus:border-[var(--primary)] transition-colors pr-10 ${
                    errors.password
                      ? 'border-[var(--danger-border)]'
                      : 'border-[var(--border)]'
                  }`}
                />

                <button
                  type="button"
                  onClick={() =>
                    setShowPassword(
                      !showPassword
                    )
                  }
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                  aria-label={
                    showPassword
                      ? 'Hide password'
                      : 'Show password'
                  }
                >
                  {showPassword
                    ? 'Hide'
                    : 'Show'}
                </button>
              </div>

              <p className="mt-1.5 text-xs text-[var(--text-muted)]">
                Minimum 8 characters with 1 uppercase letter, 1 number, and 1 special character.
              </p>
            </div>

            {/* Confirm Password */}
            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-[var(--text-label)] mb-1.5"
              >
                Confirm Password
              </label>

              <div className="relative">
                <input
                  id="confirmPassword"
                  type={
                    showConfirmPassword
                      ? 'text'
                      : 'password'
                  }
                  autoComplete="new-password"
                  {...register(
                    'confirmPassword',
                    {
                      onChange: () => {
                        setError('');
                        setSuccess('');
                      },
                    }
                  )}
                  placeholder="••••••••"
                  className={`w-full px-4 py-2.5 rounded-xl border bg-[var(--surface)] text-[var(--text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/20 focus:border-[var(--primary)] transition-colors pr-10 ${
                    errors.confirmPassword
                      ? 'border-[var(--danger-border)]'
                      : 'border-[var(--border)]'
                  }`}
                />

                <button
                  type="button"
                  onClick={() =>
                    setShowConfirmPassword(
                      !showConfirmPassword
                    )
                  }
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                  aria-label={
                    showConfirmPassword
                      ? 'Hide password'
                      : 'Show password'
                  }
                >
                  {showConfirmPassword
                    ? 'Hide'
                    : 'Show'}
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center shadow-[0_4px_14px_var(--primary-shadow)]"
            >
              {isLoading
                ? 'Resetting Password...'
                : 'Reset Password'}
            </button>
          </form>
        )}

        {/* Back to login */}
        {!success && (
          <div className="mt-8 text-center">
            <Link
              href="/login"
              className="text-sm font-semibold text-[var(--primary)] hover:text-[var(--primary-hover)] transition-colors"
            >
              Back to Sign In
            </Link>
          </div>
        )}
      </div>
    </section>
  );
}
