'use client';

import { useState } from 'react';
import Link from 'next/link';
import { API_URL } from '@/lib/api';

interface RegisterFormData {
  full_name: string;
  email: string;
  password: string;
  terms_accepted: boolean;
}

export default function Register() {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    termsAccepted: false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const passwordRegex =
    /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!formData.email || !emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (!passwordRegex.test(formData.password)) {
      newErrors.password =
        'Min 8 chars, 1 uppercase, 1 number, 1 special character';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (!formData.termsAccepted) {
      newErrors.termsAccepted =
        'You must accept the terms and conditions';
    }

    setErrors(newErrors);

    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));

    // Clear API error when user starts editing again
    if (apiError) {
      setApiError('');
    }

    setErrors((prev) => {
      const updatedErrors = { ...prev };

      if (name === 'password') {
        if (!value) {
          updatedErrors.password = 'Password is required';
        } else if (!passwordRegex.test(value)) {
          updatedErrors.password =
            'Min 8 chars, 1 uppercase, 1 number, 1 special character';
        } else {
          delete updatedErrors.password;
        }

        // Re-check confirm password whenever password changes
        if (formData.confirmPassword) {
          if (value !== formData.confirmPassword) {
            updatedErrors.confirmPassword = 'Passwords do not match';
          } else {
            delete updatedErrors.confirmPassword;
          }
        }
      }

      if (name === 'confirmPassword') {
        if (!value) {
          delete updatedErrors.confirmPassword;
        } else if (value !== formData.password) {
          updatedErrors.confirmPassword = 'Passwords do not match';
        } else {
          delete updatedErrors.confirmPassword;
        }
      }

      if (name === 'fullName') {
        if (value.trim()) {
          delete updatedErrors.fullName;
        } else {
          updatedErrors.fullName = 'Full name is required';
        }
      }

      if (name === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (value && emailRegex.test(value)) {
          delete updatedErrors.email;
        } else if (value) {
          updatedErrors.email = 'Please enter a valid email address';
        } else {
          delete updatedErrors.email;
        }
      }

      if (name === 'termsAccepted' && checked) {
        delete updatedErrors.termsAccepted;
      }

      return updatedErrors;
    });
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    setApiError('');

    if (!validateForm()) return;

    setIsLoading(true);

    const apiPayload: RegisterFormData = {
      full_name: formData.fullName,
      email: formData.email,
      password: formData.password,
      terms_accepted: formData.termsAccepted,
    };

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/register`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(apiPayload),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Registration failed. Please try again.'
        );
      }

      console.log('Registration successful:', data);
      window.location.href = `/verify-email?email=${encodeURIComponent(
  formData.email
)}`;

      // Redirect will be added after confirming backend response.
      // router.push('/login');

    } catch (error) {
      console.error('Registration failed:', error);

      setApiError(
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
      <div className="w-full max-w-[1040px] bg-white rounded-[24px] shadow-sm border border-gray-100 flex flex-col md:flex-row overflow-hidden">

        {/* Left Column: Registration Form */}
        <div className="w-full md:w-3/5 p-8 sm:p-12 lg:p-14 z-10 bg-white">

          <div className="mb-8">
            <img
              className="h-8 w-auto mb-6"
              src="/logo.svg"
              alt="UniOS.ai"
            />

            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Create Account
            </h1>

            <h2 className="text-sm text-gray-500">
              Join the all-in-one workspace for students.
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
            <button
              type="button"
              className="flex justify-center items-center gap-2 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
            >
              <img
                src="https://www.svgrepo.com/show/475656/google-color.svg"
                alt="Google"
                className="w-5 h-5"
              />
              <span className="text-sm font-semibold text-gray-700">
                Google
              </span>
            </button>

            <button
              type="button"
              className="flex justify-center items-center gap-2 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
            >
              <img
                src="https://www.svgrepo.com/show/475647/facebook-color.svg"
                alt="Facebook"
                className="w-5 h-5"
              />
              <span className="text-sm font-semibold text-gray-700">
                Facebook
              </span>
            </button>

            <button
              type="button"
              className="flex justify-center items-center gap-2 py-2.5 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
            >
              <img
                src="https://www.svgrepo.com/show/512317/github-142.svg"
                alt="GitHub"
                className="w-5 h-5"
              />
              <span className="text-sm font-semibold text-gray-700">
                GitHub
              </span>
            </button>
          </div>

          <div className="relative flex items-center py-2 mb-6">
            <div className="flex-grow border-t border-gray-200"></div>

            <span className="flex-shrink-0 mx-4 text-xs font-medium text-gray-400 tracking-wider uppercase">
              Or Email
            </span>

            <div className="flex-grow border-t border-gray-200"></div>
          </div>

          {/* API Error */}
          {apiError && (
            <div
              role="alert"
              className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600"
            >
              {apiError}
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-4">

            {/* Full Name */}
            <div>
              <label
                className="block text-sm font-medium text-gray-700 mb-1.5"
                htmlFor="fullName"
              >
                Full Name
              </label>

              <input
                id="fullName"
                name="fullName"
                type="text"
                value={formData.fullName}
                onChange={handleChange}
                placeholder="e.g. Alex Johnson"
                className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-[#6366F1] transition-colors ${
                  errors.fullName
                    ? 'border-red-500'
                    : 'border-gray-200'
                }`}
              />

              {errors.fullName && (
                <p className="mt-1.5 text-xs text-red-500">
                  {errors.fullName}
                </p>
              )}
            </div>

            {/* Email */}
            <div>
              <label
                className="block text-sm font-medium text-gray-700 mb-1.5"
                htmlFor="email"
              >
                Email Address
              </label>

              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="name@university.edu"
                className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-[#6366F1] transition-colors ${
                  errors.email
                    ? 'border-red-500'
                    : 'border-gray-200'
                }`}
              />

              {errors.email && (
                <p className="mt-1.5 text-xs text-red-500">
                  {errors.email}
                </p>
              )}
            </div>

            {/* Password Fields */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

              {/* Password */}
              <div>
                <label
                  className="block text-sm font-medium text-gray-700 mb-1.5"
                  htmlFor="password"
                >
                  Password
                </label>

                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                    className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-[#6366F1] transition-colors pr-10 ${
                      errors.password
                        ? 'border-red-500'
                        : 'border-gray-200'
                    }`}
                  />

                  <button
                    type="button"
                    onClick={() =>
                      setShowPassword(!showPassword)
                    }
                    className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
                  >
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      {showPassword ? (
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                      ) : (
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                        />
                      )}
                    </svg>
                  </button>
                </div>

                {errors.password && (
                  <p className="mt-1.5 text-xs text-red-500 leading-tight">
                    {errors.password}
                  </p>
                )}
              </div>

              {/* Confirm Password */}
              <div>
                <label
                  className="block text-sm font-medium text-gray-700 mb-1.5"
                  htmlFor="confirmPassword"
                >
                  Confirm Password
                </label>

                <div className="relative">
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={
                      showConfirmPassword ? 'text' : 'password'
                    }
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="••••••••"
                    className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-[#6366F1] transition-colors pr-10 ${
                      errors.confirmPassword
                        ? 'border-red-500'
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
                  >
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      {showConfirmPassword ? (
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                      ) : (
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                        />
                      )}
                    </svg>
                  </button>
                </div>

                {errors.confirmPassword && (
                  <p className="mt-1.5 text-xs text-red-500 leading-tight">
                    {errors.confirmPassword}
                  </p>
                )}
              </div>
            </div>

            {/* Terms */}
            <div className="flex items-start pt-2">
              <div className="flex items-center h-5">
                <input
                  id="termsAccepted"
                  name="termsAccepted"
                  type="checkbox"
                  checked={formData.termsAccepted}
                  onChange={handleChange}
                  className="w-4 h-4 text-[#6366F1] bg-white border-gray-300 rounded focus:ring-[#6366F1] focus:ring-2 cursor-pointer"
                />
              </div>

              <div className="ml-2 text-sm">
                <label
                  htmlFor="termsAccepted"
                  className={`font-medium ${
                    errors.termsAccepted
                      ? 'text-red-500'
                      : 'text-gray-600'
                  } cursor-pointer`}
                >
                  I agree to the{' '}
                  <Link
                    href="/terms"
                    className="text-[#6366F1] hover:underline"
                  >
                    Terms of Service
                  </Link>{' '}
                  and{' '}
                  <Link
                    href="/privacy"
                    className="text-[#6366F1] hover:underline"
                  >
                    Privacy Policy
                  </Link>
                </label>
              </div>
            </div>

            {/* Submit */}
            <div className="pt-4">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-[#6366F1] hover:bg-indigo-600 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center shadow-[0_4px_14px_0_rgba(99,102,241,0.39)]"
              >
                {isLoading ? (
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
                ) : (
                  'Create Account'
                )}
              </button>
            </div>
          </form>

          <div className="mt-8 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link
                href="/login"
                className="font-semibold text-[#6366F1] hover:text-indigo-600 transition-colors"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>

        {/* Right Column */}
        <div className="hidden md:flex md:w-2/5 bg-[#F8F9FB] p-10 flex-col justify-center relative overflow-hidden border-l border-gray-100">

          <div className="relative z-10 w-full max-w-sm mx-auto">

            <div className="mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Everything you need.
              </h3>

              <p className="text-sm text-gray-500">
                Unlock the tools designed to help you build skills and land roles.
              </p>
            </div>

            <div className="space-y-4">

              {/* Feature 1 */}
              <div className="bg-white p-4 rounded-2xl shadow-[0_4px_20px_rgb(0,0,0,0.03)] border border-gray-100 flex items-start gap-4 transform transition-all duration-300 hover:-translate-y-1 hover:shadow-md">
                <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center text-purple-600 shrink-0">
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-gray-900 leading-tight">
                    AI Resume Scorer
                  </h4>

                  <p className="text-[12px] text-gray-500 mt-1 leading-snug">
                    Optimize your resume structure and keywords to beat the ATS.
                  </p>
                </div>
              </div>

              {/* Feature 2 */}
              <div className="bg-white p-4 rounded-2xl shadow-[0_4px_20px_rgb(0,0,0,0.03)] border border-gray-100 flex items-start gap-4 transform transition-all duration-300 hover:-translate-y-1 hover:shadow-md">
                <div className="w-10 h-10 rounded-xl bg-orange-50 flex items-center justify-center text-orange-500 shrink-0">
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                    />
                  </svg>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-gray-900 leading-tight">
                    Coding Roadmaps
                  </h4>

                  <p className="text-[12px] text-gray-500 mt-1 leading-snug">
                    Follow structured paths for DSA, Web Dev, and System Design.
                  </p>
                </div>
              </div>

              {/* Feature 3 */}
              <div className="bg-white p-4 rounded-2xl shadow-[0_4px_20px_rgb(0,0,0,0.03)] border border-gray-100 flex items-start gap-4 transform transition-all duration-300 hover:-translate-y-1 hover:shadow-md">
                <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-blue-500 shrink-0">
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 002 2v10a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-gray-900 leading-tight">
                    Smart Job Matches
                  </h4>

                  <p className="text-[12px] text-gray-500 mt-1 leading-snug">
                    Get curated internship and job opportunities based on your skills.
                  </p>
                </div>
              </div>

            </div>
          </div>

          {/* Subtle Background Elements */}
          <div className="absolute top-[5%] right-[-10%] w-[250px] h-[250px] bg-[#6366F1]/10 rounded-full blur-3xl pointer-events-none"></div>

          <div className="absolute bottom-[0%] left-[-10%] w-[200px] h-[200px] bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

        </div>

      </div>
    </section>
  );
}
