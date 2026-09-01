'use client';

import { API_URL } from '@/lib/api';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import QRCode from 'qrcode';

interface MFAEnrollResponse {
  id?: string;
  factor_type?: string;
  friendly_name?: string;
  status?: string;
  totp?: {
    qr_code?: string;
    secret?: string;
    uri?: string;
  };
  detail?: string;
  message?: string;
}

interface MFAVerifyEnrollResponse {
  message?: string;
  session?: {
    access_token?: string;
    refresh_token?: string;
    expires_in?: number;
    token_type?: string;
  };
  detail?: string;
}

export default function MFAsetup() {
  const router = useRouter();

  const [factorId, setFactorId] = useState('');
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [code, setCode] = useState('');

  const [isLoading, setIsLoading] = useState(true);
  const [isVerifying, setIsVerifying] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const [error, setError] = useState('');

  useEffect(() => {
    enrollMFA();
  }, []);

  const enrollMFA = async () => {
    const accessToken = sessionStorage.getItem('access_token');

    if (!accessToken) {
      setError('Your session has expired. Please sign in again.');
      setIsLoading(false);
      return;
    }

    try {
      setError('');

      const response = await fetch(
        `${API_URL}/api/v1/auth/mfa/enroll`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        }
      );

      const data: MFAEnrollResponse = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : typeof data.message === 'string'
              ? data.message
              : 'Unable to set up two-factor authentication.'
        );
      }

      if (!data.id) {
        throw new Error('MFA factor ID was not returned by the server.');
      }

      setFactorId(data.id);

      if (data.totp?.secret) {
        setSecret(data.totp.secret);
      }

      /*
       * Supabase normally returns qr_code as an SVG data URI.
       * If it does, use it directly.
       *
       * Otherwise, generate a QR code from the TOTP URI.
       */
      if (data.totp?.qr_code) {
        setQrCode(data.totp.qr_code);
      } else if (data.totp?.uri) {
        const generatedQRCode = await QRCode.toDataURL(
          data.totp.uri,
          {
            width: 220,
            margin: 2,
          }
        );

        setQrCode(generatedQRCode);
      } else {
        throw new Error(
          'QR code information was not returned by the server.'
        );
      }
    } catch (err) {
      console.error('MFA enrollment failed:', err);

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to set up MFA. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleCodeChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value
      .replace(/\D/g, '')
      .slice(0, 6);

    setCode(value);

    if (error) {
      setError('');
    }
  };

  const handleVerifyEnrollment = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    if (code.length !== 6) {
      setError('Please enter the 6-digit verification code.');
      return;
    }

    if (!factorId) {
      setError('MFA setup information is missing. Please try again.');
      return;
    }

    const accessToken = sessionStorage.getItem('access_token');

    if (!accessToken) {
      setError(
        'Your session has expired. Please sign in again.'
      );
      return;
    }

    setIsVerifying(true);
    setError('');

    try {
      const response = await fetch(
        `${API_URL}/api/v1/auth/mfa/verify-enroll`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            factor_id: factorId,
            code,
          }),
        }
      );

      const data: MFAVerifyEnrollResponse =
        await response.json();

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
       * The backend returns a new session after
       * successfully activating MFA.
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

      setIsSuccess(true);
    } catch (err) {
      console.error(
        'MFA enrollment verification failed:',
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to verify MFA code. Please try again.'
      );
    } finally {
      setIsVerifying(false);
    }
  };

  const handleContinue = () => {
    router.push('/dashboard');
  };

  if (isLoading) {
    return (
      <section className="min-h-screen flex items-center justify-center bg-slate-50 p-4 font-inter">
        <div className="w-full max-w-[520px] bg-white rounded-[24px] shadow-sm border border-slate-200 p-8 sm:p-12">
          <div className="flex justify-center mb-8">
            <img
              src="/logo.svg"
              alt="UniOS.ai"
              className="h-8 w-auto"
            />
          </div>

          <div className="flex justify-center py-12">
            <svg
              className="animate-spin h-8 w-8 text-indigo-600"
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
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
          </div>

          <p className="text-center text-sm text-slate-500">
            Preparing your two-factor authentication setup...
          </p>
        </div>
      </section>
    );
  }

  if (isSuccess) {
    return (
      <section className="min-h-screen flex items-center justify-center bg-slate-50 p-4 sm:p-8 font-inter">
        <div className="w-full max-w-[520px] bg-white rounded-[24px] shadow-sm border border-slate-200 p-8 sm:p-12">

          <div className="flex justify-center mb-8">
            <img
              src="/logo.svg"
              alt="UniOS.ai"
              className="h-8 w-auto"
            />
          </div>

          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 rounded-2xl bg-emerald-50 flex items-center justify-center">
              <svg
                className="w-8 h-8 text-emerald-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
          </div>

          <div className="text-center mb-8">
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-3">
              Two-Factor Authentication Enabled
            </h1>

            <p className="text-sm text-slate-500 leading-relaxed">
              Your account is now protected with an additional
              layer of security.
            </p>
          </div>

          <button
            type="button"
            onClick={handleContinue}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 shadow-[0_4px_14px_0_rgba(79,70,229,0.25)]"
          >
            Continue to Dashboard
          </button>
        </div>
      </section>
    );
  }

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
            Set Up Two-Factor Authentication
          </h1>

          <p className="text-sm text-slate-500 leading-relaxed">
            Add an extra layer of security to your UniOS.ai
            account using an authenticator app.
          </p>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-3.5 bg-red-50 border border-red-100 rounded-xl">
            <p className="text-sm font-medium text-red-700">
              {error}
            </p>

            <button
              type="button"
              onClick={enrollMFA}
              className="mt-2 text-xs font-semibold text-red-700 hover:text-red-800 underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* QR Section */}
        {qrCode && (
          <div className="mb-8">

            <div className="text-center mb-5">
              <h2 className="text-base font-semibold text-slate-800 mb-1">
                1. Scan the QR code
              </h2>

              <p className="text-sm text-slate-500">
                Open Google Authenticator or another TOTP
                authenticator app and scan this code.
              </p>
            </div>

            <div className="flex justify-center">
              <div className="p-4 bg-white border border-slate-200 rounded-2xl shadow-sm">
                <img
                  src={qrCode}
                  alt="MFA setup QR code"
                  className="w-[220px] h-[220px]"
                />
              </div>
            </div>

            {/* Secret */}
            {secret && (
              <div className="mt-5">
                <p className="text-xs text-slate-400 text-center mb-2">
                  Can't scan the QR code? Enter this setup key
                  manually.
                </p>

                <div className="bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-center break-all">
                  <span className="text-sm font-mono font-semibold text-slate-700 tracking-wider">
                    {secret}
                  </span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Verification */}
        {qrCode && (
          <form
            onSubmit={handleVerifyEnrollment}
            className="space-y-6"
          >
            <div>
              <label
                htmlFor="mfa-setup-code"
                className="block text-sm font-medium text-slate-700 mb-2"
              >
                2. Enter the 6-digit code
              </label>

              <input
                id="mfa-setup-code"
                name="mfa-setup-code"
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
                Enter the current code shown in your
                authenticator app.
              </p>
            </div>

            <button
              type="submit"
              disabled={
                isVerifying ||
                code.length !== 6 ||
                !factorId
              }
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed flex justify-center items-center shadow-[0_4px_14px_0_rgba(79,70,229,0.25)]"
            >
              {isVerifying ? (
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
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                    />
                  </svg>

                  Enabling...
                </>
              ) : (
                'Enable Two-Factor Authentication'
              )}
            </button>
          </form>
        )}

        {/* Back */}
        <div className="mt-8 text-center">
          <Link
            href="/dashboard"
            className="text-sm font-semibold text-indigo-600 hover:text-indigo-700 transition-colors"
          >
            Back to Dashboard
          </Link>
        </div>

        <p className="text-center text-xs text-slate-400 mt-6 leading-relaxed">
          Make sure your authenticator app is installed before
          continuing. Keep your setup key private.
        </p>
      </div>
    </section>
  );
}