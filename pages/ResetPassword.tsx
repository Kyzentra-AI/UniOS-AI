
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';

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
  const searchParams =
    useSearchParams();

  const resetToken =
    searchParams.get('token');

  const [showPassword, setShowPassword] =
    useState(false);

  const [
    showConfirmPassword,
    setShowConfirmPassword,
  ] = useState(false);

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

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
        'Invalid or missing password reset token.'
      );
      return;
    }

    resetPasswordMutation.mutate({
      reset_token: resetToken,
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
          <form
            onSubmit={handleSubmit(
              handleSubmitForm,
              handleInvalid
            )}
            className="space-y-5"
          >

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
                  className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-[#6366F1] transition-colors pr-10 ${
                    errors.password
                      ? 'border-red-300'
                      : 'border-gray-200'
                  }`}
                />

                <button
                  type="button"
                  onClick={() =>
                    setShowPassword(
                      !showPassword
                    )
                  }
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
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
                  className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-[#6366F1] transition-colors pr-10 ${
                    errors.confirmPassword
                      ? 'border-red-300'
                      : 'border-gray-200'
                  }`}
                />

                <button
                  type="button"
                  onClick={() =>
                    setShowConfirmPassword(
                      !showConfirmPassword
                    )
                  }
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
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

            {/** Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-[#6366F1] hover:bg-indigo-600 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center shadow-[0_4px_14px_0_rgba(99,102,241,0.39)]"
            >
              {isLoading
                ? 'Resetting Password...'
                : 'Reset Password'}
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
