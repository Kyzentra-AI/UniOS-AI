
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import RoadmapSummary from "@/components/roadmap/RoadmapSummary";
import CurrentMissions from "@/components/roadmap/CurrentMissions";
import { useRoadmap } from "@/hooks/useRoadmap";
import { useBilling } from "@/hooks/useBilling";
import { stagger } from "@/components/roadmap/UI";
import ProtectedRoute from "@/components/ProtectedRoute";

const PROMOTION_DISMISS_KEY = "unios_trial_promotion_dismissed";

export default function DashboardPage() {
  const router = useRouter();

  const {
    roadmap,
    availableSubjects,
  } = useRoadmap();

  const {
    entitlement,
    activateTrial,
    isActivatingTrial,
    refreshBilling,
  } = useBilling();

  const [promotionReady, setPromotionReady] = useState(false);
  const [promotionDismissed, setPromotionDismissed] = useState(false);
  const [trialMessage, setTrialMessage] = useState("");
  const [trialError, setTrialError] = useState("");

  useEffect(() => {
    try {
      const dismissed =
        window.sessionStorage.getItem(PROMOTION_DISMISS_KEY) === "true";

      setPromotionDismissed(dismissed);
    } catch {
      setPromotionDismissed(false);
    }

    setPromotionReady(true);
  }, []);

  useEffect(() => {
    if (!promotionReady || promotionDismissed) {
      return;
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        dismissPromotion();
      }
    }

    window.addEventListener("keydown", handleEscape);

    return () => {
      window.removeEventListener("keydown", handleEscape);
    };
  }, [promotionReady, promotionDismissed]);

  function dismissPromotion() {
    setPromotionDismissed(true);

    try {
      window.sessionStorage.setItem(
        PROMOTION_DISMISS_KEY,
        "true"
      );
    } catch {
      // The popup can still be dismissed if storage is unavailable.
    }
  }

  function openBilling() {
    dismissPromotion();
    router.push("/billing");
  }

  async function handleActivateTrial() {
    setTrialMessage("");
    setTrialError("");

    try {
      const result = await activateTrial();

      if (result.success) {
        setTrialMessage(
          result.message || "Your free trial has been activated."
        );

        dismissPromotion();

        await refreshBilling();
      } else {
        setTrialError(
          result.message || "Unable to activate your free trial."
        );
      }
    } catch (error) {
      setTrialError(
        error instanceof Error
          ? error.message
          : "Unable to activate your free trial. Please try again."
      );
    }
  }

  const totalMissions = availableSubjects.reduce(
    (sum, subject) => sum + subject.total_missions,
    0
  );

  const completedMissions = availableSubjects.reduce(
    (sum, subject) => sum + subject.completed_missions,
    0
  );

  const overallProgress =
    totalMissions > 0
      ? Math.round(
          (completedMissions / totalMissions) * 100
        )
      : 0;

  const isTrialActive = entitlement?.isTrial === true;

  const isFreePlan =
    entitlement?.currentPlan === "FREE" &&
    !isTrialActive;

  const shouldShowPromotion =
    promotionReady &&
    !promotionDismissed &&
    isFreePlan;

  const canActivateTrial =
    entitlement?.trialUsed === false;

  return (
    <ProtectedRoute>
      <main className="min-h-screen bg-[radial-gradient(44rem_15rem_at_0%_0%,var(--primary-soft),transparent_70%)] bg-no-repeat px-4 pb-16 pt-6 sm:px-6 sm:pt-12">
        <div className="mx-auto max-w-6xl">
          <header className="rise mb-8 sm:mb-10">
            <h1 className="text-[26px] font-semibold leading-tight tracking-tight text-[var(--text-primary)] sm:text-4xl">
              Welcome to Unios
            </h1>

            <p className="mt-2 max-w-xl text-[15px] leading-6 text-[var(--text-secondary)]">
              Pick up where you left off and keep your learning on track.
            </p>
          </header>

          {trialMessage && (
            <div
              role="status"
              className="mb-6 flex flex-col gap-3 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <p className="text-sm font-medium text-[var(--text-primary)]">
                {trialMessage}
              </p>

              <Link
                href="/billing"
                className="shrink-0 text-sm font-semibold text-[var(--primary)] hover:underline"
              >
                View subscription
              </Link>
            </div>
          )}

          {isTrialActive && (
            <section className="mb-7 rounded-2xl border border-[var(--primary)]/25 bg-[var(--surface)] p-4 sm:p-5">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-[var(--primary-soft)] px-3 py-1 text-xs font-semibold text-[var(--primary)]">
                      BASIC TRIAL
                    </span>

                    {entitlement?.daysRemaining != null && (
                      <span className="text-xs text-[var(--text-secondary)]">
                        {entitlement.daysRemaining}{" "}
                        {entitlement.daysRemaining === 1
                          ? "day"
                          : "days"}{" "}
                        remaining
                      </span>
                    )}
                  </div>

                  <h2 className="mt-2 font-semibold text-[var(--text-primary)]">
                    Your free trial is active
                  </h2>

                  <p className="mt-1 text-sm text-[var(--text-secondary)]">
                    Enjoy your trial and explore the available learning features.
                  </p>
                </div>

                <Link
                  href="/billing"
                  className="shrink-0 rounded-xl border border-[var(--border)] px-4 py-2.5 text-sm font-semibold text-[var(--text-primary)] transition hover:bg-[var(--surface-alt)]"
                >
                  View plans
                </Link>
              </div>
            </section>
          )}

          {trialError && (
            <div
              role="alert"
              className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-600"
            >
              {trialError}
            </div>
          )}

          {availableSubjects.length > 0 && (
            <section
              className="rise mb-9"
              style={stagger(1)}
            >
              <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-[var(--text-primary)]">
                    Your Subjects
                  </h2>

                  <p className="mt-1 text-sm text-[var(--text-secondary)]">
                    Track your progress across individual subjects.
                  </p>
                </div>

                <Link
                  href="/roadmap"
                  className="text-sm font-medium text-[var(--primary)] transition hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                >
                  View all subjects
                </Link>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <Link
                  href="/roadmap"
                  className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 transition hover:-translate-y-0.5 hover:shadow-[0_8px_22px_rgba(24,52,58,0.07)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                >
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="font-semibold text-[var(--text-primary)]">
                      All Subjects
                    </h3>

                    <span className="text-sm font-bold text-[var(--primary)]">
                      {overallProgress}%
                    </span>
                  </div>

                  <p className="mt-1 text-xs text-[var(--text-secondary)]">
                    {completedMissions} of {totalMissions} missions completed
                  </p>

                  <div
                    className="mt-3 h-2 overflow-hidden rounded-full bg-[var(--surface-alt)]"
                    role="progressbar"
                    aria-valuenow={overallProgress}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label="All subjects progress"
                  >
                    <div
                      className="bar-grow h-full rounded-full bg-[var(--primary)]"
                      style={{ width: `${overallProgress}%` }}
                    />
                  </div>
                </Link>

                {availableSubjects.map(
  (subject: (typeof availableSubjects)[number], index: number) => {
                  const progress = Math.min(
                    100,
                    Math.max(0, subject.progress_percentage)
                  );

                  return (
                    <Link
                      key={subject.name}
                      href={`/roadmap?subject=${encodeURIComponent(subject.name)}`}
                      className="rise rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 transition hover:-translate-y-0.5 hover:shadow-[0_8px_22px_rgba(24,52,58,0.07)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                      style={stagger(index + 2)}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <h3 className="line-clamp-1 font-semibold text-[var(--text-primary)]">
                          {subject.name}
                        </h3>

                        <span className="shrink-0 text-sm font-bold text-[var(--primary)]">
                          {progress}%
                        </span>
                      </div>

                      <p className="mt-1 text-xs text-[var(--text-secondary)]">
                        {subject.completed_missions} of{" "}
                        {subject.total_missions} missions completed
                      </p>

                      <div
                        className="mt-3 h-2 overflow-hidden rounded-full bg-[var(--surface-alt)]"
                        role="progressbar"
                        aria-valuenow={progress}
                        aria-valuemin={0}
                        aria-valuemax={100}
                        aria-label={`${subject.name} progress`}
                      >
                        <div
                          className="bar-grow h-full rounded-full bg-[var(--primary)]"
                          style={{ width: `${progress}%` }}
                        />
                      </div>

                      {subject.in_progress_missions > 0 && (
                        <p className="mt-2 text-[11px] text-[var(--text-muted)]">
                          {subject.in_progress_missions} currently in progress
                        </p>
                      )}
                    </Link>
                  );
                })}
              </div>
            </section>
          )}

          <div className="grid gap-8 sm:gap-10 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)] lg:items-start">
            {roadmap && (
              <div
                className="rise"
                style={stagger(1)}
              >
                <CurrentMissions missions={roadmap.missions} />
              </div>
            )}

            <div
              className={`rise ${roadmap ? "" : "lg:col-span-2 lg:max-w-xl"}`}
              style={stagger(2)}
            >
              <RoadmapSummary />
            </div>
          </div>
        </div>

        {shouldShowPromotion && (
          <div
            className="fixed inset-0 z-[100] flex items-center justify-center overflow-y-auto bg-black/50 px-4 py-6 backdrop-blur-[3px]"
            role="presentation"
            onMouseDown={(event) => {
              if (event.target === event.currentTarget) {
                dismissPromotion();
              }
            }}
          >
            <section
              role="dialog"
              aria-modal="true"
              aria-labelledby="trial-promotion-title"
              aria-describedby="trial-promotion-description"
              className="relative my-auto w-full max-w-md overflow-hidden rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-2xl sm:p-8"
            >
              <button
                type="button"
                onClick={dismissPromotion}
                aria-label="Close free trial promotion"
                className="absolute right-4 top-4 flex h-9 w-9 items-center justify-center rounded-full text-[var(--text-secondary)] transition hover:bg-[var(--surface-alt)] hover:text-[var(--text-primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  className="h-5 w-5"
                  aria-hidden="true"
                >
                  <path d="m18 6-12 12M6 6l12 12" />
                </svg>
              </button>

              <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--primary-soft)] text-[var(--primary)]">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.7"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-7 w-7"
                  aria-hidden="true"
                >
                  <path d="M12 3v3" />
                  <path d="M18.4 5.6 16.3 7.7" />
                  <path d="M21 12h-3" />
                  <path d="M18.4 18.4 16.3 16.3" />
                  <path d="M12 18v3" />
                  <path d="M5.6 18.4 7.7 16.3" />
                  <path d="M3 12h3" />
                  <path d="M5.6 5.6 7.7 7.7" />
                  <circle cx="12" cy="12" r="4" />
                </svg>
              </div>

              <span className="inline-flex rounded-full bg-[var(--primary-soft)] px-3 py-1 text-xs font-semibold text-[var(--primary)]">
                {canActivateTrial ? "FREE PLAN" : "YOUR FREE PLAN"}
              </span>

              <h2
                id="trial-promotion-title"
                className="mt-4 text-2xl font-bold tracking-tight text-[var(--text-primary)] sm:text-3xl"
              >
                {canActivateTrial
                  ? "Try UniOS Basic free for 3 days"
                  : "Explore more with UniOS"}
              </h2>

              <p
                id="trial-promotion-description"
                className="mt-3 text-sm leading-6 text-[var(--text-secondary)]"
              >
                {canActivateTrial
                  ? "Activate your one-time 72-hour trial and explore the premium learning experience."
                  : "Explore our subscription plans to unlock more learning and career features."}
              </p>

              {canActivateTrial && (
                <div className="mt-5 space-y-3 rounded-2xl bg-[var(--surface-alt)] p-4">
                  <div className="flex items-start gap-3">
                    <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[var(--primary-soft)] text-xs font-bold text-[var(--primary)]">
                      ✓
                    </span>

                    <p className="text-sm text-[var(--text-primary)]">
                      Explore Basic plan features during your trial
                    </p>
                  </div>

                  <div className="flex items-start gap-3">
                    <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[var(--primary-soft)] text-xs font-bold text-[var(--primary)]">
                      ✓
                    </span>

                    <p className="text-sm text-[var(--text-primary)]">
                      See how UniOS can support your learning journey
                    </p>
                  </div>
                </div>
              )}

              <div className="mt-7 space-y-3">
                {canActivateTrial && (
                  <button
                    type="button"
                    onClick={handleActivateTrial}
                    disabled={isActivatingTrial}
                    className="flex w-full items-center justify-center rounded-xl bg-[var(--primary)] px-5 py-3.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {isActivatingTrial
                      ? "Activating your trial..."
                      : "Activate free trial"}
                  </button>
                )}

                <button
                  type="button"
                  onClick={openBilling}
                  className="flex w-full items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface)] px-5 py-3.5 text-sm font-semibold text-[var(--text-primary)] transition hover:bg-[var(--surface-alt)]"
                >
                  Explore subscription plans
                </button>
              </div>

              {trialError && (
                <p
                  role="alert"
                  className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-600"
                >
                  {trialError}
                </p>
              )}

              <p className="mt-5 text-center text-xs leading-5 text-[var(--text-muted)]">
                You can close this window and continue learning. You can
                explore subscription plans anytime from the billing page.
              </p>
            </section>
          </div>
        )}
      </main>
    </ProtectedRoute>
  );
}
