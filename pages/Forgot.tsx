
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
            Enter your email address and we&apos;ll
            send you a link to reset your password.
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

        <form
          onSubmit={handleSubmit(
            handleSubmitForm,
            handleInvalid
          )}
          className="space-y-5"
        >
          {/** Email */}
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700 mb-1.5"
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
              className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-[#6366F1] transition-colors ${
                errors.email
                  ? 'border-red-300'
                  : 'border-gray-200'
              }`}
            />
          </div>

          {/** Submit */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-[#6366F1] hover:bg-indigo-600 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center shadow-[0_4px_14px_0_rgba(99,102,241,0.39)]"
          >
            {isLoading
              ? 'Sending...'
              : 'Send Reset Link'}
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
