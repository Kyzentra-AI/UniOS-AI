
'use client';

import { useState } from 'react';
import Link from 'next/link';

import {
  useAnalyzeResume,
  useATSHistory,
} from '@/hooks/useLaunch';
import {
  ATSState,
  LaunchLoadingState,
} from '@/components/launch/states/LaunchStates';
import type {
  ATSFinding,
  ATSFindingSeverity,
} from '@/types/launch';

const inputClass =
  'w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-3 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--primary)]';

const severityStyle: Record<ATSFindingSeverity, string> = {
  info: 'bg-[var(--primary-soft)] text-[var(--primary)]',
  warning: 'bg-[var(--feature-orange-soft)] text-[var(--feature-orange)]',
  critical: 'bg-[var(--danger-soft)] text-[var(--danger-text)]',
};

const categoryLabel: Record<ATSFinding['category'], string> = {
  structure: 'Structure',
  content: 'Content',
  formatting: 'Formatting',
  contact_information: 'Contact information',
  missing_information: 'Missing information',
  readability: 'Readability',
};

export default function ATS() {
  const [file, setFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState('');
  const [notice, setNotice] = useState('');

  const analyze = useAnalyzeResume();
  const history = useATSHistory();

  const validateFile = (selected: File | null) => {
    setFileError('');
    setNotice('');

    if (!selected) {
      setFile(null);
      return;
    }

    const extension = selected.name.split('.').pop()?.toLowerCase();
    const supportedExtension = extension === 'pdf' || extension === 'docx';
    const supportedMime = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/octet-stream',
      '',
    ].includes(selected.type);

    if (!supportedExtension || !supportedMime) {
      setFile(null);
      setFileError('Choose a PDF or DOCX resume.');
      return;
    }

    if (selected.size === 0) {
      setFile(null);
      setFileError('The selected file is empty.');
      return;
    }

    setFile(selected);
  };

  const submit = async () => {
    if (!file) {
      setFileError('Select a PDF or DOCX resume first.');
      return;
    }

    setFileError('');
    setNotice('');

    try {
      await analyze.mutateAsync(file);
      setNotice('The server returned an analysis response.');
      setFile(null);
    } catch (error) {
      setNotice(
        error instanceof Error
          ? error.message
          : 'Analysis failed. No score or findings were fabricated.',
      );
    }
  };

  const result = analyze.data?.analysis;

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <Link
        href="/launch"
        className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)]"
      >
        ← Back to Launch
      </Link>

      <header className="mb-8 mt-5">
        <p className="text-sm font-medium text-[var(--feature-blue)]">
          RESUME QUALITY
        </p>
        <h1 className="mt-2 text-3xl font-semibold text-[var(--text-primary)]">
          ATS Resume Checker
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">
          Upload a resume to review the findings produced by the
          implemented analysis checks. A score appears only when the
          server returns one with its methodology.
        </p>
      </header>

      <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-7">
        <h2 className="text-lg font-semibold text-[var(--text-primary)]">
          Upload your resume
        </h2>
        <p className="mt-2 text-sm text-[var(--text-secondary)]">
          Supported frontend selections: PDF and DOCX. Actual support,
          file limits and parsing are enforced by the server.
        </p>

        <label className="mt-5 block">
          <span className="mb-2 block text-sm font-medium text-[var(--text-label)]">
            Resume document
          </span>
          <input
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={(event) => validateFile(event.target.files?.[0] ?? null)}
            className={inputClass}
          />
        </label>

        {file && (
          <div className="mt-4 rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-4">
            <p className="font-medium text-[var(--text-primary)]">
              {file.name}
            </p>
            <p className="mt-1 text-xs text-[var(--text-secondary)]">
              {(file.size / 1024).toFixed(1)} KB
            </p>
          </div>
        )}

        {fileError && (
          <p role="alert" className="mt-3 text-sm text-[var(--danger-text)]">
            {fileError}
          </p>
        )}

        <button
          type="button"
          disabled={!file || analyze.isPending}
          onClick={() => void submit()}
          className="mt-5 rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-medium text-white hover:bg-[var(--primary-hover)] disabled:cursor-not-allowed disabled:opacity-50"
        >
          {analyze.isPending ? 'Analyzing...' : 'Analyze resume'}
        </button>

        {analyze.isPending && (
          <div className="mt-5">
            <LaunchLoadingState message="Waiting for the actual analysis response..." />
          </div>
        )}

        {notice && !analyze.isPending && (
          <p role="status" className="mt-4 rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-4 text-sm text-[var(--text-primary)]">
            {notice}
          </p>
        )}

        {analyze.isError && (
          <div className="mt-5">
            <ATSState
              kind="error"
              title="Analysis request failed"
              message={analyze.error.message}
              action={
                file ? (
                  <button
                    type="button"
                    onClick={() => void submit()}
                    className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm text-white"
                  >
                    Retry analysis
                  </button>
                ) : undefined
              }
            />
          </div>
        )}
      </section>

      {result && (
        <section className="mt-8 space-y-5">
          {result.status === 'failed' ? (
            <ATSState
              kind="error"
              title="Analysis could not be completed"
              message={result.summary || 'The server reported a failed analysis.'}
            />
          ) : (
            <>
              <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-7">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p className="text-xs font-medium uppercase tracking-wide text-[var(--text-muted)]">
                      Analysis result
                    </p>
                    <h2 className="mt-2 break-all text-xl font-semibold text-[var(--text-primary)]">
                      {result.document.fileName}
                    </h2>
                    <p className="mt-2 text-sm text-[var(--text-secondary)]">
                      {result.document.fileType.toUpperCase()}
                      {' · '}
                      {result.document.pageCount === null
                        ? 'Page count unavailable'
                        : `${result.document.pageCount} page(s)`}
                      {' · '}
                      {result.document.extractedCharacterCount.toLocaleString()} extracted characters
                    </p>
                  </div>

                  <span className="rounded-full bg-[var(--primary-soft)] px-3 py-1.5 text-xs font-medium text-[var(--primary)]">
                    Completed
                  </span>
                </div>

                {result.score ? (
                  <div className="mt-6 rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-5">
                    <p className="text-sm text-[var(--text-secondary)]">
                      ATS score
                    </p>
                    <p className="mt-1 text-3xl font-semibold text-[var(--text-primary)]">
                      {result.score.value}
                      <span className="text-lg text-[var(--text-muted)]">
                        {' '}/ {result.score.maxValue}
                      </span>
                    </p>
                    <p className="mt-3 text-sm text-[var(--text-secondary)]">
                      Methodology: {result.score.methodology}
                    </p>
                    <p className="mt-1 text-xs text-[var(--text-muted)]">
                      Version: {result.score.methodologyVersion}
                    </p>
                  </div>
                ) : (
                  <div className="mt-6 rounded-xl border border-[var(--border)] p-4">
                    <p className="font-medium text-[var(--text-primary)]">
                      No score available
                    </p>
                    <p className="mt-1 text-sm text-[var(--text-secondary)]">
                      The server did not return a documented score.
                      Review the actual findings below instead.
                    </p>
                  </div>
                )}

                <div className="mt-6">
                  <h3 className="font-semibold text-[var(--text-primary)]">
                    Summary
                  </h3>
                  <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-[var(--text-secondary)]">
                    {result.summary || 'No summary was provided by the server.'}
                  </p>
                </div>
              </div>

              <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-7">
                <h3 className="text-lg font-semibold text-[var(--text-primary)]">
                  Findings and recommendations
                </h3>

                {result.findings.length === 0 ? (
                  <div className="mt-5">
                    <ATSState
                      kind="empty"
                      title="No findings returned"
                      message="The analysis response contains no findings. This does not automatically mean the resume is perfect."
                    />
                  </div>
                ) : (
                  <div className="mt-5 space-y-4">
                    {result.findings.map((finding) => (
                      <article
                        key={finding.id}
                        className="rounded-xl border border-[var(--border)] p-4 sm:p-5"
                      >
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-xs font-medium text-[var(--text-secondary)]">
                            {categoryLabel[finding.category]}
                          </span>
                          <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${severityStyle[finding.severity]}`}>
                            {finding.severity}
                          </span>
                        </div>
                        <h4 className="mt-3 font-semibold text-[var(--text-primary)]">
                          {finding.title}
                        </h4>
                        <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                          {finding.description}
                        </p>
                        <div className="mt-3 rounded-lg bg-[var(--surface-alt)] p-3">
                          <p className="text-xs font-semibold uppercase tracking-wide text-[var(--text-label)]">
                            Recommendation
                          </p>
                          <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
                            {finding.recommendation}
                          </p>
                        </div>
                      </article>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </section>
      )}

      <section className="mt-10">
        <h2 className="mb-4 text-xl font-semibold text-[var(--text-primary)]">
          Analysis history
        </h2>

        {history.isPending ? (
          <LaunchLoadingState message="Loading your analysis history..." />
        ) : history.isError ? (
          <ATSState
            kind="error"
            message={history.error.message}
            action={
              <button
                onClick={() => void history.refetch()}
                className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm text-white"
              >
                Retry
              </button>
            }
          />
        ) : history.data.items.length === 0 ? (
          <ATSState
            kind="empty"
            title="No previous analyses"
            message="Completed analyses will appear here when available from the server."
          />
        ) : (
          <div className="space-y-3">
            {history.data.items.map((item) => (
              <article
                key={item.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4"
              >
                <div className="min-w-0">
                  <p className="break-all font-medium text-[var(--text-primary)]">
                    {item.document.fileName}
                  </p>
                  <p className="mt-1 text-xs text-[var(--text-secondary)]">
                    {new Date(item.createdAt).toLocaleString()}
                    {' · '}
                    {item.status}
                  </p>
                </div>
                <div className="text-right">
                  {item.score ? (
                    <p className="font-semibold text-[var(--text-primary)]">
                      {item.score.value}/{item.score.maxValue}
                    </p>
                  ) : (
                    <p className="text-sm text-[var(--text-muted)]">
                      No score
                    </p>
                  )}
                  <p className="text-xs text-[var(--text-secondary)]">
                    {item.findings.length} finding(s)
                  </p>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
