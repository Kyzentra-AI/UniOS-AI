
'use client';

import {
  enrollMFA,
  verifyMFAEnrollment,
} from '@/lib/api';

import {
  getAccessToken,
  saveSession,
  getRememberMe,
} from '@/lib/auth';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import QRCode from 'qrcode';

export default function MFASetup() {
  const router = useRouter();

  const [factorId, setFactorId] = useState('');
  const [secret, setSecret] = useState('');
  const [qrCode, setQrCode] = useState('');
  const [code, setCode] = useState('');

  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isVerifying, setIsVerifying] = useState(false);

  // Prevent duplicate MFA enrollment requests in development
  const hasInitialized = useRef(false);

  useEffect(() => {
    if (hasInitialized.current) return;

    hasInitialized.current = true;

    const setupMFA = async () => {
      const accessToken = getAccessToken();

      if (!accessToken) {
        setError(
          'Your session has expired. Please sign in again.'
        );
        setIsLoading(false);
        return;
      }

      try {
        const data = await enrollMFA(accessToken);

        const id = data.id || data.factor_id;

        if (!id) {
          throw new Error(
            'MFA setup failed because no factor ID was returned.'
          );
        }

        setFactorId(id);

        const uri = data.totp?.uri || '';
        const returnedSecret = data.totp?.secret || '';

        setSecret(returnedSecret);

        // Generate a browser-compatible QR image
        // from the otpauth:// URI returned by Supabase.
        if (uri) {
          const generatedQRCode =
            await QRCode.toDataURL(uri);

          setQrCode(generatedQRCode);
        } else {
          throw new Error(
            'MFA setup failed because no setup URI was returned.'
          );
        }
      } catch (err) {
        console.error(
          'MFA enrollment failed:',
          err
        );

        setError(
          err instanceof Error
            ? err.message
            : 'Unable to set up MFA. Please try again.'
        );
      } finally {
        setIsLoading(false);
      }
    };

    setupMFA();
  }, []);

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

  const handleVerify = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    if (code.length !== 6) {
      setError(
        'Please enter the 6-digit verification code.'
      );
      return;
    }

    if (!factorId) {
      setError(
        'MFA setup information is missing. Please restart the setup.'
      );
      return;
    }

    const accessToken = getAccessToken();

    if (!accessToken) {
      setError(
        'Your session has expired. Please sign in again.'
      );
      return;
    }

    setIsVerifying(true);
    setError('');

    try {
      const data = await verifyMFAEnrollment(
        accessToken,
        {
          factor_id: factorId,
          code,
        }
      );

      if (!data.session?.access_token) {
        throw new Error(
          'MFA was activated, but no valid session was returned.'
        );
      }

      saveSession(
        data.session,
        getRememberMe()
      );

      setCode('');

      router.replace('/dashboard');
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

  return (
    <section className="min-h-screen flex items-center justify-center bg-[var(--auth-bg)] p-4 sm:p-8 font-inter">
      <div className="w-full max-w-[520px] bg-[var(--surface)] rounded-[24px] shadow-sm border border-[var(--border)] p-8 sm:p-12">

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
          <div className="w-16 h-16 rounded-2xl bg-[var(--primary-soft)] flex items-center justify-center">
            <svg
              className="w-8 h-8 text-[var(--primary)]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.7}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2h12V9a4 4 0 00-8 0v2h8z"
              />
            </svg>
          </div>
        </div>

        {/* Heading */}
        <div className="text-center mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-[var(--text-primary)] mb-3">
            Set Up Two-Factor Authentication
          </h1>

          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
            Scan the QR code using your authenticator app,
            then enter the 6-digit code to activate MFA.
          </p>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-3.5 bg-[var(--danger-soft)] border border-[var(--danger-border)] rounded-xl">
            <p className="text-sm font-medium text-[var(--danger)]">
              {error}
            </p>
          </div>
        )}

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <svg
              className="animate-spin h-8 w-8 text-[var(--primary)]"
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

            <p className="mt-4 text-sm text-[var(--text-secondary)]">
              Preparing your MFA setup...
            </p>
          </div>
        ) : (
          <>
            {/* QR Code */}
            {qrCode && (
              <div className="flex justify-center mb-6">
                <div className="p-4 bg-[var(--surface)] border border-[var(--border)] rounded-2xl">
                  <img
                    src={qrCode}
                    alt="MFA setup QR code"
                    className="w-48 h-48"
                  />
                </div>
              </div>
            )}

            {/* Manual Secret */}
            {secret && (
              <div className="mb-8">
                <p className="text-sm font-medium text-[var(--text-label)] mb-2 text-center">
                  Or enter this setup key manually
                </p>

                <div className="px-4 py-3 bg-[var(--auth-bg)] border border-[var(--border)] rounded-xl text-center break-all">
                  <code className="text-sm font-semibold tracking-wider text-[var(--text-primary)]">
                    {secret}
                  </code>
                </div>
              </div>
            )}

            {/* Verification Form */}
            <form
              onSubmit={handleVerify}
              className="space-y-6"
            >
              <div>
                <label
                  htmlFor="mfa-code"
                  className="block text-sm font-medium text-[var(--text-label)] mb-2"
                >
                  Authentication Code
                </label>

                <input
                  id="mfa-code"
                  name="mfa-code"
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  maxLength={6}
                  value={code}
                  onChange={handleCodeChange}
                  placeholder="000000"
                  className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-[var(--text-primary)] text-center text-xl tracking-[0.5em] font-semibold focus:outline-none focus:ring-2 focus:ring-[var(--primary-soft)] focus:border-[var(--primary)] transition-colors"
                  autoFocus
                />
              </div>

              <button
                type="submit"
                disabled={
                  isVerifying ||
                  code.length !== 6 ||
                  !factorId
                }
                className="w-full bg-[var(--primary)] hover:bg-[var(--primary-hover)] text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed flex justify-center items-center shadow-[0_4px_14px_0_var(--primary-shadow)]"
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
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>

                    Verifying...
                  </>
                ) : (
                  'Activate MFA'
                )}
              </button>
            </form>
          </>
        )}

        <p className="text-center text-xs text-[var(--text-muted)] mt-6 leading-relaxed">
          Make sure your authenticator app is installed before
          continuing. Keep your setup key private.
        </p>
      </div>
    </section>
  );
}

