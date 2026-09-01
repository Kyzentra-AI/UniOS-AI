'use client';

import { API_URL } from '@/lib/api';
import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { saveSession } from '@/lib/auth';

interface LoginFormData {
  email: string;
  password: string;
  remember_me: boolean;
}

interface LoginResponse {
  message?: string;
  detail?: string;
  access_token?: string;
  token?: string;
  requires_mfa?: boolean;
  user_id?: string;
  email_verified?: boolean;
  session?: {
    access_token?: string;
    refresh_token?: string;
    expires_in?: number;
    token_type?: string;
  };
}

export default function Login() {
  const router = useRouter();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [socialLoading, setSocialLoading] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!formData.email.trim()) {
      newErrors.email = 'Email address is required';
    } else if (!emailRegex.test(formData.email.trim())) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
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

    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }

    if (serverError) {
      setServerError(null);
    }
  };

  const handleSocialLogin = async (
    provider: 'google' | 'facebook' | 'github'
  ) => {
    setSocialLoading(provider);
    setServerError(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/social`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ provider }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Unable to start social login.'
        );
      }

      if (!data.url) {
        throw new Error('Social login URL was not returned by the server.');
      }

      window.location.href = data.url;
    } catch (error) {
      console.error(`${provider} login failed:`, error);

      setServerError(
        error instanceof Error
          ? error.message
          : 'Unable to start social login.'
      );

      setSocialLoading(null);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setServerError(null);

    const apiPayload: LoginFormData = {
      email: formData.email.trim(),
      password: formData.password,
      remember_me: formData.rememberMe,
    };

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiPayload),
      });

      const data: LoginResponse = await response.json();

      if (!response.ok) {
        const detail =
          typeof data.detail === 'string'
            ? data.detail
            : typeof data.message === 'string'
              ? data.message
              : 'Invalid email or password.';

        const normalizedDetail = detail.toLowerCase();

        if (
          normalizedDetail.includes('verify') ||
          normalizedDetail.includes('unverified') ||
          normalizedDetail.includes('email not verified')
        ) {
          router.push(
            `/verify-email?email=${encodeURIComponent(
              formData.email.trim()
            )}`
          );
          return;
        }

        setServerError(detail);
        return;
      }

      if (data.requires_mfa) {
        if (data.user_id) {
          sessionStorage.setItem('mfa_user_id', data.user_id);
        }

        const mfaAccessToken = data.session?.access_token;

        if (!mfaAccessToken) {
          setServerError(
            'MFA session could not be established. Please sign in again.'
          );
          return;
        }

        sessionStorage.setItem('mfa_access_token', mfaAccessToken);

        router.push('/mfa-verify');
        return;
      }

      if (data.session?.access_token) {
        saveSession(data.session, formData.rememberMe);
        router.push('/dashboard');
        return;
      }

      setServerError('Unable to sign in. Please try again.');
    } catch (error) {
      console.error('Login failed:', error);

      setServerError(
        'Unable to connect to the server. Please make sure the backend is running.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="min-h-screen flex items-center justify-center bg-slate-50 p-4 sm:p-8 font-inter">
      <div className="w-full max-w-[1040px] bg-white rounded-[24px] shadow-sm border border-slate-200 flex flex-col md:flex-row overflow-hidden">

        {/* Login Form */}
        <div className="w-full md:w-3/5 p-8 sm:p-12 lg:p-14 z-10 bg-white">
          <div className="mb-8">
            <img
              className="h-8 w-auto mb-6"
              src="/logo.svg"
              alt="UniOS.ai"
            />

            <h1 className="text-3xl font-bold text-slate-900 mb-2">
              Welcome back
            </h1>

            <h2 className="text-sm text-slate-500">
              Sign in to continue your academic journey.
            </h2>
          </div>

          {/* Social Login */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
            <button
              type="button"
              onClick={() => handleSocialLogin('google')}
              disabled={socialLoading !== null || isLoading}
              className="flex justify-center items-center gap-2 py-2.5 border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <img
                src="https://www.svgrepo.com/show/475656/google-color.svg"
                alt="Google"
                className="w-5 h-5"
              />

              <span className="text-sm font-semibold text-slate-700">
                {socialLoading === 'google' ? 'Connecting...' : 'Google'}
              </span>
            </button>

            <button
              type="button"
              onClick={() => handleSocialLogin('facebook')}
              disabled={socialLoading !== null || isLoading}
              className="flex justify-center items-center gap-2 py-2.5 border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <img
                src="https://www.svgrepo.com/show/475647/facebook-color.svg"
                alt="Facebook"
                className="w-5 h-5"
              />

              <span className="text-sm font-semibold text-slate-700">
                {socialLoading === 'facebook' ? 'Connecting...' : 'Facebook'}
              </span>
            </button>

            <button
              type="button"
              onClick={() => handleSocialLogin('github')}
              disabled={socialLoading !== null || isLoading}
              className="flex justify-center items-center gap-2 py-2.5 border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <img
                src="https://www.svgrepo.com/show/512317/github-142.svg"
                alt="GitHub"
                className="w-5 h-5"
              />

              <span className="text-sm font-semibold text-slate-700">
                {socialLoading === 'github' ? 'Connecting...' : 'GitHub'}
              </span>
            </button>
          </div>

          {/* Divider */}
          <div className="relative flex items-center py-2 mb-6">
            <div className="flex-grow border-t border-slate-200" />

            <span className="flex-shrink-0 mx-4 text-xs font-medium text-slate-400 tracking-wider uppercase">
              Or Email
            </span>

            <div className="flex-grow border-t border-slate-200" />
          </div>

          {/* Server Error */}
          {serverError && (
            <div className="mb-6 p-3.5 bg-red-50 border border-red-100 rounded-xl flex items-start gap-2.5">
              <svg
                className="w-5 h-5 text-red-500 shrink-0 mt-0.5"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l-1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>

              <p className="text-sm font-medium text-red-700">
                {serverError}
              </p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label
                className="block text-sm font-medium text-slate-700 mb-1.5"
                htmlFor="email"
              >
                Email Address
              </label>

              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="name@university.edu"
                className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition-colors ${
                  errors.email
                    ? 'border-red-500 bg-red-50/50'
                    : 'border-slate-200'
                }`}
              />

              {errors.email && (
                <p className="mt-1.5 text-xs text-red-500">
                  {errors.email}
                </p>
              )}
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label
                  className="block text-sm font-medium text-slate-700"
                  htmlFor="password"
                >
                  Password
                </label>

                <Link
                  href="/forgot-password"
                  className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 transition-colors"
                >
                  Forgot?
                </Link>
              </div>

              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  className={`w-full px-4 py-2.5 rounded-xl border text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition-colors pr-10 ${
                    errors.password
                      ? 'border-red-500 bg-red-50/50'
                      : 'border-slate-200'
                  }`}
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-600 focus:outline-none"
                  aria-label={
                    showPassword ? 'Hide password' : 'Show password'
                  }
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
                <p className="mt-1.5 text-xs text-red-500">
                  {errors.password}
                </p>
              )}
            </div>

            <div className="flex items-center pt-2">
              <input
                id="rememberMe"
                name="rememberMe"
                type="checkbox"
                checked={formData.rememberMe}
                onChange={handleChange}
                className="w-4 h-4 text-indigo-600 bg-white border-slate-300 rounded focus:ring-indigo-600 focus:ring-2 cursor-pointer"
              />

              <label
                htmlFor="rememberMe"
                className="ml-2 text-sm font-medium text-slate-600 cursor-pointer"
              >
                Keep me signed in
              </label>
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={isLoading || socialLoading !== null}
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center shadow-[0_4px_14px_0_rgba(79,70,229,0.39)]"
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

                    Signing in...
                  </>
                ) : (
                  'Sign In to Dashboard'
                )}
              </button>
            </div>
          </form>

          <div className="mt-8 text-center">
            <p className="text-sm text-slate-600">
              Don't have an account?{' '}

              <Link
                href="/register"
                className="font-semibold text-indigo-600 hover:text-indigo-700 transition-colors"
              >
                Start for free
              </Link>
            </p>
          </div>
        </div>

        {/* Platform Preview */}
        <div className="hidden md:flex md:w-2/5 bg-slate-100 p-10 flex-col justify-center relative overflow-hidden border-l border-slate-200">
          <div className="relative z-10 w-full max-w-sm mx-auto">
            <div className="mb-8">
              <h3 className="text-2xl font-bold text-slate-900 mb-2">
                Everything you need.
              </h3>

              <p className="text-sm text-slate-500">
                Access the tools designed to help you build skills and land
                roles.
              </p>
            </div>

            <div className="space-y-4">
              <div className="bg-white p-4 rounded-2xl shadow-[0_4px_20px_rgb(0,0,0,0.03)] border border-slate-200 flex items-start gap-4 transform transition-all duration-300 hover:-translate-y-1 hover:shadow-md">
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
                  <h4 className="text-sm font-bold text-slate-900 leading-tight">
                    AI Resume Scorer
                  </h4>

                  <p className="text-[12px] text-slate-500 mt-1 leading-snug">
                    Optimize your resume structure and keywords to beat the
                    ATS.
                  </p>
                </div>
              </div>

              <div className="bg-white p-4 rounded-2xl shadow-[0_4px_20px_rgb(0,0,0,0.03)] border border-slate-200 flex items-start gap-4 transform transition-all duration-300 hover:-translate-y-1 hover:shadow-md">
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
                  <h4 className="text-sm font-bold text-slate-900 leading-tight">
                    Coding Roadmaps
                  </h4>

                  <p className="text-[12px] text-slate-500 mt-1 leading-snug">
                    Follow structured paths for DSA, Web Dev, and System
                    Design.
                  </p>
                </div>
              </div>

              <div className="bg-white p-4 rounded-2xl shadow-[0_4px_20px_rgb(0,0,0,0.03)] border border-slate-200 flex items-start gap-4 transform transition-all duration-300 hover:-translate-y-1 hover:shadow-md">
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
                      d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                    />
                  </svg>
                </div>

                <div>
                  <h4 className="text-sm font-bold text-slate-900 leading-tight">
                    Smart Job Matches
                  </h4>

                  <p className="text-[12px] text-slate-500 mt-1 leading-snug">
                    Get curated internship and job opportunities based on
                    your skills.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="absolute top-[5%] right-[-10%] w-[250px] h-[250px] bg-indigo-600/5 rounded-full blur-3xl pointer-events-none" />

          <div className="absolute bottom-[0%] left-[-10%] w-[200px] h-[200px] bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />
        </div>
      </div>
    </section>
  );
}