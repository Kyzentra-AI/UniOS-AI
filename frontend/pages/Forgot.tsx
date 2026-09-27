
'use client';

import { useState } from 'react';
import Link from 'next/link';

import { useMutation } from '@tanstack/react-query';

import {
  useForm,
  type FieldErrors,
} from 'react-hook-form';

import { zodResolver } from '@hookform/resolvers/zod';

import { forgotPassword } from '@/lib/api';

import {
  forgotPasswordSchema,
  type ForgotPasswordFormData,
} from '@/app/validations/auth';

export default function Forgot() {
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(
      forgotPasswordSchema
    ),
    mode: 'onChange',
    defaultValues: {
      email: '',
    },
  });

  const forgotPasswordMutation =
    useMutation({
      mutationFn: forgotPassword,

      onSuccess: () => {
        setError('');

        setSuccess(
          'If an account exists with this email, a password reset link has been sent.'
        );
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
    formData: ForgotPasswordFormData
  ) => {
    setError('');
    setSuccess('');

    forgotPasswordMutation.mutate({
      email: formData.email.trim(),
    });
  };

  const handleInvalid = (
    formErrors: FieldErrors<ForgotPasswordFormData>
  ) => {
    setSuccess('');

    setError(
      formErrors.email?.message ||
        'Please check your email address.'
    );
  };

  const isLoading =
    forgotPasswordMutation.isPending;

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
            Forgot Password?
          </h1>

          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
            Enter your email address and we&apos;ll
            send you a link to reset your password.
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
        {success && (
          <div
            role="status"
            className="mb-5 rounded-xl border border-[var(--border)] bg-[var(--primary-soft)] px-4 py-3 text-sm text-[var(--text-primary)]"
          >
            {success}
          </div>
        )}

        <form
          onSubmit={handleSubmit(
            handleSubmitForm,
            handleInvalid
          )}
          className="space-y-5"
        >
          {/* Email */}
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-[var(--text-label)] mb-1.5"
            >
              Email Address
            </label>

            <input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="name@university.edu"
              disabled={isLoading}
              {...register('email', {
                onChange: () => {
                  setError('');
                  setSuccess('');
                },
              })}
              className={`w-full px-4 py-2.5 rounded-xl border bg-[var(--surface)] text-[var(--text-primary)] text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/20 focus:border-[var(--primary)] transition-colors ${
                errors.email
                  ? 'border-[var(--danger-border)]'
                  : 'border-[var(--border)]'
              }`}
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center"
          >
            {isLoading
              ? 'Sending...'
              : 'Send Reset Link'}
          </button>
        </form>

        {/* Back to login */}
        <div className="mt-8 text-center">
          <Link
            href="/login"
            className="text-sm font-semibold text-[var(--primary)] hover:text-[var(--primary-hover)] transition-colors"
          >
            Back to Sign In
          </Link>
        </div>
      </div>
    </section>
  );
}
