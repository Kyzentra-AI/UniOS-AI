'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { saveSession } from '@/lib/auth';
import { checkResetPasswordMFAStatus } from '@/lib/api';

export default function AuthCallbackPage() {
  const router = useRouter();

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const hash = window.location.hash;

        if (!hash) {
          setError(
            'Authentication session was not returned by the provider.'
          );
          return;
        }

        const params = new URLSearchParams(hash.substring(1));

        const accessToken = params.get('access_token');
        const refreshToken = params.get('refresh_token');
        const expiresIn = params.get('expires_in');
        const tokenType = params.get('token_type');

        if (!accessToken) {
          const authError =
            params.get('error_description') ||
            params.get('error') ||
            'Authentication session was not returned by the provider.';

          setError(authError);
          return;
        }

        // Check whether this Google account already has MFA enabled.
        const mfaStatus = await checkResetPasswordMFAStatus(accessToken);

        // Remove OAuth tokens from the address bar.
        window.history.replaceState(
          {},
          document.title,
          '/auth/callback'
        );

        if (mfaStatus.requires_mfa) {
          // MFA is already configured.
          // Do NOT create the final session yet.
          sessionStorage.setItem(
            'mfa_user_id',
            mfaStatus.user_id
          );

          sessionStorage.setItem(
            'mfa_access_token',
            accessToken
          );

          // Social login currently has no "Remember me" option,
          // so use the same default as normal login.
          sessionStorage.setItem(
            'mfa_remember_me',
            'false'
          );

          router.replace('/mfa-verify');
          return;
        }

        // MFA is not configured yet.
        saveSession({
          access_token: accessToken,
          refresh_token: refreshToken || undefined,
          expires_in: expiresIn ? Number(expiresIn) : undefined,
          token_type: tokenType || 'bearer',
        });

        router.replace('/mfa-enroll');
      } catch (err) {
        console.error('OAuth callback failed:', err);

        setError(
          err instanceof Error
            ? err.message
            : 'Unable to complete authentication.'
        );
      }
    };

    handleCallback();
  }, [router]);

  if (error) {
    return (
      <main className="min-h-screen flex items-center justify-center p-6">
        <div className="w-full max-w-md text-center">
          <h1 className="text-xl font-semibold text-[var(--text-primary)]">
            Authentication failed
          </h1>

          <p className="mt-3 text-sm text-[var(--text-secondary)]">
            {error}
          </p>

          <button
            type="button"
            onClick={() => router.replace('/login')}
            className="mt-6 bg-[var(--primary)] text-white px-5 py-3 rounded-xl"
          >
            Back to login
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex items-center justify-center">
      <p className="text-sm text-[var(--text-secondary)]">
        Completing authentication...
      </p>
    </main>
  );
}