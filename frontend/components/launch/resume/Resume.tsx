
'use client';

import Link from 'next/link';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useFieldArray, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import {
  generateResumeSchema,
  type GenerateResumeInput,
} from '@/app/validations/launch';

import {
  useCreateResume,
  useGenerateResume,
  useProfileResumePreview,
  useResume,
  useResumes,
  useUpdateResume,
  useExportResume,
} from '@/hooks/useLaunch';

import {
  LaunchErrorState,
  LaunchLoadingState,
  ResumeState,
} from '@/components/launch/states/LaunchStates';

import type {
  ResumeDraft,
  ResumeSource,
} from '@/types/launch';

const emptyDraft: ResumeDraft = {
  contact: {
    fullName: '',
    email: '',
    phone: '',
    location: '',
    linkedInUrl: '',
    githubUrl: '',
    portfolioUrl: '',
  },
  headline: '',
  summary: '',
  skills: [],
  education: [],
  experience: [],
  projects: [],
  achievements: [],
};

const inputClass =
  'w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary-soft)]';

const labelClass =
  'mb-1.5 block text-sm font-medium text-[var(--text-label)]';

function SectionHeading({
  title,
  onAdd,
}: {
  title: string;
  onAdd: () => void;
}) {
  return (
    <div className="mb-4 flex items-center justify-between gap-3">
      <h3 className="text-base font-semibold text-[var(--text-primary)]">
        {title}
      </h3>

      <button
        type="button"
        onClick={onAdd}
        className="rounded-lg border border-[var(--border)] px-3 py-2 text-sm font-medium text-[var(--primary)] hover:bg-[var(--primary-soft)]"
      >
        + Add
      </button>
    </div>
  );
}

function ErrorText({ message }: { message?: string }) {
  if (!message) return null;

  return (
    <span className="mt-1 block text-xs text-red-600">
      {message}
    </span>
  );
}

/* Convert technical field names into readable labels. */
function humanizeField(value: string) {
  const labels: Record<string, string> = {
    fullName: 'Full name',
    email: 'Email',
    phone: 'Phone number',
    location: 'Location',
    linkedInUrl: 'LinkedIn URL',
    githubUrl: 'GitHub URL',
    portfolioUrl: 'Portfolio URL',
    institution: 'Institution',
    degree: 'Degree',
    fieldOfStudy: 'Field of study',
    startDate: 'Start date',
    endDate: 'End date',
    grade: 'Grade / CGPA',
    company: 'Company',
    role: 'Job title',
    description: 'Description',
    name: 'Project name',
    projectUrl: 'Project URL',
    technologies: 'Technologies',
    title: 'Title',
    date: 'Date',
  };

  return labels[value] ??
    value
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, (char) => char.toUpperCase());
}

/* Convert Zod/RHF messages into simple user-facing messages. */
function friendlyMessage(
  field: string,
  message: string,
) {
  const label = humanizeField(field);
  const lower = message.toLowerCase();

  if (
    lower.includes('required') ||
    lower.includes('too_small') ||
    lower.includes('minimum') ||
    lower.includes('at least')
  ) {
    return `${label} is required.`;
  }

  if (lower.includes('email')) {
    return 'Enter a valid email address.';
  }

  if (lower.includes('url')) {
    return 'Enter a valid URL starting with https:// or http://.';
  }

  if (lower.includes('expected string')) {
    return `${label} is missing or invalid.`;
  }

  if (lower.includes('expected boolean')) {
    return `${label} has an invalid value.`;
  }

  return `${label}: Please check this value.`;
}

/* Friendly validation summary. Never display raw schema paths. */
function getFriendlyValidationMessages(
  errors: Record<string, unknown>,
) {
  const messages: string[] = [];

  const add = (message: string) => {
    if (!messages.includes(message)) {
      messages.push(message);
    }
  };

  const getMessage = (node: unknown): string | undefined => {
    if (!node || typeof node !== 'object') return undefined;

    const item = node as Record<string, unknown>;

    return typeof item.message === 'string'
      ? item.message
      : undefined;
  };

  const getChild = (
    node: unknown,
    key: string,
  ): unknown => {
    if (!node || typeof node !== 'object') return undefined;
    return (node as Record<string, unknown>)[key];
  };

  const root = errors.content;

  if (errors.title) {
    add('Resume title is required.');
  }

  const contact = getChild(root, 'contact');

  const contactFields = [
    'fullName',
    'email',
    'phone',
    'location',
    'linkedInUrl',
    'githubUrl',
    'portfolioUrl',
  ];

  for (const field of contactFields) {
    const message = getMessage(getChild(contact, field));

    if (message) {
      add(`Personal information: ${friendlyMessage(field, message)}`);
    }
  }

  const sections = [
    {
      key: 'education',
      label: 'Education',
      fields: [
        'institution',
        'degree',
        'fieldOfStudy',
        'startDate',
        'endDate',
        'grade',
      ],
    },
    {
      key: 'experience',
      label: 'Experience',
      fields: [
        'company',
        'role',
        'location',
        'startDate',
        'endDate',
        'description',
      ],
    },
    {
      key: 'projects',
      label: 'Projects',
      fields: [
        'name',
        'description',
        'projectUrl',
        'startDate',
        'endDate',
        'technologies',
      ],
    },
    {
      key: 'achievements',
      label: 'Achievements',
      fields: [
        'title',
        'description',
        'date',
      ],
    },
  ];

  for (const section of sections) {
    const sectionErrors = getChild(root, section.key);

    if (
      sectionErrors &&
      typeof sectionErrors === 'object'
    ) {
      const entries = Object.entries(sectionErrors);

      for (const [index, itemErrors] of entries) {
        if (!/^\d+$/.test(index)) continue;

        for (const field of section.fields) {
          const message = getMessage(
            getChild(itemErrors, field),
          );

          if (message) {
            add(
              `${section.label} ${Number(index) + 1}: ${friendlyMessage(field, message)}`,
            );
          }
        }
      }
    }
  }

  return messages;
}

/* Normalize API errors without exposing raw backend validation paths. */
function getFriendlyApiError(error: unknown) {
  if (!(error instanceof Error)) {
    return 'Something went wrong. Please review your details and try again.';
  }

  const message = error.message.toLowerCase();

  if (
    message.includes('validation') ||
    message.includes('required') ||
    message.includes('missing') ||
    message.includes('invalid') ||
    message.includes('unprocessable') ||
    message.includes('422')
  ) {
    return 'Some resume details are missing or invalid. Please review the highlighted sections and try again.';
  }

  if (
    message.includes('network') ||
    message.includes('fetch') ||
    message.includes('connection')
  ) {
    return 'Unable to connect to the server. Please check your connection and try again.';
  }

  if (
    message.includes('unauthorized') ||
    message.includes('401') ||
    message.includes('403')
  ) {
    return 'Your session may have expired. Please sign in again and retry.';
  }

  if (
    message.includes('500') ||
    message.includes('internal server')
  ) {
    return 'The server could not process your request right now. Please try again later.';
  }

  return 'Unable to process your resume. Please try again.';
}

function PreviewSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="mt-5">
      <h3 className="mb-2 border-b border-gray-300 pb-1 text-[11px] font-bold uppercase tracking-[0.13em] text-gray-800">
        {title}
      </h3>

      {children}
    </section>
  );
}

export default function Resume({
  resumeId,
}: {
  resumeId?: string;
}) {
  const router = useRouter();
  const params = useParams<{ resumeId?: string }>();

  const activeResumeId = resumeId ?? params?.resumeId;
  const isEditing = Boolean(activeResumeId);

  const [mode, setMode] = useState<ResumeSource>('manual');
  const [missingFields, setMissingFields] = useState<string[]>([]);
  const [notice, setNotice] = useState('');
  const [generated, setGenerated] = useState(false);

  const [autoSaveStatus, setAutoSaveStatus] = useState<
    'idle' | 'saving' | 'saved' | 'error'
  >('idle');

  const lastSavedSnapshot = useRef('');

  const profilePreview = useProfileResumePreview(
    mode === 'profile' && !isEditing,
  );

  const savedResume = useResume(activeResumeId ?? '');
  const resumeList = useResumes();

  const createResume = useCreateResume();
  const updateResume = useUpdateResume();
  const generateResume = useGenerateResume();
  const exportResume = useExportResume();

  const form = useForm<GenerateResumeInput>({
    resolver: zodResolver(generateResumeSchema),
    mode: 'onSubmit',
    defaultValues: {
      title: '',
      source: 'manual',
      content: emptyDraft,
      preferences: {
        targetRole: '',
        tone: 'professional',
      },
    },
  });

  const education = useFieldArray({
    control: form.control,
    name: 'content.education',
  });

  const experience = useFieldArray({
    control: form.control,
    name: 'content.experience',
  });

  const projects = useFieldArray({
    control: form.control,
    name: 'content.projects',
  });

  const achievements = useFieldArray({
    control: form.control,
    name: 'content.achievements',
  });

  const content = form.watch('content');
  const title = form.watch('title');

  const preferences = form.watch('preferences') ?? {
    targetRole: '',
    tone: 'professional' as const,
  };

  const contact = content.contact;
  const skills = content.skills ?? [];

  const validationMessages = useMemo(
    () =>
      getFriendlyValidationMessages(
        form.formState.errors as Record<string, unknown>,
      ),
    [form.formState.errors],
  );

  // Load an existing resume.
  useEffect(() => {
    if (!isEditing || !savedResume.data) return;

    const record = savedResume.data.resume;

    const values: GenerateResumeInput = {
      title: record.title,
      source: record.source,
      content: record.content,
      preferences: {
        targetRole: '',
        tone: 'professional',
      },
    };

    form.reset(values);

    lastSavedSnapshot.current = JSON.stringify({
      title: values.title,
      content: values.content,
    });

    setMode(record.source);
    setGenerated(true);
    setAutoSaveStatus('saved');
  }, [isEditing, savedResume.data, form]);

  // Load profile data.
  useEffect(() => {
    if (
      isEditing ||
      mode !== 'profile' ||
      !profilePreview.data
    ) {
      return;
    }

    form.setValue('source', 'profile');

    form.setValue(
      'content',
      profilePreview.data.content,
      { shouldDirty: false },
    );

    setMissingFields(profilePreview.data.missingFields);
    setNotice('');
  }, [
    isEditing,
    mode,
    profilePreview.data,
    form,
  ]);

  // Auto-save existing resume.
  useEffect(() => {
    if (
      !isEditing ||
      !activeResumeId ||
      !savedResume.data ||
      !form.formState.isDirty
    ) {
      return;
    }

    const snapshot = JSON.stringify({
      title,
      content,
    });

    if (snapshot === lastSavedSnapshot.current) {
      return;
    }

    const timer = window.setTimeout(async () => {
      const valid = await form.trigger();

      if (!valid) {
        setAutoSaveStatus('error');
        return;
      }

      try {
        setAutoSaveStatus('saving');

        await updateResume.mutateAsync({
          resumeId: activeResumeId,
          payload: {
            title,
            content,
          },
        });

        lastSavedSnapshot.current = snapshot;
        setAutoSaveStatus('saved');
      } catch {
        setAutoSaveStatus('error');
      }
    }, 1800);

    return () => window.clearTimeout(timer);
  }, [
    isEditing,
    activeResumeId,
    savedResume.data,
    title,
    content,
    form,
    form.formState.isDirty,
    updateResume,
  ]);

  const addSkill = () => {
    form.setValue(
      'content.skills',
      [...skills, ''],
      { shouldDirty: true },
    );
  };

  const removeSkill = (index: number) => {
    form.setValue(
      'content.skills',
      skills.filter((_, i) => i !== index),
      { shouldDirty: true },
    );
  };

  const submit = form.handleSubmit(async (values) => {
    setNotice('');

    try {
      if (isEditing && activeResumeId) {
        await updateResume.mutateAsync({
          resumeId: activeResumeId,
          payload: {
            title: values.title,
            content: values.content,
          },
        });

        lastSavedSnapshot.current = JSON.stringify({
          title: values.title,
          content: values.content,
        });

        setAutoSaveStatus('saved');
        setNotice('Resume saved successfully.');
        return;
      }

      if (generated) {
        const result = await createResume.mutateAsync({
          title: values.title,
          source: values.source,
          content: values.content,
        });

        setNotice('Resume draft saved successfully.');

        router.push(
          `/launch/resume/${encodeURIComponent(result.resume.id)}`,
        );

        return;
      }

      const result = await generateResume.mutateAsync({
        ...values,
        preferences: {
          targetRole: values.preferences?.targetRole?.trim() || undefined,
          tone: values.preferences?.tone ?? 'professional',
        },
      });

      form.reset({
        title: result.resume.title,
        source: result.resume.source,
        content: result.resume.content,
        preferences: values.preferences,
      });

      setGenerated(true);
      setNotice('Resume generated successfully.');

      router.replace(
        `/launch/resume/${encodeURIComponent(result.resume.id)}`,
      );
    } catch (error) {
      setNotice(getFriendlyApiError(error));
    }
  });

  const handleDownloadPDF = async () => {
    if (!activeResumeId) return;

    try {
      const blob = await exportResume.mutateAsync(activeResumeId);

      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');

      link.href = url;
      link.download = `resume_${activeResumeId.slice(0, 8)}.pdf`;

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (error) {
      setNotice(getFriendlyApiError(error));
    }
  };

  if (isEditing && savedResume.isPending) {
    return <LaunchLoadingState message="Loading your resume..." />;
  }

  if (isEditing && savedResume.isError) {
    return (
      <LaunchErrorState
        title="Unable to load this resume"
        message="We couldn't load your resume. Please try again."
        action={
          <button
            onClick={() => void savedResume.refetch()}
            className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm text-white"
          >
            Try again
          </button>
        }
      />
    );
  }

  const isBusy =
    form.formState.isSubmitting ||
    createResume.isPending ||
    updateResume.isPending ||
    generateResume.isPending;

  const visibleEducation = content.education.filter((item) =>
    [
      item.institution,
      item.degree,
      item.fieldOfStudy,
      item.startDate,
      item.endDate,
      item.grade,
    ].some((value) => value?.trim()),
  );

  const visibleExperience = content.experience.filter((item) =>
    [
      item.company,
      item.role,
      item.location,
      item.startDate,
      item.endDate,
      item.description,
    ].some((value) => value?.trim()),
  );

  const visibleProjects = content.projects.filter((item) =>
    [
      item.name,
      item.description,
      item.projectUrl,
      item.startDate,
      item.endDate,
      ...(item.technologies ?? []),
    ].some((value) => value?.trim()),
  );

  const visibleAchievements = content.achievements.filter((item) =>
    [
      item.title,
      item.description,
      item.date,
    ].some((value) => value?.trim()),
  );

  const visibleSkills = skills.filter((skill) => skill.trim());

  const contactDetails = [
    contact.email,
    contact.phone,
    contact.location,
  ].filter((value) => value?.trim());

  const socialLinks = [
    contact.linkedInUrl,
    contact.githubUrl,
    contact.portfolioUrl,
  ].filter((value) => value?.trim());

  return (
    <main className="mx-auto max-w-[1500px] px-4 py-7 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-7">
        <Link
          href="/launch"
          className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)]"
        >
          ← Back to Launch
        </Link>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-[var(--text-primary)] sm:text-3xl">
              {isEditing ? 'Edit resume' : 'Resume Builder'}
            </h1>

            <p className="mt-1.5 text-sm text-[var(--text-secondary)]">
              Build a professional resume with accurate, editable information.
            </p>
          </div>

          {isEditing && (
            <div className="flex flex-wrap items-center gap-3">
              <span className="text-xs text-[var(--text-muted)]">
                {autoSaveStatus === 'saving'
                  ? 'Saving changes...'
                  : autoSaveStatus === 'saved'
                    ? 'Changes saved'
                    : autoSaveStatus === 'error'
                      ? 'Auto-save unavailable — check required fields or save manually'
                      : ''}
              </span>

              <button
                type="button"
                onClick={handleDownloadPDF}
                disabled={exportResume.isPending}
                className="rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-800 shadow-sm hover:bg-gray-50 disabled:opacity-50"
              >
                {exportResume.isPending
                  ? 'Preparing PDF...'
                  : '↓ Download PDF'}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Mode selector */}
      {!isEditing && (
        <div className="mb-6 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => {
              setMode('manual');
              setGenerated(false);
              setMissingFields([]);
              setNotice('');

              form.reset({
                title: '',
                source: 'manual',
                content: emptyDraft,
                preferences: {
                  targetRole: '',
                  tone: 'professional',
                },
              });
            }}
            className={`rounded-xl border px-4 py-3 text-sm font-medium ${
              mode === 'manual'
                ? 'border-[var(--primary)] bg-[var(--primary-soft)] text-[var(--primary)]'
                : 'border-[var(--border)] bg-[var(--surface)]'
            }`}
          >
            Enter details manually
          </button>

          <button
            type="button"
            onClick={() => {
              setMode('profile');
              setNotice('');
            }}
            className={`rounded-xl border px-4 py-3 text-sm font-medium ${
              mode === 'profile'
                ? 'border-[var(--primary)] bg-[var(--primary-soft)] text-[var(--primary)]'
                : 'border-[var(--border)] bg-[var(--surface)]'
            }`}
          >
            Generate from profile
          </button>
        </div>
      )}

      {mode === 'profile' && profilePreview.isPending && (
        <LaunchLoadingState message="Loading your existing profile..." />
      )}

      {mode === 'profile' && profilePreview.isError && (
        <div className="mb-6">
          <LaunchErrorState
            title="Profile preview unavailable"
            message="We couldn't load your profile details. Please try again."
            action={
              <button
                type="button"
                onClick={() => void profilePreview.refetch()}
                className="rounded-lg bg-[var(--primary)] px-4 py-2 text-sm text-white"
              >
                Retry profile loading
              </button>
            }
          />
        </div>
      )}

      {mode === 'profile' &&
        profilePreview.data &&
        missingFields.length > 0 && (
          <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50 p-4">
            <h3 className="font-semibold text-amber-900">
              Complete your resume
            </h3>

            <p className="mt-1 text-sm text-amber-800">
              Your profile is missing: {missingFields.join(', ')}.
              You can fill these fields below.
            </p>
          </div>
        )}

      <form
        onSubmit={submit}
        className="grid items-start gap-7 xl:grid-cols-[minmax(0,1fr)_minmax(380px,0.9fr)]"
      >
        {/* LEFT: EDITOR */}
        <div className="min-w-0 space-y-5">
          {/* Basic details */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
            <h2 className="mb-5 text-lg font-semibold text-[var(--text-primary)]">
              Personal information
            </h2>

            <label className={labelClass}>
              Resume title *
              <input
                {...form.register('title')}
                placeholder="e.g. Software Engineer Resume"
                className={inputClass}
              />
              <ErrorText message={form.formState.errors.title?.message} />
            </label>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              {([
                ['fullName', 'Full name *', 'text'],
                ['email', 'Email address *', 'email'],
                ['phone', 'Phone number', 'text'],
                ['location', 'Location', 'text'],
                ['linkedInUrl', 'LinkedIn URL', 'url'],
                ['githubUrl', 'GitHub URL', 'url'],
                ['portfolioUrl', 'Portfolio URL', 'url'],
              ] as const).map(([name, label, type]) => (
                <label key={name} className={labelClass}>
                  {label}

                  <input
                    type={type}
                    {...form.register(`content.contact.${name}`)}
                    className={inputClass}
                    placeholder={
                      name === 'email'
                        ? 'name@example.com'
                        : name === 'phone'
                          ? '+91 ...'
                          : name === 'linkedInUrl'
                            ? 'https://linkedin.com/in/...'
                            : name === 'githubUrl'
                              ? 'https://github.com/...'
                              : name === 'portfolioUrl'
                                ? 'https://...'
                                : ''
                    }
                  />

                  <ErrorText
                    message={
                      form.formState.errors.content?.contact?.[name]?.message
                    }
                  />
                </label>
              ))}
            </div>

            <label className={`${labelClass} mt-4`}>
              Professional headline
              <input
                {...form.register('content.headline')}
                placeholder="e.g. Computer Science Student | Full Stack Developer"
                className={inputClass}
              />
            </label>

            <label className={`${labelClass} mt-4`}>
              Professional summary
              <textarea
                {...form.register('content.summary')}
                rows={4}
                className={inputClass}
                placeholder="Write a concise summary of your skills, experience and professional interests."
              />
            </label>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <label className={labelClass}>
                Target role (optional)
                <input
                  value={preferences.targetRole ?? ''}
                  onChange={(e) =>
                    form.setValue('preferences.targetRole', e.target.value, {
                      shouldDirty: true,
                    })
                  }
                  className={inputClass}
                  placeholder="e.g. Software Engineer"
                />
              </label>

              <label className={labelClass}>
                Writing tone
                <select
                  value={preferences.tone ?? 'professional'}
                  onChange={(e) =>
                    form.setValue(
                      'preferences.tone',
                      e.target.value as 'professional' | 'concise',
                      { shouldDirty: true },
                    )
                  }
                  className={inputClass}
                >
                  <option value="professional">Professional</option>
                  <option value="concise">Concise</option>
                </select>
              </label>
            </div>
          </section>

          {/* Skills */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
            <SectionHeading title="Skills" onAdd={addSkill} />

            {skills.map((_, index) => (
              <div key={index} className="mb-3 flex gap-2">
                <input
                  {...form.register(`content.skills.${index}`)}
                  className={inputClass}
                  placeholder="e.g. React, Python, SQL"
                />

                <button
                  type="button"
                  onClick={() => removeSkill(index)}
                  aria-label="Remove skill"
                  className="rounded-lg border border-[var(--border)] px-3 text-red-600 hover:bg-red-50"
                >
                  ×
                </button>
              </div>
            ))}
          </section>

          {/* Education */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
            <SectionHeading
              title="Education"
              onAdd={() =>
                education.append({
                  id: crypto.randomUUID(),
                  institution: '',
                  degree: '',
                  fieldOfStudy: '',
                  startDate: '',
                  endDate: '',
                  grade: '',
                })
              }
            />

            {education.fields.map((item, index) => (
              <div
                key={item.id}
                className="mb-5 rounded-xl border border-[var(--border)] p-4 last:mb-0"
              >
                <div className="mb-3 flex justify-between">
                  <p className="text-sm font-semibold text-[var(--text-primary)]">
                    Education {index + 1}
                  </p>

                  <button
                    type="button"
                    onClick={() => education.remove(index)}
                    className="text-sm text-red-600"
                  >
                    Remove
                  </button>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  {([
                    ['institution', 'Institution'],
                    ['degree', 'Degree'],
                    ['fieldOfStudy', 'Field of study'],
                    ['startDate', 'Start date'],
                    ['endDate', 'End date'],
                    ['grade', 'Grade / CGPA'],
                  ] as const).map(([key, label]) => (
                    <label key={key} className={labelClass}>
                      {label}
                      <input
                        type={
                          key === 'startDate' || key === 'endDate'
                            ? 'date'
                            : 'text'
                        }
                        {...form.register(`content.education.${index}.${key}`)}
                        className={inputClass}
                      />
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </section>

          {/* Experience */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
            <SectionHeading
              title="Experience"
              onAdd={() =>
                experience.append({
                  id: crypto.randomUUID(),
                  company: '',
                  role: '',
                  location: '',
                  startDate: '',
                  endDate: '',
                  isCurrent: false,
                  description: '',
                })
              }
            />

            {experience.fields.map((item, index) => (
              <div
                key={item.id}
                className="mb-5 rounded-xl border border-[var(--border)] p-4 last:mb-0"
              >
                <div className="mb-3 flex justify-between">
                  <p className="text-sm font-semibold text-[var(--text-primary)]">
                    Experience {index + 1}
                  </p>

                  <button
                    type="button"
                    onClick={() => experience.remove(index)}
                    className="text-sm text-red-600"
                  >
                    Remove
                  </button>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  {([
                    ['company', 'Company'],
                    ['role', 'Job title'],
                    ['location', 'Location'],
                    ['startDate', 'Start date'],
                    ['endDate', 'End date'],
                  ] as const).map(([key, label]) => (
                    <label key={key} className={labelClass}>
                      {label}
                      <input
                        type={
                          key === 'startDate' || key === 'endDate'
                            ? 'date'
                            : 'text'
                        }
                        {...form.register(`content.experience.${index}.${key}`)}
                        className={inputClass}
                      />
                    </label>
                  ))}
                </div>

                <label className="mt-3 flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                  <input
                    type="checkbox"
                    {...form.register(`content.experience.${index}.isCurrent`)}
                  />
                  Currently working here
                </label>

                <label className={`${labelClass} mt-3`}>
                  Description
                  <textarea
                    {...form.register(`content.experience.${index}.description`)}
                    rows={3}
                    className={inputClass}
                    placeholder="Describe your responsibilities and achievements."
                  />
                </label>
              </div>
            ))}
          </section>

          {/* Projects */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
            <SectionHeading
              title="Projects"
              onAdd={() =>
                projects.append({
                  id: crypto.randomUUID(),
                  name: '',
                  description: '',
                  technologies: [],
                  projectUrl: '',
                  startDate: '',
                  endDate: '',
                })
              }
            />

            {projects.fields.map((item, index) => (
              <div
                key={item.id}
                className="mb-5 rounded-xl border border-[var(--border)] p-4 last:mb-0"
              >
                <div className="mb-3 flex justify-between">
                  <p className="text-sm font-semibold text-[var(--text-primary)]">
                    Project {index + 1}
                  </p>

                  <button
                    type="button"
                    onClick={() => projects.remove(index)}
                    className="text-sm text-red-600"
                  >
                    Remove
                  </button>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <label className={labelClass}>
                    Project name *
                    <input
                      {...form.register(`content.projects.${index}.name`)}
                      className={inputClass}
                    />
                    <ErrorText
                      message={
                        form.formState.errors.content?.projects?.[index]?.name?.message
                      }
                    />
                  </label>

                  <label className={labelClass}>
                    Project URL
                    <input
                      {...form.register(`content.projects.${index}.projectUrl`)}
                      className={inputClass}
                      placeholder="https://..."
                    />
                  </label>

                  <label className={labelClass}>
                    Technologies (comma-separated)
                    <input
                      value={(
                        form.watch(`content.projects.${index}.technologies`) ?? []
                      ).join(', ')}
                      onChange={(e) =>
                        form.setValue(
                          `content.projects.${index}.technologies`,
                          e.target.value
                            .split(',')
                            .map((value) => value.trim())
                            .filter(Boolean),
                          { shouldDirty: true },
                        )
                      }
                      className={inputClass}
                      placeholder="React, FastAPI, PostgreSQL"
                    />
                  </label>

                  <label className={labelClass}>
                    Start date
                    <input
                      type="date"
                      {...form.register(`content.projects.${index}.startDate`)}
                      className={inputClass}
                    />
                  </label>

                  <label className={labelClass}>
                    End date
                    <input
                      type="date"
                      {...form.register(`content.projects.${index}.endDate`)}
                      className={inputClass}
                    />
                  </label>
                </div>

                <label className={`${labelClass} mt-3`}>
                  Description
                  <textarea
                    {...form.register(`content.projects.${index}.description`)}
                    rows={3}
                    className={inputClass}
                    placeholder="Explain what you built and the problem it solves."
                  />
                </label>
              </div>
            ))}
          </section>

          {/* Achievements */}
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
            <SectionHeading
              title="Achievements"
              onAdd={() =>
                achievements.append({
                  id: crypto.randomUUID(),
                  title: '',
                  description: '',
                  date: '',
                })
              }
            />

            {achievements.fields.map((item, index) => (
              <div
                key={item.id}
                className="mb-5 rounded-xl border border-[var(--border)] p-4 last:mb-0"
              >
                <div className="mb-3 flex justify-between">
                  <p className="text-sm font-semibold text-[var(--text-primary)]">
                    Achievement {index + 1}
                  </p>

                  <button
                    type="button"
                    onClick={() => achievements.remove(index)}
                    className="text-sm text-red-600"
                  >
                    Remove
                  </button>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <label className={labelClass}>
                    Title *
                    <input
                      {...form.register(`content.achievements.${index}.title`)}
                      className={inputClass}
                    />
                    <ErrorText
                      message={
                        form.formState.errors.content?.achievements?.[index]?.title?.message
                      }
                    />
                  </label>

                  <label className={labelClass}>
                    Date
                    <input
                      type="date"
                      {...form.register(`content.achievements.${index}.date`)}
                      className={inputClass}
                    />
                  </label>
                </div>

                <label className={`${labelClass} mt-3`}>
                  Description
                  <textarea
                    {...form.register(`content.achievements.${index}.description`)}
                    rows={2}
                    className={inputClass}
                  />
                </label>
              </div>
            ))}
          </section>

          {/* Friendly validation summary */}
          {validationMessages.length > 0 && (
            <div
              role="alert"
              className="rounded-xl border border-red-200 bg-red-50 p-4"
            >
              <p className="mb-2 text-sm font-semibold text-red-800">
                Please review the following details:
              </p>

              <ul className="list-inside list-disc space-y-1 text-sm text-red-700">
                {validationMessages.map((message, index) => (
                  <li key={`${message}-${index}`}>
                    {message}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {notice && (
            <div
              role="status"
              className="rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-4 text-sm text-[var(--text-primary)]"
            >
              {notice}
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            <button
              type="submit"
              disabled={
                isBusy ||
                (mode === 'profile' && profilePreview.isPending)
              }
              className="rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-medium text-white hover:bg-[var(--primary-hover)] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isBusy
                ? 'Please wait...'
                : isEditing
                  ? 'Save changes'
                  : generated
                    ? 'Save resume draft'
                    : 'Generate resume'}
            </button>

            {!isEditing && generated && (
              <button
                type="button"
                onClick={() => {
                  setGenerated(false);
                  setNotice(
                    'Review your information and generate again if needed.',
                  );
                }}
                className="rounded-xl border border-[var(--border)] px-5 py-3 text-sm text-[var(--text-primary)]"
              >
                Back to generation
              </button>
            )}
          </div>
        </div>

        {/* RIGHT: PROFESSIONAL WHITE RESUME PREVIEW */}
        <aside className="min-w-0 xl:sticky xl:top-5">
          <div className="mb-3 flex items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-semibold text-[var(--text-primary)]">
                Live resume preview
              </h2>

              <p className="mt-0.5 text-xs text-[var(--text-secondary)]">
                Standard professional layout
              </p>
            </div>

            <span className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-3 py-1 text-xs text-[var(--text-secondary)]">
              A4 style
            </span>
          </div>

          <div className="max-h-[calc(100vh-130px)] overflow-y-auto rounded-xl border border-gray-200 bg-gray-100 p-3 sm:p-5">
            <article className="mx-auto min-h-[842px] w-full max-w-[595px] bg-white px-7 py-9 text-gray-800 shadow-md sm:px-10 sm:py-11">
              <header className="border-b-2 border-gray-800 pb-4 text-center">
                {contact.fullName?.trim() && (
                  <h1 className="text-2xl font-bold tracking-wide text-gray-950">
                    {contact.fullName}
                  </h1>
                )}

                {content.headline?.trim() && (
                  <p className="mt-1 text-sm font-medium text-gray-600">
                    {content.headline}
                  </p>
                )}

                {contactDetails.length > 0 && (
                  <p className="mt-3 flex flex-wrap justify-center gap-x-2 gap-y-1 text-[10px] text-gray-600">
                    {contactDetails.map((value, index) => (
                      <span key={`${value}-${index}`}>
                        {index > 0 && (
                          <span className="mr-2 text-gray-400">|</span>
                        )}
                        {value}
                      </span>
                    ))}
                  </p>
                )}

                {socialLinks.length > 0 && (
                  <div className="mt-1.5 flex flex-wrap justify-center gap-x-3 gap-y-1 text-[10px] text-gray-600">
                    {contact.linkedInUrl?.trim() && (
                      <span>{contact.linkedInUrl}</span>
                    )}
                    {contact.githubUrl?.trim() && (
                      <span>{contact.githubUrl}</span>
                    )}
                    {contact.portfolioUrl?.trim() && (
                      <span>{contact.portfolioUrl}</span>
                    )}
                  </div>
                )}
              </header>

              {content.summary?.trim() && (
                <PreviewSection title="Professional Summary">
                  <p className="whitespace-pre-wrap text-[11px] leading-[1.65] text-gray-700">
                    {content.summary}
                  </p>
                </PreviewSection>
              )}

              {visibleSkills.length > 0 && (
                <PreviewSection title="Technical Skills">
                  <p className="text-[11px] leading-[1.8] text-gray-700">
                    {visibleSkills.join('  •  ')}
                  </p>
                </PreviewSection>
              )}

              {visibleExperience.length > 0 && (
                <PreviewSection title="Experience">
                  <div className="space-y-3">
                    {visibleExperience.map((item) => (
                      <div key={item.id}>
                        {(item.role || item.company) && (
                          <div className="flex flex-wrap items-baseline justify-between gap-x-2">
                            <p className="text-[12px] font-bold text-gray-900">
                              {[item.role, item.company]
                                .filter(Boolean)
                                .join(' — ')}
                            </p>

                            {(item.startDate || item.endDate || item.isCurrent) && (
                              <p className="text-[10px] text-gray-500">
                                {[
                                  item.startDate,
                                  item.isCurrent ? 'Present' : item.endDate,
                                ]
                                  .filter(Boolean)
                                  .join(' – ')}
                              </p>
                            )}
                          </div>
                        )}

                        {item.location?.trim() && (
                          <p className="mt-0.5 text-[10px] italic text-gray-500">
                            {item.location}
                          </p>
                        )}

                        {item.description?.trim() && (
                          <p className="mt-1 whitespace-pre-wrap text-[11px] leading-[1.6] text-gray-700">
                            {item.description}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </PreviewSection>
              )}

              {visibleProjects.length > 0 && (
                <PreviewSection title="Projects">
                  <div className="space-y-3">
                    {visibleProjects.map((item) => (
                      <div key={item.id}>
                        <div className="flex flex-wrap items-baseline justify-between gap-x-2">
                          {item.name?.trim() && (
                            <p className="text-[12px] font-bold text-gray-900">
                              {item.name}
                            </p>
                          )}

                          {(item.startDate || item.endDate) && (
                            <p className="text-[10px] text-gray-500">
                              {[item.startDate, item.endDate]
                                .filter(Boolean)
                                .join(' – ')}
                            </p>
                          )}
                        </div>

                        {item.description?.trim() && (
                          <p className="mt-1 whitespace-pre-wrap text-[11px] leading-[1.6] text-gray-700">
                            {item.description}
                          </p>
                        )}

                        {item.technologies?.some((value) => value.trim()) && (
                          <p className="mt-1 text-[10px] text-gray-600">
                            <strong>Technologies:</strong>{' '}
                            {item.technologies
                              .filter((value) => value.trim())
                              .join(', ')}
                          </p>
                        )}

                        {item.projectUrl?.trim() && (
                          <p className="mt-1 break-all text-[10px] text-gray-600">
                            {item.projectUrl}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </PreviewSection>
              )}

              {visibleEducation.length > 0 && (
                <PreviewSection title="Education">
                  <div className="space-y-3">
                    {visibleEducation.map((item) => (
                      <div key={item.id}>
                        <div className="flex flex-wrap items-baseline justify-between gap-x-2">
                          {item.institution?.trim() && (
                            <p className="text-[12px] font-bold text-gray-900">
                              {item.institution}
                            </p>
                          )}

                          {(item.startDate || item.endDate) && (
                            <p className="text-[10px] text-gray-500">
                              {[item.startDate, item.endDate]
                                .filter(Boolean)
                                .join(' – ')}
                            </p>
                          )}
                        </div>

                        {[item.degree, item.fieldOfStudy]
                          .filter((value) => value?.trim())
                          .length > 0 && (
                          <p className="mt-0.5 text-[11px] text-gray-700">
                            {[item.degree, item.fieldOfStudy]
                              .filter((value) => value?.trim())
                              .join(', ')}
                          </p>
                        )}

                        {item.grade?.trim() && (
                          <p className="mt-0.5 text-[10px] text-gray-600">
                            Grade: {item.grade}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </PreviewSection>
              )}

              {visibleAchievements.length > 0 && (
                <PreviewSection title="Achievements">
                  <div className="space-y-2">
                    {visibleAchievements.map((item) => (
                      <div key={item.id}>
                        <div className="flex flex-wrap items-baseline justify-between gap-x-2">
                          {item.title?.trim() && (
                            <p className="text-[11px] font-semibold text-gray-900">
                              {item.title}
                            </p>
                          )}

                          {item.date?.trim() && (
                            <p className="text-[10px] text-gray-500">
                              {item.date}
                            </p>
                          )}
                        </div>

                        {item.description?.trim() && (
                          <p className="mt-0.5 text-[11px] leading-[1.5] text-gray-700">
                            {item.description}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </PreviewSection>
              )}

              {!contact.fullName?.trim() &&
                !content.headline?.trim() &&
                !content.summary?.trim() &&
                visibleSkills.length === 0 &&
                visibleExperience.length === 0 &&
                visibleProjects.length === 0 &&
                visibleEducation.length === 0 &&
                visibleAchievements.length === 0 && (
                  <div className="flex min-h-[450px] items-center justify-center text-center">
                    <div>
                      <p className="text-sm font-medium text-gray-500">
                        Your resume preview will appear here.
                      </p>
                      <p className="mt-1 text-xs text-gray-400">
                        Start entering your information to build your resume.
                      </p>
                    </div>
                  </div>
                )}
            </article>
          </div>
        </aside>
      </form>

      {/* Saved resumes */}
      {!isEditing && (
        <section className="mt-12">
          <h2 className="mb-4 text-xl font-semibold text-[var(--text-primary)]">
            Saved resumes
          </h2>

          {resumeList.isPending ? (
            <LaunchLoadingState message="Loading saved resumes..." />
          ) : resumeList.isError ? (
            <LaunchErrorState message="Unable to load saved resumes. Please try again." />
          ) : resumeList.data.items.length === 0 ? (
            <ResumeState kind="empty" />
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {resumeList.data.items.map((item) => (
                <Link
                  key={item.id}
                  href={`/launch/resume/${encodeURIComponent(item.id)}`}
                  className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4 hover:border-[var(--primary)]"
                >
                  <p className="font-medium text-[var(--text-primary)]">
                    {item.title}
                  </p>

                  <p className="mt-1 text-xs text-[var(--text-secondary)]">
                    {item.status} · {item.source}
                  </p>
                </Link>
              ))}
            </div>
          )}
        </section>
      )}
    </main>
  );
}
