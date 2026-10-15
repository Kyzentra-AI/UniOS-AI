
'use client';

import type { ReactNode } from 'react';

type StateProps = {
  title?: string;
  message?: string;
  action?: ReactNode;
};

function StateShell({
  title,
  message,
  action,
  icon,
}: StateProps & { icon: ReactNode }) {
  return (
    <div className="flex min-h-56 flex-col items-center justify-center rounded-2xl border border-[var(--border)] bg-[var(--surface)] px-6 py-10 text-center">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-[var(--primary-soft)] text-xl text-[var(--primary)]">
        {icon}
      </div>
      <h3 className="text-base font-semibold text-[var(--text-primary)]">
        {title}
      </h3>
      {message && (
        <p className="mt-2 max-w-md text-sm leading-6 text-[var(--text-secondary)]">
          {message}
        </p>
      )}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

export function LaunchLoadingState({
  message = 'Loading your workspace...',
}: { message?: string }) {
  return (
    <StateShell
      icon={<span className="animate-pulse">◌</span>}
      title="Just a moment"
      message={message}
    />
  );
}

export function LaunchErrorState({
  message = 'We could not load this information. Please try again.',
  action,
}: StateProps) {
  return (
    <StateShell
      icon={<span>!</span>}
      title="Something went wrong"
      message={message}
      action={action}
    />
  );
}

export function LaunchEmptyState({
  title = 'Nothing here yet',
  message = 'Your saved information will appear here when available.',
  action,
}: StateProps) {
  return (
    <StateShell
      icon={<span>＋</span>}
      title={title}
      message={message}
      action={action}
    />
  );
}

export function LaunchStates({
  kind,
  ...props
}: StateProps & {
  kind: 'loading' | 'error' | 'empty';
}) {
  if (kind === 'loading') return <LaunchLoadingState {...props} />;
  if (kind === 'error') return <LaunchErrorState {...props} />;
  return <LaunchEmptyState {...props} />;
}

export function ResumeState({
  kind,
  ...props
}: StateProps & {
  kind: 'loading' | 'error' | 'empty';
}) {
  const defaults = {
    loading: {
      title: 'Loading resumes',
      message: 'Fetching your saved resume information...',
    },
    error: {
      title: 'Unable to load resumes',
      message: 'Your saved resumes could not be retrieved.',
    },
    empty: {
      title: 'No saved resumes',
      message: 'Create a resume manually or start with your profile.',
    },
  }[kind];

  return (
    <LaunchStates
      kind={kind}
      title={props.title ?? defaults.title}
      message={props.message ?? defaults.message}
      action={props.action}
    />
  );
}

export function ATSState({
  kind,
  ...props
}: StateProps & {
  kind: 'loading' | 'error' | 'empty';
}) {
  const defaults = {
    loading: {
      title: 'Analyzing your resume',
      message: 'Please wait while the analysis is processed.',
    },
    error: {
      title: 'Analysis unavailable',
      message: 'We could not complete the request. No score has been generated.',
    },
    empty: {
      title: 'Ready to check your resume?',
      message: 'Upload a PDF or DOCX file to begin.',
    },
  }[kind];

  return (
    <LaunchStates
      kind={kind}
      title={props.title ?? defaults.title}
      message={props.message ?? defaults.message}
      action={props.action}
    />
  );
}
