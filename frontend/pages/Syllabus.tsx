'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Upload,
  FileText,
  CircleAlert,
  Check,
  Plus,
  Trash2,
} from 'lucide-react';

import { useSyllabus } from '@/hooks/useSyllabus';
import { useRoadmap } from '@/hooks/useRoadmap';
import { Chevron, Node, stagger } from '@/components/roadmap/UI';

import type {
  ParsedSyllabusContent,
  SyllabusSubject,
} from '@/types/syllabus';

const primaryBtn =
  'inline-flex items-center justify-center gap-2 rounded-xl bg-[var(--primary)] px-5 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2';
const ghostBtn =
  'inline-flex items-center justify-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-5 py-2.5 text-sm font-semibold text-[var(--text-primary)] transition hover:border-[var(--primary)] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]';
const fieldClass =
  'w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-3.5 py-2.5 text-sm text-[var(--text-primary)] outline-none transition placeholder:text-[var(--text-muted)] focus:border-[var(--primary)] focus:shadow-[0_0_0_4px_var(--primary-soft)]';
const card =
  'rounded-3xl border border-[var(--border)] bg-[var(--surface)] shadow-[0_8px_28px_rgba(24,52,58,0.04)]';

function Spinner() {
  return (
    <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
  );
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <div
      role="alert"
      className="rise flex items-start gap-3 rounded-2xl border border-red-500/30 bg-red-500/5 p-4 text-left text-sm text-red-600"
    >
      <CircleAlert size={18} className="mt-0.5 shrink-0" />
      <p className="min-w-0 break-words">{message}</p>
    </div>
  );
}

export default function Syllabus() {
  const router = useRouter();

  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [syllabusId, setSyllabusId] =
    useState<string | null>(null);

  const [actionError, setActionError] =
    useState<string | null>(null);

  const [editedContent, setEditedContent] =
    useState<ParsedSyllabusContent | null>(null);

  // Presentation only: which subject rows are expanded.
  const [openSubjects, setOpenSubjects] =
    useState<Record<number, boolean>>({});

  const {
    uploadSyllabus,
    isUploading,
    uploadError,

    status,
    isLoadingStatus,
    statusError,

    syllabus,
    isLoadingSyllabus,
    syllabusError,

    updateParsedContent,
    isUpdatingParsedContent,
    updateParsedContentError,

    confirmSyllabus,
    isConfirming,
    confirmError,

    reprocessSyllabus,
    isReprocessing,
    reprocessError,
  } = useSyllabus(syllabusId ?? undefined);

  const {
    generateRoadmap,
    isGenerating,
    generateError,
  } = useRoadmap();

  /*
   * When the backend reaches WAITING_FOR_CONFIRMATION
   * and syllabus data becomes available, initialize
   * the editable local form.
   */
  useEffect(() => {
    if (!syllabus?.parsed_content) {
      return;
    }

    setEditedContent(syllabus.parsed_content);
  }, [syllabus?.parsed_content]);

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];

    if (!file) return;

    setActionError(null);
    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setActionError(
        'Please select a syllabus file.'
      );
      return;
    }

    try {
      setActionError(null);

      const response = await uploadSyllabus({
        file: selectedFile,
      });

      setSyllabusId(response.id);
    } catch (error) {
      setActionError(
        error instanceof Error
          ? error.message
          : 'Failed to upload syllabus.'
      );
    }
  };

  const handleSubjectNameChange = (
    subjectIndex: number,
    value: string
  ) => {
    setEditedContent((current) => {
      if (!current) return current;

      const subjects = [...current.subjects];

      subjects[subjectIndex] = {
        ...subjects[subjectIndex],
        name: value,
      };

      return {
        ...current,
        subjects,
      };
    });
  };

  const handleTopicChange = (
    subjectIndex: number,
    topicIndex: number,
    value: string
  ) => {
    setEditedContent((current) => {
      if (!current) return current;

      const subjects = [...current.subjects];

      const topics = [
        ...subjects[subjectIndex].topics,
      ];

      topics[topicIndex] = value;

      subjects[subjectIndex] = {
        ...subjects[subjectIndex],
        topics,
      };

      return {
        ...current,
        subjects,
      };
    });
  };

  const handleAddSubject = () => {
    if (editedContent) {
      setOpenSubjects((open) => ({
        ...open,
        [editedContent.subjects.length]: true,
      }));
    }

    setEditedContent((current) => {
      if (!current) return current;

      return {
        ...current,
        subjects: [
          ...current.subjects,
          {
            name: '',
            topics: [''],
          },
        ],
      };
    });
  };

  const handleRemoveSubject = (
    subjectIndex: number
  ) => {
    setOpenSubjects({});

    setEditedContent((current) => {
      if (!current) return current;

      return {
        ...current,
        subjects: current.subjects.filter(
          (_, index) => index !== subjectIndex
        ),
      };
    });
  };

  const handleAddTopic = (
    subjectIndex: number
  ) => {
    setEditedContent((current) => {
      if (!current) return current;

      const subjects = [...current.subjects];

      subjects[subjectIndex] = {
        ...subjects[subjectIndex],
        topics: [
          ...subjects[subjectIndex].topics,
          '',
        ],
      };

      return {
        ...current,
        subjects,
      };
    });
  };

  const handleRemoveTopic = (
    subjectIndex: number,
    topicIndex: number
  ) => {
    setEditedContent((current) => {
      if (!current) return current;

      const subjects = [...current.subjects];

      subjects[subjectIndex] = {
        ...subjects[subjectIndex],
        topics: subjects[
          subjectIndex
        ].topics.filter(
          (_, index) => index !== topicIndex
        ),
      };

      return {
        ...current,
        subjects,
      };
    });
  };

  const handleSaveEdits = async () => {
    if (!syllabusId || !editedContent) {
      return;
    }

    try {
      setActionError(null);

      await updateParsedContent({
        id: syllabusId,
        parsedContent: editedContent,
      });
    } catch (error) {
      setActionError(
        error instanceof Error
          ? error.message
          : 'Failed to update syllabus.'
      );
    }
  };

  const handleConfirm = async () => {
    if (!syllabusId) return;

    try {
      setActionError(null);

      /*
       * Save the latest edits first.
       * Then finalize the syllabus.
       */
      if (editedContent) {
        await updateParsedContent({
          id: syllabusId,
          parsedContent: editedContent,
        });
      }

      await confirmSyllabus(syllabusId);
    } catch (error) {
      setActionError(
        error instanceof Error
          ? error.message
          : 'Failed to confirm syllabus.'
      );
    }
  };

  const handleGenerateRoadmap = async () => {
    if (!syllabusId) return;

    try {
      setActionError(null);

      await generateRoadmap({
        syllabus_id: syllabusId,
        scope: 'ACADEMIC',
      });

      router.push('/roadmap');
    } catch (error) {
      setActionError(
        error instanceof Error
          ? error.message
          : 'Failed to start roadmap generation.'
      );
    }
  };

  const handleReprocess = async () => {
    if (!syllabusId) return;

    try {
      setActionError(null);
      setEditedContent(null);

      await reprocessSyllabus(syllabusId);
    } catch (error) {
      setActionError(
        error instanceof Error
          ? error.message
          : 'Failed to reprocess syllabus.'
      );
    }
  };

  const errorMessage =
    actionError ||
    (uploadError instanceof Error
      ? uploadError.message
      : null) ||
    (statusError instanceof Error
      ? statusError.message
      : null) ||
    (syllabusError instanceof Error
      ? syllabusError.message
      : null) ||
    (updateParsedContentError instanceof Error
      ? updateParsedContentError.message
      : null) ||
    (confirmError instanceof Error
      ? confirmError.message
      : null) ||
    (reprocessError instanceof Error
      ? reprocessError.message
      : null) ||
    (generateError instanceof Error
      ? generateError.message
      : null);

  const isProcessing =
    status === 'PROCESSING' ||
    isLoadingStatus;

  const isWaitingForConfirmation =
    status === 'WAITING_FOR_CONFIRMATION';

  const isConfirmed =
    status === 'CONFIRMED';

  const isFailed =
    status === 'FAILED';

  /*
   * Initial upload screen
   */
  if (!syllabusId) {
    return (
      <main className="min-h-screen bg-[var(--background)] px-4 py-8 sm:px-6 sm:py-12 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <header className="rise mb-8 sm:mb-10">
            <h1 className="text-[28px] font-bold leading-tight tracking-tight text-[var(--text-primary)] sm:text-4xl">
              Add your syllabus
            </h1>

            <p className="mt-3 max-w-2xl text-[15px] leading-6 text-[var(--text-secondary)]">
              Upload your syllabus so UniOS can
              understand your subjects and topics
              and build your learning roadmap.
            </p>
          </header>

          <div className="grid gap-8 lg:grid-cols-[1fr_1.15fr] lg:items-start lg:gap-12">
            <section className={`rise ${card} p-5 sm:p-7 lg:order-last`} style={stagger(1)}>
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">
                Syllabus
              </h2>

              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                Upload your syllabus as a PDF.
              </p>

              <label
                htmlFor="syllabus-upload"
                className="group mt-5 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-[var(--border)] px-6 py-10 text-center transition duration-200 hover:border-[var(--primary)] hover:bg-[var(--primary-soft)] focus-within:border-[var(--primary)] focus-within:shadow-[0_0_0_4px_var(--primary-soft)]"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-[var(--primary-soft)] transition-transform duration-200 group-hover:-translate-y-0.5">
                  <Upload
                    size={22}
                    className="text-[var(--primary)]"
                  />
                </div>

                <p className="font-medium text-[var(--text-primary)]">
                  {selectedFile ? 'Choose a different file' : 'Upload your syllabus'}
                </p>

                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                  PDF files are supported
                </p>

                <input
                  id="syllabus-upload"
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={handleFileChange}
                  className="sr-only"
                />
              </label>

              {selectedFile && (
                <div className="rise mt-4 flex items-center gap-3 rounded-2xl border border-[var(--border)] bg-[var(--background)] p-4">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[var(--primary-soft)]">
                    <FileText
                      size={18}
                      className="text-[var(--primary)]"
                    />
                  </span>

                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-[var(--text-primary)]">
                      {selectedFile.name}
                    </p>

                    <p className="text-xs text-[var(--text-secondary)]">
                      {(
                        selectedFile.size /
                        1024 /
                        1024
                      ).toFixed(2)}{' '}
                      MB
                    </p>
                  </div>
                </div>
              )}

              {errorMessage && (
                <div className="mt-4">
                  <ErrorBanner message={errorMessage} />
                </div>
              )}

              <div className="mt-6 flex sm:justify-end">
                <button
                  type="button"
                  onClick={handleUpload}
                  disabled={
                    !selectedFile ||
                    isUploading
                  }
                  className={`${primaryBtn} w-full sm:w-auto`}
                >
                  {isUploading && <Spinner />}
                  {isUploading
                    ? 'Uploading...'
                    : 'Upload syllabus'}
                </button>
              </div>
            </section>

            <ol className="rise relative" style={stagger(2)}>
              <span
                aria-hidden="true"
                className="line-grow absolute bottom-8 left-[14px] top-8 w-px bg-[var(--border)]"
              />
              {[
                ['Upload your syllabus', 'A PDF of your course outline.'],
                ['Review what we found', 'Check the subjects and topics, and fix anything that is off.'],
                ['Generate your roadmap', 'Missions are built from the topics you confirm.'],
              ].map(([title, text], i) => (
                <li key={title} className="relative pb-6 pl-11 last:pb-0" style={stagger(i)}>
                  <span className="absolute left-0 top-0">
                    <Node state="idle">{i + 1}</Node>
                  </span>
                  <p className="pt-1 text-sm font-semibold text-[var(--text-primary)]">{title}</p>
                  <p className="mt-0.5 text-sm leading-6 text-[var(--text-secondary)]">{text}</p>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </main>
    );
  }

  /*
   * Processing screen
   */
  if (isProcessing) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--background)] px-4 py-10 sm:px-6">
        <div
          role="status"
          aria-live="polite"
          className={`rise w-full max-w-lg ${card} p-6 sm:p-8`}
        >
          <div className="flex items-center gap-4">
            <span className="h-9 w-9 shrink-0 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />
            <div>
              <h1 className="text-xl font-semibold text-[var(--text-primary)]">
                Processing your syllabus
              </h1>

              <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
                We are extracting your subjects and
                topics. This may take a little while.
              </p>
            </div>
          </div>

          <div className="mt-6 space-y-3 border-t border-[var(--border)] pt-6" aria-hidden="true">
            {[0, 1, 2].map((n) => (
              <div key={n} className="flex items-center gap-3">
                <div className="skeleton h-8 w-8 shrink-0 rounded-full" />
                <div className="flex-1 space-y-2">
                  <div className="skeleton h-4 w-2/3 rounded-md" />
                  <div className="skeleton h-3 w-full rounded-md" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    );
  }

  /*
   * Failed processing
   */
  if (isFailed) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--background)] px-4 py-10 sm:px-6">
        <div role="alert" className={`rise w-full max-w-lg ${card} p-6 sm:p-8`}>
          <div className="flex items-center gap-2.5">
            <span
              className="h-2 w-2 shrink-0 rounded-full"
              style={{ backgroundColor: 'var(--danger)' }}
            />
            <h1 className="text-xl font-semibold text-[var(--text-primary)]">
              Syllabus processing failed
            </h1>
          </div>

          <p className="mt-2 pl-[18px] text-sm leading-6 text-[var(--text-secondary)]">
            We could not process your syllabus.
            You can try processing it again.
          </p>

          {errorMessage && (
            <div className="mt-4 pl-[18px]">
              <ErrorBanner message={errorMessage} />
            </div>
          )}

          <button
            type="button"
            onClick={handleReprocess}
            disabled={isReprocessing}
            className={`${primaryBtn} mt-6 w-full sm:ml-[18px] sm:w-auto`}
          >
            {isReprocessing && <Spinner />}
            {isReprocessing
              ? 'Reprocessing...'
              : 'Try again'}
          </button>
        </div>
      </main>
    );
  }

  /*
   * Confirmed screen
   */
  if (isConfirmed) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--background)] px-4 py-10 sm:px-6">
        <div className={`rise w-full max-w-md ${card} p-6 text-center sm:p-8`}>
          <span className="pop mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-[var(--primary)] text-white">
            <Check size={26} strokeWidth={2.5} />
          </span>

          <h1 className="mt-5 text-2xl font-semibold text-[var(--text-primary)]">
            Syllabus confirmed
          </h1>

          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            Your syllabus has been saved successfully.
            You can now generate your learning roadmap.
          </p>

          {errorMessage && (
            <div className="mt-5">
              <ErrorBanner message={errorMessage} />
            </div>
          )}

          <button
            type="button"
            onClick={handleGenerateRoadmap}
            disabled={isGenerating}
            className={`${primaryBtn} mt-6 w-full py-3`}
          >
            {isGenerating && <Spinner />}
            {isGenerating
              ? 'Generating roadmap...'
              : 'Generate Roadmap'}
          </button>
        </div>
      </main>
    );
  }

  /*
   * Parsed syllabus / confirmation screen
   */
  const subjectCount = editedContent?.subjects.length ?? 0;
  const topicCount =
    editedContent?.subjects.reduce(
      (total, subject) =>
        total + subject.topics.filter((topic) => topic.trim()).length,
      0
    ) ?? 0;
  const isSubjectOpen = (index: number) =>
    openSubjects[index] ?? subjectCount <= 3;
  const setAllOpen = (value: boolean) =>
    setOpenSubjects(
      Object.fromEntries(
        (editedContent?.subjects ?? []).map((_, index) => [index, value])
      )
    );

  return (
    <main className="min-h-screen bg-[var(--background)] px-4 py-8 sm:px-6 sm:py-12 lg:px-8">
      <div className="mx-auto max-w-4xl">
        <header className="rise mb-8">
          <h1 className="text-[28px] font-bold leading-tight tracking-tight text-[var(--text-primary)] sm:text-4xl">
            Check your syllabus
          </h1>

          <p className="mt-3 max-w-2xl text-[15px] leading-6 text-[var(--text-secondary)]">
            Review the subjects and topics extracted
            from your syllabus. You can edit them before
            confirming.
          </p>
        </header>

        {isLoadingSyllabus ? (
          <section
            role="status"
            aria-live="polite"
            className={`rise ${card} p-5 sm:p-6`}
          >
            <p className="text-sm text-[var(--text-secondary)]">
              Loading extracted syllabus...
            </p>
            <div className="mt-5 space-y-3" aria-hidden="true">
              {[0, 1, 2, 3].map((n) => (
                <div key={n} className="skeleton h-14 w-full rounded-2xl" />
              ))}
            </div>
          </section>
        ) : editedContent ? (
          <section>
            <div className="rise mb-4 flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
              <p className="text-sm text-[var(--text-secondary)]">
                <span className="font-semibold text-[var(--text-primary)]">{subjectCount}</span>{' '}
                {subjectCount === 1 ? 'subject' : 'subjects'} ·{' '}
                <span className="font-semibold text-[var(--text-primary)]">{topicCount}</span>{' '}
                {topicCount === 1 ? 'topic' : 'topics'}
              </p>

              {subjectCount > 1 && (
                <div className="flex gap-1 text-sm font-medium">
                  <button
                    type="button"
                    onClick={() => setAllOpen(true)}
                    className="rounded-lg px-2.5 py-1.5 text-[var(--primary)] transition hover:bg-[var(--primary-soft)]"
                  >
                    Expand all
                  </button>
                  <button
                    type="button"
                    onClick={() => setAllOpen(false)}
                    className="rounded-lg px-2.5 py-1.5 text-[var(--primary)] transition hover:bg-[var(--primary-soft)]"
                  >
                    Collapse all
                  </button>
                </div>
              )}
            </div>

            <ul className="space-y-2.5">
              {editedContent.subjects.map(
                (
                  subject: SyllabusSubject,
                  subjectIndex
                ) => {
                  const open = isSubjectOpen(subjectIndex);
                  const filled = subject.topics.filter((topic) => topic.trim());

                  return (
                    <li
                      key={subjectIndex}
                      className="rise"
                      style={stagger(Math.min(subjectIndex, 8))}
                    >
                      <article className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface)]">
                        <div className="flex items-center gap-1 pr-2">
                          <button
                            type="button"
                            aria-expanded={open}
                            aria-controls={`subject-panel-${subjectIndex}`}
                            onClick={() =>
                              setOpenSubjects((current) => ({
                                ...current,
                                [subjectIndex]: !isSubjectOpen(subjectIndex),
                              }))
                            }
                            className="group flex min-w-0 flex-1 items-center gap-3 p-3.5 text-left transition hover:bg-[var(--background)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-[var(--primary)] sm:p-4"
                          >
                            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--primary-soft)] text-xs font-bold text-[var(--primary)]">
                              {subjectIndex + 1}
                            </span>

                            <span className="min-w-0 flex-1">
                              <span className="block truncate font-semibold text-[var(--text-primary)]">
                                {subject.name || 'Untitled subject'}
                              </span>
                              <span className="mt-0.5 block truncate text-xs text-[var(--text-secondary)]">
                                {filled.length
                                  ? `${filled.length} ${filled.length === 1 ? 'topic' : 'topics'} · ${filled.slice(0, 3).join(', ')}${filled.length > 3 ? '…' : ''}`
                                  : 'No topics yet'}
                              </span>
                            </span>

                            <Chevron
                              className={`shrink-0 text-[var(--text-muted)] transition-transform duration-200 ${
                                open ? 'rotate-90' : ''
                              }`}
                            />
                          </button>

                          <button
                            type="button"
                            onClick={() =>
                              handleRemoveSubject(
                                subjectIndex
                              )
                            }
                            className="shrink-0 rounded-lg p-2 text-[var(--text-muted)] transition hover:text-[var(--danger)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                            aria-label="Remove subject"
                          >
                            <Trash2 size={17} />
                          </button>
                        </div>

                        <div
                          id={`subject-panel-${subjectIndex}`}
                          inert={!open}
                          className={`grid transition-[grid-template-rows] duration-300 ease-out ${
                            open ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'
                          }`}
                        >
                          <div className="overflow-hidden">
                            <div className="space-y-5 border-t border-[var(--border)] p-4 sm:p-5">
                              <div>
                                <label className="text-xs font-medium text-[var(--text-muted)]">
                                  Subject
                                  <input
                                    value={subject.name}
                                    onChange={(event) =>
                                      handleSubjectNameChange(
                                        subjectIndex,
                                        event.target.value
                                      )
                                    }
                                    className={`${fieldClass} mt-1.5 font-semibold`}
                                  />
                                </label>
                              </div>

                              <div>
                                <div className="mb-2.5 flex items-center justify-between">
                                  <span className="text-xs font-medium text-[var(--text-muted)]">
                                    Topics
                                  </span>

                                  <button
                                    type="button"
                                    onClick={() =>
                                      handleAddTopic(
                                        subjectIndex
                                      )
                                    }
                                    className="flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs font-semibold text-[var(--primary)] transition hover:bg-[var(--primary-soft)]"
                                  >
                                    <Plus size={14} />
                                    Add topic
                                  </button>
                                </div>

                                <div className="space-y-2">
                                  {subject.topics.map(
                                    (
                                      topic,
                                      topicIndex
                                    ) => (
                                      <div
                                        key={topicIndex}
                                        className="flex items-center gap-2"
                                      >
                                        <input
                                          value={topic}
                                          aria-label={`Topic ${topicIndex + 1}`}
                                          onChange={(event) =>
                                            handleTopicChange(
                                              subjectIndex,
                                              topicIndex,
                                              event.target.value
                                            )
                                          }
                                          className={`${fieldClass} flex-1`}
                                        />

                                        <button
                                          type="button"
                                          onClick={() =>
                                            handleRemoveTopic(
                                              subjectIndex,
                                              topicIndex
                                            )
                                          }
                                          className="shrink-0 rounded-lg p-2 text-[var(--text-muted)] transition hover:text-[var(--danger)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                                          aria-label="Remove topic"
                                        >
                                          <Trash2 size={16} />
                                        </button>
                                      </div>
                                    )
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </article>
                    </li>
                  );
                }
              )}
            </ul>

            <button
              type="button"
              onClick={handleAddSubject}
              className="mt-3 flex w-full items-center justify-center gap-2 rounded-2xl border-2 border-dashed border-[var(--border)] px-5 py-3.5 text-sm font-semibold text-[var(--primary)] transition hover:border-[var(--primary)] hover:bg-[var(--primary-soft)]"
            >
              <Plus size={17} />
              Add subject
            </button>

            {errorMessage && (
              <div className="mt-4">
                <ErrorBanner message={errorMessage} />
              </div>
            )}

            <div className="sticky bottom-3 z-10 mt-6 flex flex-col gap-3 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-3 shadow-[0_10px_30px_rgba(24,52,58,0.12)] sm:flex-row sm:items-center sm:justify-between sm:pl-5">
              <p className="hidden text-sm text-[var(--text-secondary)] sm:block">
                {subjectCount} {subjectCount === 1 ? 'subject' : 'subjects'} · {topicCount} {topicCount === 1 ? 'topic' : 'topics'}
              </p>

              <div className="flex flex-col gap-2 sm:flex-row">
                <button
                  type="button"
                  onClick={handleSaveEdits}
                  disabled={
                    isUpdatingParsedContent ||
                    isConfirming
                  }
                  className={ghostBtn}
                >
                  {isUpdatingParsedContent && <Spinner />}
                  {isUpdatingParsedContent
                    ? 'Saving...'
                    : 'Save changes'}
                </button>

                <button
                  type="button"
                  onClick={handleConfirm}
                  disabled={
                    isUpdatingParsedContent ||
                    isConfirming
                  }
                  className={primaryBtn}
                >
                  {isConfirming && <Spinner />}
                  {isConfirming
                    ? 'Confirming...'
                    : 'Looks Good — Confirm'}
                </button>
              </div>
            </div>
          </section>
        ) : (
          <section className="rise rounded-3xl border border-dashed border-[var(--border)] bg-[var(--surface)] px-6 py-10 text-center">
            <p className="text-sm text-[var(--text-secondary)]">
              No parsed syllabus content is available yet.
            </p>
          </section>
        )}
      </div>
    </main>
  );
}