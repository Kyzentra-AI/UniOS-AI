
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

import { useBilling } from '@/hooks/useBilling';
import { openCashfreeCheckout } from '@/services/cashfreeService';
import type { PlanConfiguration } from '@/types/billing';

export default function BillingPage() {
  const router = useRouter();

  const {
    plans,
    entitlement,
    isLoading,
    plansError,
    entitlementError,
    activateTrial,
    isActivatingTrial,
    trialError,
    createCheckout,
    isCreatingCheckout,
    checkoutError,
  } = useBilling();

  const [activePlan, setActivePlan] = useState<string | null>(null);
  const [message, setMessage] = useState('');

  async function handleCheckout(plan: PlanConfiguration) {
    setMessage('');
    setActivePlan(plan.planCode);

    try {
      const returnUrl =
        `${window.location.origin}/billing/return?order_id={order_id}`;

      const checkout = await createCheckout({
        planCode: plan.planCode,
        returnUrl,
      });

      await openCashfreeCheckout(
        checkout.paymentSessionId,
        checkout.environment
      );

      router.push(
        `/billing/return?order_id=${encodeURIComponent(checkout.orderId)}`
      );
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : 'Unable to start checkout. Please try again.'
      );
    } finally {
      setActivePlan(null);
    }
  }

  async function handleTrial() {
    setMessage('');

    try {
      const result = await activateTrial();
      setMessage(result.message);
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : 'Unable to activate your trial.'
      );
    }
  }

  if (isLoading) {
    return (
      <main className="mx-auto max-w-6xl px-6 py-16">
        <p className="text-sm text-slate-500">
          Loading your subscription and plans...
        </p>
      </main>
    );
  }

  if (plansError) {
    return (
      <main className="mx-auto max-w-6xl px-6 py-16">
        <h1 className="text-2xl font-semibold text-slate-900">
          Unable to load plans
        </h1>
        <p className="mt-2 text-sm text-slate-600">
          Please try again in a moment.
        </p>
      </main>
    );
  }

  const canActivateTrial =
    entitlement?.currentPlan === 'FREE' &&
    entitlement.trialUsed === false;

  return (
    <main className="min-h-screen bg-[#F7F1E7] px-5 py-12 text-[#18343A] sm:px-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-teal-700">
              UniOS.ai
            </p>
            <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
              Choose your plan
            </h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-600 sm:text-base">
              Find the right level of support for your learning and career
              journey. Your plan and usage limits are managed by UniOS.
            </p>
          </div>

          <div className="rounded-2xl border border-[#D8DED7] bg-[#FFF9F0] p-4">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              Current plan
            </p>
            <p className="mt-1 text-lg font-bold">
              {entitlement?.currentPlan ?? 'Unavailable'}
            </p>
            <p className="mt-1 text-sm text-slate-600">
              {entitlement?.isTrial
                ? 'Trial active'
                : entitlement?.isActive
                  ? 'Active subscription'
                  : 'No active paid subscription'}
            </p>
            {entitlement?.daysRemaining != null && (
              <p className="mt-1 text-xs text-slate-500">
                {entitlement.daysRemaining} day(s) remaining
              </p>
            )}
          </div>
        </div>

        {entitlementError && (
          <div className="mb-6 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
            Your plans are available, but your current subscription status
            could not be loaded. Please refresh or sign in again.
          </div>
        )}

        {message && (
          <div
            role="status"
            className="mb-6 rounded-xl border border-teal-200 bg-white p-4 text-sm"
          >
            {message}
          </div>
        )}

        {trialError && (
          <p className="mb-4 text-sm text-red-700">
            {trialError.message}
          </p>
        )}

        {checkoutError && (
          <p className="mb-4 text-sm text-red-700">
            {checkoutError.message}
          </p>
        )}

        {canActivateTrial && (
          <section className="mb-8 flex flex-col gap-4 rounded-2xl border border-teal-200 bg-[#FFF9F0] p-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="font-semibold">Try Basic for 3 days</h2>
              <p className="mt-1 text-sm text-slate-600">
                Activate your one-time trial if your account is eligible.
              </p>
            </div>

            <button
              type="button"
              onClick={handleTrial}
              disabled={isActivatingTrial}
              className="rounded-xl bg-[#18343A] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#24515A] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isActivatingTrial ? 'Activating...' : 'Activate free trial'}
            </button>
          </section>
        )}

        <section className="grid gap-5 md:grid-cols-3">
          {plans.map((plan) => {
            const isCurrentPlan =
              entitlement?.currentPlan === plan.planCode &&
              entitlement?.isActive;

            const isBusy =
              isCreatingCheckout && activePlan === plan.planCode;

            return (
              <article
                key={plan.planCode}
                className={`flex flex-col rounded-2xl border bg-[#FFF9F0] p-6 shadow-sm ${
                  plan.planCode === 'PRO'
                    ? 'border-teal-700 ring-1 ring-teal-700'
                    : 'border-[#D8DED7]'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="text-xl font-bold">{plan.name}</h2>
                    <p className="mt-2 min-h-10 text-sm leading-5 text-slate-600">
                      {plan.description}
                    </p>
                  </div>

                  {plan.planCode === 'PRO' && (
                    <span className="rounded-full bg-teal-100 px-3 py-1 text-xs font-semibold text-teal-900">
                      Pro
                    </span>
                  )}
                </div>

                <div className="mt-6">
                  <p className="text-3xl font-bold">
                    {new Intl.NumberFormat('en-IN', {
                      style: 'currency',
                      currency: plan.currency,
                      maximumFractionDigits: 0,
                    }).format(plan.price)}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    {plan.price === 0
                      ? 'Free plan'
                      : `${plan.durationDays} days · prepaid`}
                  </p>
                </div>

                <ul className="mt-6 flex-1 space-y-3">
                  {plan.features.map((feature, index) => (
                    <li
                      key={`${plan.planCode}-${index}`}
                      className="flex gap-2 text-sm leading-5 text-slate-700"
                    >
                      <span
                        aria-hidden="true"
                        className="font-bold text-teal-700"
                      >
                        ✓
                      </span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  type="button"
                  disabled={
                    isBusy ||
                    isCreatingCheckout ||
                    isActivatingTrial ||
                    isCurrentPlan ||
                    plan.planCode === 'FREE'
                  }
                  onClick={() => handleCheckout(plan)}
                  className="mt-8 w-full rounded-xl bg-[#18343A] px-4 py-3 text-sm font-semibold text-white transition hover:bg-[#24515A] disabled:cursor-not-allowed disabled:bg-slate-300 disabled:text-slate-600"
                >
                  {isBusy
                    ? 'Preparing checkout...'
                    : isCurrentPlan
                      ? 'Current plan'
                      : plan.planCode === 'FREE'
                        ? 'Included'
                        : `Choose ${plan.name}`}
                </button>
              </article>
            );
          })}
        </section>

        <p className="mt-8 text-center text-xs leading-5 text-slate-500">
          Paid plans are prepaid. Payment status is confirmed by the UniOS
          backend; closing the checkout window does not itself confirm a
          successful or failed payment.
        </p>
      </div>
    </main>
  );
}
