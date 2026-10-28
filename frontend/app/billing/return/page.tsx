
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
    const id = new URLSearchParams(window.location.search).get('order_id');

    if (!id) {
      setResult('ERROR');
      setErrorMessage('No payment order was provided.');
      return;
    }

    setOrderId(id);

    let cancelled = false;

    async function verifyWithPolling() {
      for (let attempt = 0; attempt < 10; attempt += 1) {
        if (cancelled) return;

        try {
          const response = await verifyPayment(id!);

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
    <main className="flex min-h-screen items-center justify-center bg-[#F7F1E7] px-5 py-12 text-[#18343A]">
      <section className="w-full max-w-lg rounded-3xl border border-[#D8DED7] bg-[#FFF9F0] p-8 shadow-sm sm:p-10">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-700">
          UniOS.ai · Billing
        </p>

        <h1 className="mt-5 text-2xl font-bold">{heading}</h1>

        {result === 'VERIFYING' && (
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Please wait while we confirm the order with our payment
            provider. Do not make another payment while verification is
            in progress.
          </p>
        )}

        {result === 'SUCCESS' && (
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Your payment has been confirmed by the backend.
            Your subscription details are being refreshed.
          </p>
        )}

        {result === 'FAILED' && (
          <p className="mt-3 text-sm leading-6 text-slate-600">
            The backend reports that this order failed or was abandoned.
            You can return to pricing and try again if you wish.
          </p>
        )}

        {result === 'PENDING' && (
          <p className="mt-3 text-sm leading-6 text-slate-600">
            We have not received a final payment status yet. You can check
            again shortly; you do not need to pay again just because this
            page is still pending.
          </p>
        )}

        {result === 'ERROR' && (
          <p className="mt-3 text-sm leading-6 text-slate-600">
            {errorMessage || 'Please return to billing and try again.'}
          </p>
        )}

        {orderId && (
          <div className="mt-6 rounded-xl bg-[#F7F1E7] p-4">
            <p className="text-xs text-slate-500">Order ID</p>
            <p className="mt-1 break-all text-sm font-medium">{orderId}</p>

            {payment && (
              <>
                <p className="mt-3 text-xs text-slate-500">Order status</p>
                <p className="mt-1 text-sm font-semibold">
                  {payment.status}
                </p>
                <p className="mt-3 text-xs text-slate-500">Amount</p>
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
            className="rounded-xl bg-[#18343A] px-5 py-3 text-center text-sm font-semibold text-white hover:bg-[#24515A]"
          >
            Back to billing
          </Link>

          <Link
            href="/dashboard"
            className="rounded-xl border border-[#D8DED7] px-5 py-3 text-center text-sm font-semibold hover:bg-[#F7F1E7]"
          >
            Go to dashboard
          </Link>
        </div>
      </section>
    </main>
  );
}
