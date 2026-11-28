
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

import { useBilling } from '@/hooks/useBilling';
import type { PaymentStatusResponse } from '@/types/billing';

type ResultState =
  | 'VERIFYING'
  | 'SUCCESS'
  | 'FAILED'
  | 'PENDING'
  | 'ERROR';

export default function BillingReturnPage() {
  const { verifyPayment } = useBilling();

  const [orderId, setOrderId] = useState('');
  const [result, setResult] = useState<ResultState>('VERIFYING');
  const [payment, setPayment] =
    useState<PaymentStatusResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const id = searchParams.get('order_id');

    if (id === null || id.trim() === '') {
      setResult('ERROR');
      setErrorMessage('No payment order was provided.');
      return;
    }

    const validOrderId: string = id;

    setOrderId(validOrderId);

    let cancelled = false;

    async function verifyWithPolling() {
      for (let attempt = 0; attempt < 10; attempt += 1) {
        if (cancelled) return;

        try {
          const response = await verifyPayment(validOrderId);

          if (cancelled) return;

          setPayment(response);

          if (response.status === 'SUCCESS') {
            setResult('SUCCESS');
            return;
          }

          if (
            response.status === 'FAILED' ||
            response.status === 'ABANDONED'
          ) {
            setResult('FAILED');
            return;
          }
        } catch (error) {
          if (cancelled) return;

          setErrorMessage(
            error instanceof Error
              ? error.message
              : 'Payment verification is temporarily unavailable.'
          );
        }

        if (attempt < 9) {
          await new Promise<void>((resolve) => {
            window.setTimeout(resolve, 3000);
          });
        }
      }

      if (!cancelled) {
        setResult((current) =>
          current === 'VERIFYING' ? 'PENDING' : current
        );
      }
    }

    void verifyWithPolling();

    return () => {
      cancelled = true;
    };
  }, [verifyPayment]);

  const heading = {
    VERIFYING: 'Verifying your payment',
    SUCCESS: 'Payment confirmed',
    FAILED: 'Payment not completed',
    PENDING: 'Payment is still processing',
    ERROR: 'Unable to verify payment',
  }[result];

  return (
    <main className="flex min-h-screen items-center justify-center bg-[var(--background)] px-5 py-12 text-[var(--text-primary)]">
      <section className="w-full max-w-lg rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-8 shadow-sm sm:p-10">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--primary)]">
          UniOS.ai · Billing
        </p>

        <h1 className="mt-5 text-2xl font-bold">{heading}</h1>

        {result === 'VERIFYING' && (
          <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
            Please wait while we confirm the order with our payment
            provider. Do not make another payment while verification is
            in progress.
          </p>
        )}

        {result === 'SUCCESS' && (
          <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
            Your payment has been confirmed by the backend.
            Your subscription details are being refreshed.
          </p>
        )}

        {result === 'FAILED' && (
          <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
            The backend reports that this order failed or was abandoned.
            You can return to pricing and try again if you wish.
          </p>
        )}

        {result === 'PENDING' && (
          <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
            We have not received a final payment status yet. You can check
            again shortly; you do not need to pay again just because this
            page is still pending.
          </p>
        )}

        {result === 'ERROR' && (
          <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
            {errorMessage || 'Please return to billing and try again.'}
          </p>
        )}

        {orderId && (
          <div className="mt-6 rounded-xl bg-[var(--surface-alt)] p-4">
            <p className="text-xs text-[var(--text-muted)]">Order ID</p>
            <p className="mt-1 break-all text-sm font-medium">{orderId}</p>

            {payment && (
              <>
                <p className="mt-3 text-xs text-[var(--text-muted)]">
                  Order status
                </p>
                <p className="mt-1 text-sm font-semibold">
                  {payment.status}
                </p>

                <p className="mt-3 text-xs text-[var(--text-muted)]">
                  Amount
                </p>
                <p className="mt-1 text-sm font-semibold">
                  {new Intl.NumberFormat('en-IN', {
                    style: 'currency',
                    currency: payment.currency,
                    maximumFractionDigits: 2,
                  }).format(payment.amount)}
                </p>
              </>
            )}
          </div>
        )}

        {errorMessage && result !== 'ERROR' && (
          <p className="mt-4 text-xs text-amber-800">
            Latest verification message: {errorMessage}
          </p>
        )}

        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <Link
            href="/billing"
            className="rounded-xl bg-[var(--primary)] px-5 py-3 text-center text-sm font-semibold text-white hover:bg-[var(--primary-hover)]"
          >
            Back to billing
          </Link>

          <Link
            href="/dashboard"
            className="rounded-xl border border-[var(--border)] px-5 py-3 text-center text-sm font-semibold text-[var(--text-primary)] hover:bg-[var(--surface-alt)]"
          >
            Go to dashboard
          </Link>
        </div>
      </section>
    </main>
  );
}
