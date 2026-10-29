
'use client';

import { useState } from 'react';

const FAQS = [
  {
    question: 'What is UniOS.AI?',
    answer:
      'UniOS.AI is a platform focused on organizing student learning, projects, skill development, and career preparation.',
  },
  {
    question: 'Who can use UniOS.AI?',
    answer:
      'The platform is intended for students who want to organize their academic learning and prepare for professional opportunities.',
  },
  {
    question: 'How do I create an account?',
    answer:
      'Open the registration page, complete the available fields, and follow the instructions shown there.',
  },
  {
    question: 'Where can I access my profile?',
    answer:
      'After signing in, use the Profile link in the navigation bar to open your profile page.',
  },
  {
    question: 'How do I access my dashboard?',
    answer:
      'Sign in to your account and select Dashboard from the navigation bar.',
  },
];

export default function FAQsPage() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-[var(--background)] text-[var(--foreground)]">
      <section className="mx-auto max-w-3xl px-5 py-20 sm:px-8 sm:py-24">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[var(--primary)]">
          Resources
        </p>

        <h1 className="mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
          Frequently Asked Questions
        </h1>

        <p className="mt-5 text-base leading-7 text-[var(--text-secondary)]">
          Answers to common questions about navigating UniOS.AI.
        </p>

        <div className="mt-10 divide-y divide-[var(--border)] border-y border-[var(--border)]">
          {FAQS.map((faq, index) => {
            const isOpen = openIndex === index;

            return (
              <div key={faq.question}>
                <button
                  type="button"
                  aria-expanded={isOpen}
                  onClick={() =>
                    setOpenIndex((current) =>
                      current === index ? null : index
                    )
                  }
                  className="flex w-full items-center justify-between gap-4 py-5 text-left text-base font-medium transition hover:text-[var(--primary)]"
                >
                  <span>{faq.question}</span>

                  <span
                    aria-hidden="true"
                    className={`text-xl transition-transform ${
                      isOpen ? 'rotate-45' : ''
                    }`}
                  >
                    +
                  </span>
                </button>

                {isOpen && (
                  <p className="max-w-2xl pb-5 text-sm leading-6 text-[var(--text-secondary)]">
                    {faq.answer}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </section>
    </main>
  );
}
