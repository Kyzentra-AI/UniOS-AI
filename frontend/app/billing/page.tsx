
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

import {
  useBilling,
  useCheckoutPreview,
} from '@/hooks/useBilling';

import { openCashfreeCheckout } from '@/services/cashfreeService';

import type {
  BillingCycle,
  PlanConfiguration,
  PlanTier,
} from '@/types/billing';

const BILLING_CYCLES: {
  value: BillingCycle;
  label: string;
}[] = [
  { value: 'WEEKLY', label: 'Weekly' },
  { value: 'MONTHLY', label: 'Monthly' },
  { value: 'SEMESTER', label: 'Semester' },
];

function formatPrice(amount: number, currency = 'INR') {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(value?: string | null) {
  if (!value) return 'Not available';

  return new Date(value).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

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
  } = useBilling();

  const [billingCycle, setBillingCycle] =
    useState<BillingCycle>('MONTHLY');

  const [selectedPlan, setSelectedPlan] =
    useState<PlanTier | null>(null);

  const [message, setMessage] = useState('');
  const [activePlan, setActivePlan] =
    useState<PlanTier | null>(null);

  const previewQuery = useCheckoutPreview(
    selectedPlan,
    billingCycle
  );

  const preview = previewQuery.data;

  async function handleCheckout(plan: PlanConfiguration) {
    setMessage('');

    const availableCycle = plan.cycles.find(
      (cycle) => cycle.billingCycle === billingCycle
    );

    if (!availableCycle) {
      setMessage(
        'This billing cycle is not available for the selected plan.'
      );
      return;
    }

    setSelectedPlan(plan.planCode);
  }

  async function proceedToCheckout() {
    if (!selectedPlan || !preview || !preview.allowed) {
      return;
    }

    setMessage('');
    setActivePlan(selectedPlan);

    try {
      const returnUrl =
        `${window.location.origin}/billing/return?order_id={order_id}`;

      const checkout = await createCheckout({
        planCode: selectedPlan as Exclude<PlanTier, 'FREE'>,
        billingCycle,
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

  const canActivateTrial =
    entitlement?.currentPlan === 'FREE' &&
    entitlement.trialUsed === false;

  if (isLoading) {
    return (
      <main className="min-h-screen bg-[var(--background)] px-5 py-16 text-[var(--text-primary)]">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-center">
          <div className="relative mb-8 flex h-24 w-24 items-center justify-center">
            <div className="absolute inset-0 rounded-full border-4 border-[var(--border)] opacity-50" />
            <div className="absolute inset-0 animate-spin rounded-full border-4 border-transparent border-t-[var(--primary)] border-r-[var(--primary)]" />
            <div className="absolute h-14 w-14 animate-pulse rounded-full bg-[var(--primary-soft)]" />
            <div className="relative h-5 w-5 rounded-full bg-[var(--primary)] shadow-lg shadow-[var(--primary-shadow)]" />
          </div>

          <h2 className="text-xl font-semibold tracking-tight text-[var(--text-primary)]">
            Preparing your plans
          </h2>

          <p className="mt-2 text-center text-sm text-[var(--text-secondary)]">
            Loading your subscription and finding the right plan for you.
          </p>

          <div className="mt-6 flex items-center gap-2">
            <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--primary)]" />
            <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--primary)] [animation-delay:150ms]" />
            <span className="h-2 w-2 animate-bounce rounded-full bg-[var(--primary)] [animation-delay:300ms]" />
          </div>

          <div className="mt-14 grid w-full max-w-4xl gap-5 md:grid-cols-3">
            {[1, 2, 3].map((item) => (
              <div
                key={item}
                className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm"
              >
                <div className="skeleton mb-5 h-4 w-24 rounded-md" />
                <div className="skeleton mb-3 h-8 w-32 rounded-lg" />
                <div className="skeleton mb-7 h-3 w-40 rounded-md" />
                <div className="skeleton mb-3 h-10 w-full rounded-xl" />

                <div className="mt-7 space-y-4">
                  {[1, 2, 3, 4].map((line) => (
                    <div key={line} className="flex items-center gap-3">
                      <div className="skeleton h-4 w-4 rounded-full" />
                      <div className="skeleton h-3 flex-1 rounded-md" />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <p className="mt-8 text-xs text-[var(--text-muted)]">
            This usually takes just a moment.
          </p>
        </div>
      </main>
    );
  }

  if (plansError) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--background)] px-5 py-16">
        <div className="w-full max-w-md rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-8 text-center shadow-sm">
          <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-[var(--danger-soft)]">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              className="h-8 w-8 text-[var(--danger)]"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="9" />
              <path d="M12 8v4" />
              <path d="M12 16h.01" />
            </svg>
          </div>

          <h1 className="text-2xl font-semibold tracking-tight text-[var(--text-primary)]">
            Unable to load plans
          </h1>

          <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
            We couldn't retrieve your subscription details right now.
            Please try again in a moment.
          </p>

          <div className="mt-7 rounded-xl border border-[var(--danger-border)] bg-[var(--danger-soft)] px-4 py-3 text-xs text-[var(--danger-text)]">
            Your subscription information hasn't been changed.
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[var(--background)] px-5 py-12 text-[var(--text-primary)] sm:px-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--primary)]">
              UniOS.ai
            </p>

            <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
              Choose your plan
            </h1>

            <p className="mt-3 max-w-xl text-sm leading-6 text-[var(--text-secondary)] sm:text-base">
              Find the right level of support for your learning and career
              journey. Your plan and usage limits are managed by UniOS.
            </p>
          </div>

          <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4">
            <p className="text-xs font-medium uppercase tracking-wide text-[var(--text-muted)]">
              Current plan
            </p>

            <p className="mt-1 text-lg font-bold">
              {entitlement?.currentPlan ?? 'Unavailable'}
            </p>

            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              {entitlement?.isTrial
                ? 'Trial active'
                : entitlement?.isActive
                  ? 'Active subscription'
                  : 'No active paid subscription'}
            </p>

            {entitlement?.daysRemaining != null && (
              <p className="mt-1 text-xs text-[var(--text-muted)]">
                {entitlement.daysRemaining} day(s) remaining
              </p>
            )}

            {entitlement?.currentPeriodEnd && (
              <p className="mt-1 text-xs text-[var(--text-muted)]">
                Valid until {formatDate(entitlement.currentPeriodEnd)}
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
            className="mb-6 rounded-xl border border-[var(--primary-soft)] bg-[var(--surface)] p-4 text-sm text-[var(--text-primary)]"
          >
            {message}
          </div>
        )}

        {trialError && (
          <p className="mb-4 text-sm text-[var(--danger)]">
            {trialError.message}
          </p>
        )}

        {canActivateTrial && (
          <section className="mb-8 flex flex-col gap-4 rounded-2xl border border-[var(--primary-soft)] bg-[var(--surface)] p-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="font-semibold">Try Basic for 3 days</h2>
              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                Activate your one-time 72-hour trial if your account is eligible.
              </p>
            </div>

            <button
              type="button"
              onClick={handleTrial}
              disabled={isActivatingTrial}
              className="rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isActivatingTrial ? 'Activating...' : 'Activate free trial'}
            </button>
          </section>
        )}

        <section className="mb-6 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5">
          <p className="text-sm font-semibold">Choose billing duration</p>

          <div className="mt-4 flex flex-wrap gap-2">
            {BILLING_CYCLES.map((cycle) => (
              <button
                key={cycle.value}
                type="button"
                onClick={() => {
                  setBillingCycle(cycle.value);
                  setSelectedPlan(null);
                }}
                className={`rounded-xl border px-5 py-2.5 text-sm font-semibold transition ${
                  billingCycle === cycle.value
                    ? 'border-[var(--primary)] bg-[var(--primary)] text-white'
                    : 'border-[var(--border)] bg-[var(--surface-alt)] text-[var(--text-primary)] hover:border-[var(--primary)]'
                }`}
              >
                {cycle.label}
              </button>
            ))}
          </div>
        </section>

        <section className="grid gap-5 md:grid-cols-3">
          {plans.map((plan) => {
            const cycleOption = plan.cycles.find(
              (cycle) => cycle.billingCycle === billingCycle
            );

            const isCurrentPlan =
              entitlement?.currentPlan === plan.planCode &&
              entitlement?.isActive;

            const isSelected = selectedPlan === plan.planCode;

            const isBusy =
              isCreatingCheckout &&
              activePlan === plan.planCode;

            return (
              <article
                key={plan.planCode}
                className={`flex flex-col rounded-2xl border bg-[var(--surface)] p-6 shadow-sm ${
                  plan.planCode === 'PRO'
                    ? 'border-[var(--primary)] ring-1 ring-[var(--primary)]'
                    : 'border-[var(--border)]'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="text-xl font-bold">{plan.name}</h2>

                    <p className="mt-2 min-h-10 text-sm leading-5 text-[var(--text-secondary)]">
                      {plan.description}
                    </p>
                  </div>

                  {plan.planCode === 'PRO' && (
                    <span className="rounded-full bg-[var(--primary-soft)] px-3 py-1 text-xs font-semibold text-[var(--text-primary)]">
                      Pro
                    </span>
                  )}
                </div>

                <div className="mt-6">
                  <p className="text-3xl font-bold">
                    {cycleOption
                      ? formatPrice(cycleOption.price, cycleOption.currency)
                      : plan.planCode === 'FREE'
                        ? formatPrice(0, plan.currency)
                        : 'Unavailable'}
                  </p>

                  <p className="mt-1 text-xs text-[var(--text-muted)]">
                    {plan.planCode === 'FREE'
                      ? 'Free plan'
                      : cycleOption
                        ? `${cycleOption.durationDays} days · prepaid`
                        : `Not available for ${billingCycle.toLowerCase()}`}
                  </p>

                  {cycleOption && plan.planCode !== 'FREE' && (
                    <div className="mt-4 rounded-xl bg-[var(--surface-alt)] p-3">
                      <p className="text-sm font-semibold">
                        {cycleOption.totalCredits.toLocaleString('en-IN')} credits
                      </p>

                      <p className="mt-1 text-xs text-[var(--text-secondary)]">
                        Learn: {cycleOption.moduleCredits.LEARN ?? 0}
                        {' · '}
                        Build: {cycleOption.moduleCredits.BUILD ?? 0}
                        {' · '}
                        Launch: {cycleOption.moduleCredits.LAUNCH ?? 0}
                      </p>

                      <p className="mt-1 text-xs text-[var(--text-muted)]">
                        {cycleOption.renewalPolicy === 'MANUAL'
                          ? 'Manual renewal'
                          : cycleOption.renewalPolicy === 'ONE_TIME'
                            ? 'One-time prepaid'
                            : 'No renewal'}
                      </p>
                    </div>
                  )}
                </div>

                <ul className="mt-6 flex-1 space-y-3">
                  {plan.features.map((feature, index) => (
                    <li
                      key={`${plan.planCode}-${index}`}
                      className="flex gap-2 text-sm leading-5 text-[var(--text-secondary)]"
                    >
                      <span
                        aria-hidden="true"
                        className="font-bold text-[var(--primary)]"
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
                    !cycleOption ||
                    plan.planCode === 'FREE' ||
                    isCreatingCheckout ||
                    isActivatingTrial
                  }
                  onClick={() => handleCheckout(plan)}
                  className={`mt-8 w-full rounded-xl px-4 py-3 text-sm font-semibold transition disabled:cursor-not-allowed disabled:bg-[var(--surface-muted)] disabled:text-[var(--text-muted)] ${
                    isSelected
                      ? 'bg-[var(--primary)] text-white'
                      : 'bg-[var(--primary)] text-white hover:bg-[var(--primary-hover)]'
                  }`}
                >
                  {isBusy
                    ? 'Preparing checkout...'
                    : isSelected
                      ? 'Selected'
                      : isCurrentPlan
                        ? 'Review renewal'
                        : plan.planCode === 'FREE'
                          ? 'Included'
                          : `Choose ${plan.name}`}
                </button>
              </article>
            );
          })}
        </section>

        {selectedPlan && (
          <section className="mt-8 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <h2 className="text-lg font-bold">
              Checkout preview
            </h2>

            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Review the amount and subscription changes before proceeding.
            </p>

            {previewQuery.isLoading && (
              <p className="mt-5 text-sm text-[var(--text-secondary)]">
                Calculating your checkout amount...
              </p>
            )}

            {previewQuery.error && (
              <p className="mt-5 text-sm text-[var(--danger)]">
                {previewQuery.error.message}
              </p>
            )}

            {preview && (
              <>
                <div className="mt-5 grid gap-4 sm:grid-cols-2">
                  <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                    <p className="text-xs text-[var(--text-muted)]">Selected plan</p>
                    <p className="mt-1 font-semibold">
                      {preview.planCode} · {preview.billingCycle}
                    </p>
                  </div>

                  <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                    <p className="text-xs text-[var(--text-muted)]">Action</p>
                    <p className="mt-1 font-semibold">
                      {preview.actionType}
                    </p>
                  </div>

                  <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                    <p className="text-xs text-[var(--text-muted)]">Plan price</p>
                    <p className="mt-1 font-semibold">
                      {formatPrice(preview.skuPrice, preview.currency)}
                    </p>
                  </div>

                  <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                    <p className="text-xs text-[var(--text-muted)]">Prorated credit</p>
                    <p className="mt-1 font-semibold">
                      {formatPrice(preview.proratedCredit, preview.currency)}
                    </p>
                  </div>

                  <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                    <p className="text-xs text-[var(--text-muted)]">New subscription starts</p>
                    <p className="mt-1 font-semibold">
                      {formatDate(preview.newPeriodStart)}
                    </p>
                  </div>

                  <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                    <p className="text-xs text-[var(--text-muted)]">New subscription ends</p>
                    <p className="mt-1 font-semibold">
                      {formatDate(preview.newPeriodEnd)}
                    </p>
                  </div>
                </div>

                {preview.remainingDaysCredited > 0 && (
                  <p className="mt-4 text-sm text-[var(--text-secondary)]">
                    {preview.remainingDaysCredited} remaining day(s) credited
                    from your existing subscription.
                  </p>
                )}

                <div className="mt-5 flex flex-col gap-2 border-t border-[var(--border)] pt-5 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-[var(--text-muted)]">
                      Final payable amount {preview.gstIncluded ? '(GST included)' : ''}
                    </p>
                    <p className="mt-1 text-2xl font-bold">
                      {formatPrice(preview.payableAmount, preview.currency)}
                    </p>
                  </div>

                  <button
                    type="button"
                    disabled={
                      !preview.allowed ||
                      previewQuery.isFetching ||
                      isCreatingCheckout
                    }
                    onClick={proceedToCheckout}
                    className="rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)] disabled:cursor-not-allowed disabled:bg-[var(--surface-muted)] disabled:text-[var(--text-muted)]"
                  >
                    {isCreatingCheckout
                      ? 'Preparing checkout...'
                      : 'Proceed to payment'}
                  </button>
                </div>

                {!preview.allowed && (
                  <div className="mt-4 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
                    {preview.blockReason ||
                      'This subscription change is currently unavailable.'}
                  </div>
                )}
              </>
            )}
          </section>
        )}

        <p className="mt-8 text-center text-xs leading-5 text-[var(--text-muted)]">
          Paid plans are prepaid. Payment status is confirmed by the UniOS
          backend; closing the checkout window does not itself confirm a
          successful or failed payment.
        </p>
      </div>
    </main>
  );
}
