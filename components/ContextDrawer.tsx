
'use client';

import React, { useState } from 'react';
import { X, ChevronDown, CheckCircle2, CircleAlert } from 'lucide-react';

interface ContextDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

const languages = [
  'English',
  'Hindi',
  'Marathi',
  'Kannada',
  'Tamil',
  'Bengali',
  'Telugu',
];

const deliveryModes = ['Visual', 'Story', 'Voice', 'Text'];

const frictionPoints = [
  {
    title: 'SQL Joins',
    count: 4,
  },
  {
    title: 'TCP / UDP',
    count: 3,
  },
];

export default function ContextDrawer({
  isOpen,
  onClose,
}: ContextDrawerProps) {
  const [language, setLanguage] = useState('English');
  const [deliveryMode, setDeliveryMode] = useState('Story');

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-[60] bg-black/20 backdrop-blur-[1px]"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer */}
      <aside
  className="fixed right-0 top-0 z-[70] flex h-screen w-full max-w-md flex-col border-l border-[var(--border)] bg-[var(--surface)] shadow-2xl"
  role="dialog"
  aria-modal="true"
  aria-label="AI Context"
>
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[var(--border)] px-5 py-4">
          <div>
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              AI Context
            </h2>

            <p className="mt-0.5 text-xs text-[var(--text-secondary)]">
              Your current learning context
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close AI Context"
            className="rounded-lg p-2 text-[var(--text-muted)] transition hover:bg-[var(--surface-alt)] hover:text-[var(--text-primary)]"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-6">
          {/* Language */}
          <section className="mb-7">
            <div className="mb-3">
              <h3 className="text-sm font-semibold text-[var(--text-primary)]">
                Language
              </h3>

              <p className="mt-1 text-xs text-[var(--text-secondary)]">
                Choose the language you want your AI responses in.
              </p>
            </div>

            <div className="relative">
              <select
                value={language}
                onChange={(event) => setLanguage(event.target.value)}
                className="w-full appearance-none rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] px-4 py-3 pr-10 text-sm font-medium text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]"
              >
                {languages.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>

              <ChevronDown
                size={17}
                className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-[var(--text-muted)]"
              />
            </div>
          </section>

          {/* Delivery Mode */}
          <section className="mb-7">
            <div className="mb-3">
              <h3 className="text-sm font-semibold text-[var(--text-primary)]">
                Delivery Mode
              </h3>

              <p className="mt-1 text-xs text-[var(--text-secondary)]">
                Choose how you prefer concepts to be explained.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2">
              {deliveryModes.map((mode) => {
                const isSelected = deliveryMode === mode;

                return (
                  <button
                    key={mode}
                    type="button"
                    onClick={() => setDeliveryMode(mode)}
                    className={`rounded-xl border px-4 py-3 text-sm font-medium transition ${
                      isSelected
                        ? 'border-[var(--primary)] bg-[var(--primary-soft)] text-[var(--primary)]'
                        : 'border-[var(--border)] bg-[var(--surface-alt)] text-[var(--text-secondary)] hover:border-[var(--primary)] hover:text-[var(--primary)]'
                    }`}
                  >
                    {mode}
                  </button>
                );
              })}
            </div>
          </section>

          {/* Active Friction Points */}
          <section>
            <div className="mb-3">
              <div className="flex items-center gap-2">
                <CircleAlert
                  size={17}
                  className="text-[var(--feature-orange)]"
                />

                <h3 className="text-sm font-semibold text-[var(--text-primary)]">
                  Active Friction Points
                </h3>
              </div>

              <p className="mt-1 text-xs text-[var(--text-secondary)]">
                Areas where UniOS has noticed repeated difficulty.
              </p>
            </div>

            <div className="space-y-2.5">
              {frictionPoints.length > 0 ? (
                frictionPoints.map((point) => (
                  <div
                    key={point.title}
                    className="flex items-center justify-between rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] px-4 py-3"
                  >
                    <div className="flex items-center gap-3">
                      <CheckCircle2
                        size={17}
                        className="text-[var(--primary)]"
                      />

                      <span className="text-sm font-medium text-[var(--text-primary)]">
                        {point.title}
                      </span>
                    </div>

                    <span className="text-xs text-[var(--text-muted)]">
                      Seen {point.count} times
                    </span>
                  </div>
                ))
              ) : (
                <div className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--surface-alt)] px-4 py-6 text-center">
                  <p className="text-sm text-[var(--text-muted)]">
                    No active friction points.
                  </p>
                </div>
              )}
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="border-t border-[var(--border)] px-5 py-4">
          <p className="text-xs leading-5 text-[var(--text-muted)]">
            Changes made here will influence your AI experience in real time
            once the AI context service is connected.
          </p>
        </div>
      </aside>
    </>
  );
}
