
'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';

import { saveSession } from '@/lib/auth';
import {
  checkResetPasswordMFAStatus,
  exchangeOAuthCode,
} from '@/lib/api';

interface AuthSession {
  access_token: string;
  refresh_token?: string;
  expires_in?: number;
  token_type?: string;
}

export default function AuthCallbackPage() {
  const router = useRouter();

  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(true);

  // Prevent duplicate callback processing in React Strict Mode.
  const callbackStarted = useRef(false);

  useEffect(() => {
    if (callbackStarted.current) return;
    callbackStarted.current = true;

    const handleCallback = async () => {
      try {
        const url = new URL(window.location.href);

        const queryParams = url.searchParams;
        const hashParams = new URLSearchParams(
          url.hash.startsWith('#') ? url.hash.substring(1) : url.hash
        );

        // Read OAuth errors from both query parameters and hash.
        const authError =
          queryParams.get('error_description') ||
          queryParams.get('error') ||
          hashParams.get('error_description') ||
          hashParams.get('error');

        const authCode = queryParams.get('code');

        const accessToken = hashParams.get('access_token');
        const refreshToken = hashParams.get('refresh_token');
        const expiresIn = hashParams.get('expires_in');
        const tokenType = hashParams.get('token_type');

        // Remove OAuth parameters and tokens from the address bar.
        window.history.replaceState(
          {},
          document.title,
          window.location.pathname
        );

        if (authError) {
          throw new Error(authError);
        }

        let session: AuthSession;

        // Flow 1: Authorization code returned by the OAuth provider.
        if (authCode) {
          const response = await exchangeOAuthCode(authCode);

          if (!response.session?.access_token) {
            throw new Error(
              'The authentication provider did not return a valid session.'
            );
          }

          session = response.session;
        }
        // Flow 2: Tokens returned directly in the URL hash.
        else if (accessToken) {
          session = {
            access_token: accessToken,
            refresh_token: refreshToken || undefined,
            expires_in: expiresIn ? Number(expiresIn) : undefined,
            token_type: tokenType || 'bearer',
          };
        } else {
          throw new Error(
            'Authentication session was not returned by the provider. Please try again.'
          );
        }

        // Check whether this account already has MFA enabled.
        const mfaStatus = await checkResetPasswordMFAStatus(
          session.access_token
        );

        if (mfaStatus.requires_mfa) {
          sessionStorage.setItem('mfa_user_id', mfaStatus.user_id);
          sessionStorage.setItem(
            'mfa_access_token',
            session.access_token
          );
          sessionStorage.setItem('mfa_remember_me', 'false');

          router.replace('/mfa-verify');
          return;
        }

        // Save the session using the existing authentication helper.
        saveSession(session, false);

        router.replace('/mfa-enroll');
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to complete authentication. Please try again.'
        );
        setIsProcessing(false);
      }
    };

    void handleCallback();
  }, [router]);

  if (error) {
    return (
      <main className="min-h-screen flex items-center justify-center p-6">
        <div className="w-full max-w-md text-center">
          <h1 className="text-xl font-semibold text-[var(--text-primary)]">
            Authentication failed
          </h1>

          <div
            role="alert"
            className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
          >
            {error}
          </div>

          <button
            type="button"
            onClick={() => router.replace('/login')}
            className="mt-6 bg-[var(--primary)] text-white px-5 py-3 rounded-xl"
          >
            Try again
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex items-center justify-center">
      <p className="text-sm text-[var(--text-secondary)]">
        {isProcessing ? 'Completing authentication...' : 'Please wait...'}
      </p>
    </main>
  );
}
