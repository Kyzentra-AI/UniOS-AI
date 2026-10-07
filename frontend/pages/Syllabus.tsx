'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Upload,
  FileText,
  CircleAlert,
  CheckCircle2,
  Plus,
  Trash2,
} from 'lucide-react';

import { useSyllabus } from '@/hooks/useSyllabus';
import { useRoadmap } from '@/hooks/useRoadmap';

import type {
  ParsedSyllabusContent,
  SyllabusSubject,
} from '@/types/syllabus';

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
      <main className="min-h-screen bg-[var(--background)] px-4 py-8 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <div className="mb-8">
            <p className="mb-2 text-sm font-semibold text-[var(--primary)]">
              Learning Setup
            </p>

            <h1 className="text-3xl font-bold tracking-tight text-[var(--text-primary)]">
              Add your syllabus
            </h1>

            <p className="mt-2 max-w-2xl text-[var(--text-secondary)]">
              Upload your syllabus so UniOS can
              understand your subjects and topics
              and build your learning roadmap.
            </p>
          </div>

          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-[var(--text-primary)]">
                Syllabus
              </h2>

              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                Upload your syllabus as a PDF.
              </p>
            </div>

            <label
              htmlFor="syllabus-upload"
              className="flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-[var(--border)] px-6 py-12 text-center transition hover:border-[var(--primary)]"
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--background)]">
                <Upload
                  size={22}
                  className="text-[var(--primary)]"
                />
              </div>

              <p className="font-medium text-[var(--text-primary)]">
                Upload your syllabus
              </p>

              <p className="mt-1 text-sm text-[var(--text-secondary)]">
                PDF files are supported
              </p>

              <input
                id="syllabus-upload"
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>

            {selectedFile && (
              <div className="mt-5 flex items-center justify-between rounded-xl border border-[var(--border)] bg-[var(--background)] p-4">
                <div className="flex min-w-0 items-center gap-3">
                  <FileText
                    size={20}
                    className="shrink-0 text-[var(--primary)]"
                  />

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
              </div>
            )}

            {errorMessage && (
              <div className="mt-5 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                <CircleAlert
                  size={18}
                  className="mt-0.5 shrink-0"
                />

                <p>{errorMessage}</p>
              </div>
            )}

            <div className="mt-6 flex justify-end">
              <button
                type="button"
                onClick={handleUpload}
                disabled={
                  !selectedFile ||
                  isUploading
                }
                className="rounded-xl bg-[var(--primary)] px-5 py-2.5 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isUploading
                  ? 'Uploading...'
                  : 'Upload syllabus'}
              </button>
            </div>
          </section>
        </div>
      </main>
    );
  }

  /*
   * Processing screen
   */
  if (isProcessing) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--background)] px-6">
        <div className="w-full max-w-md text-center">
          <div className="mx-auto mb-5 h-10 w-10 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--primary)]" />

          <h1 className="text-2xl font-semibold text-[var(--text-primary)]">
            Processing your syllabus
          </h1>

          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            We are extracting your subjects and
            topics. This may take a little while.
          </p>
        </div>
      </main>
    );
  }

  /*
   * Failed processing
   */
  if (isFailed) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--background)] px-6">
        <div className="w-full max-w-md text-center">
          <CircleAlert
            size={40}
            className="mx-auto text-[var(--danger)]"
          />

          <h1 className="mt-4 text-2xl font-semibold text-[var(--text-primary)]">
            Syllabus processing failed
          </h1>

          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            We could not process your syllabus.
            You can try processing it again.
          </p>

          {errorMessage && (
            <p className="mt-3 text-sm text-[var(--danger-text)]">
              {errorMessage}
            </p>
          )}

          <button
            type="button"
            onClick={handleReprocess}
            disabled={isReprocessing}
            className="mt-6 rounded-xl bg-[var(--primary)] px-5 py-2.5 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50"
          >
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
      <main className="flex min-h-screen items-center justify-center bg-[var(--background)] px-6">
        <div className="w-full max-w-md text-center">
          <CheckCircle2
            size={44}
            className="mx-auto text-[var(--primary)]"
          />

          <h1 className="mt-4 text-2xl font-semibold text-[var(--text-primary)]">
            Syllabus confirmed
          </h1>

          <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
            Your syllabus has been saved successfully.
            You can now generate your learning roadmap.
          </p>

          {errorMessage && (
            <div className="mt-5 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-left text-sm text-red-700">
              <CircleAlert
                size={18}
                className="mt-0.5 shrink-0"
              />

              <p>{errorMessage}</p>
            </div>
          )}

          <button
            type="button"
            onClick={handleGenerateRoadmap}
            disabled={isGenerating}
            className="mt-6 w-full rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50"
          >
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
  return (
    <main className="min-h-screen bg-[var(--background)] px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-5xl">
        <div className="mb-8">
          <p className="mb-2 text-sm font-semibold text-[var(--primary)]">
            Review Syllabus
          </p>

          <h1 className="text-3xl font-bold tracking-tight text-[var(--text-primary)]">
            Check your syllabus
          </h1>

          <p className="mt-2 max-w-2xl text-[var(--text-secondary)]">
            Review the subjects and topics extracted
            from your syllabus. You can edit them before
            confirming.
          </p>
        </div>

        {isLoadingSyllabus ? (
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <p className="text-sm text-[var(--text-secondary)]">
              Loading extracted syllabus...
            </p>
          </section>
        ) : editedContent ? (
          <section className="space-y-5">
            {editedContent.subjects.map(
              (
                subject: SyllabusSubject,
                subjectIndex
              ) => (
                <article
                  key={subjectIndex}
                  className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <label className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
                        Subject
                      </label>

                      <input
                        value={subject.name}
                        onChange={(event) =>
                          handleSubjectNameChange(
                            subjectIndex,
                            event.target.value
                          )
                        }
                        className="mt-2 w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm font-semibold text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]"
                      />
                    </div>

                    <button
                      type="button"
                      onClick={() =>
                        handleRemoveSubject(
                          subjectIndex
                        )
                      }
                      className="mt-6 rounded-lg p-2 text-[var(--text-muted)] transition hover:text-[var(--danger)]"
                      aria-label="Remove subject"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>

                  <div className="mt-6">
                    <div className="mb-3 flex items-center justify-between">
                      <label className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
                        Topics
                      </label>

                      <button
                        type="button"
                        onClick={() =>
                          handleAddTopic(
                            subjectIndex
                          )
                        }
                        className="flex items-center gap-1.5 text-xs font-semibold text-[var(--primary)]"
                      >
                        <Plus size={15} />
                        Add topic
                      </button>
                    </div>

                    <div className="space-y-3">
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
                              onChange={(event) =>
                                handleTopicChange(
                                  subjectIndex,
                                  topicIndex,
                                  event.target.value
                                )
                              }
                              className="flex-1 rounded-xl border border-[var(--border)] bg-[var(--background)] px-4 py-2.5 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]"
                            />

                            <button
                              type="button"
                              onClick={() =>
                                handleRemoveTopic(
                                  subjectIndex,
                                  topicIndex
                                )
                              }
                              className="rounded-lg p-2 text-[var(--text-muted)] transition hover:text-[var(--danger)]"
                              aria-label="Remove topic"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                </article>
              )
            )}

            <button
              type="button"
              onClick={handleAddSubject}
              className="flex w-full items-center justify-center gap-2 rounded-2xl border-2 border-dashed border-[var(--border)] px-5 py-4 text-sm font-semibold text-[var(--primary)] transition hover:border-[var(--primary)]"
            >
              <Plus size={18} />
              Add subject
            </button>

            {errorMessage && (
              <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                <CircleAlert
                  size={18}
                  className="mt-0.5 shrink-0"
                />

                <p>{errorMessage}</p>
              </div>
            )}

            <div className="flex flex-col justify-end gap-3 pt-2 sm:flex-row">
              <button
                type="button"
                onClick={handleSaveEdits}
                disabled={
                  isUpdatingParsedContent ||
                  isConfirming
                }
                className="rounded-xl border border-[var(--border)] bg-[var(--surface)] px-5 py-2.5 text-sm font-semibold text-[var(--text-primary)] transition hover:bg-[var(--background)] disabled:cursor-not-allowed disabled:opacity-50"
              >
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
                className="rounded-xl bg-[var(--primary)] px-5 py-2.5 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isConfirming
                  ? 'Confirming...'
                  : 'Looks Good — Confirm'}
              </button>
            </div>
          </section>
        ) : (
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6">
            <p className="text-sm text-[var(--text-secondary)]">
              No parsed syllabus content is available yet.
            </p>
          </section>
        )}
      </div>
    </main>
  );
}