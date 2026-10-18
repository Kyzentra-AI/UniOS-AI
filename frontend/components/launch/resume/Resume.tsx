
'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  useFieldArray,
  useForm,
} from 'react-hook-form';
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
  'w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-3 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary-soft)]';

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
      <h3 className="text-lg font-semibold text-[var(--text-primary)]">
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
  const [preferences, setPreferences] = useState({
    targetRole: '',
    tone: 'professional' as 'professional' | 'concise',
  });
  const [missingFields, setMissingFields] = useState<string[]>([]);
  const [notice, setNotice] = useState('');
  const [generated, setGenerated] = useState(false);

  const profilePreview = useProfileResumePreview(mode === 'profile' && !isEditing);
  const savedResume = useResume(activeResumeId ?? '');
  const resumeList = useResumes();
  const createResume = useCreateResume();
  const updateResume = useUpdateResume();
  const generateResume = useGenerateResume();

  const form = useForm<GenerateResumeInput>({
    resolver: zodResolver(generateResumeSchema),
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

  useEffect(() => {
    if (!isEditing || !savedResume.data) return;

    const record = savedResume.data.resume;

    form.reset({
      title: record.title,
      source: record.source,
      content: record.content,
      preferences: {
        targetRole: '',
        tone: 'professional',
      },
    });

    setMode(record.source);
  }, [isEditing, savedResume.data, form]);

  useEffect(() => {
  if (isEditing || mode !== 'profile' || !profilePreview.data) {
    return;
  }

  form.setValue('source', 'profile');
  form.setValue('content', profilePreview.data.content);
  setMissingFields(profilePreview.data.missingFields);
  setNotice('');
}, [isEditing, mode, profilePreview.data, form]);

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
          targetRole: preferences.targetRole || undefined,
          tone: preferences.tone,
        },
      });

      form.reset({
        title: result.resume.title,
        source: result.resume.source,
        content: result.resume.content,
        preferences: values.preferences,
      });

      setGenerated(true);
      setNotice('Generated resume loaded. Review it before saving.');
      router.replace(
        `/launch/resume/${encodeURIComponent(result.resume.id)}`,
      );
    } catch (error) {
      setNotice(
        error instanceof Error
          ? error.message
          : 'The operation failed. Your existing draft has not been intentionally cleared.',
      );
    }
  });

  if (isEditing && savedResume.isPending) {
    return <LaunchLoadingState message="Loading your resume..." />;
  }

  if (isEditing && savedResume.isError) {
    return (
      <LaunchErrorState
        title="Unable to load this resume"
        message={savedResume.error.message}
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

  const contact = form.watch('content.contact');
  const skills = form.watch('content.skills');

  const addSkill = () => {
    form.setValue('content.skills', [...skills, ''], {
      shouldDirty: true,
    });
  };

  const removeSkill = (index: number) => {
    form.setValue(
      'content.skills',
      skills.filter((_, i) => i !== index),
      { shouldDirty: true },
    );
  };

  const field = (
    name: keyof ResumeDraft['contact'],
    label: string,
    type = 'text',
  ) => (
    <label className={labelClass}>
      {label}
      <input
        type={type}
        {...form.register(`content.contact.${name}`)}
        className={inputClass}
      />
      {form.formState.errors.content?.contact?.[name]?.message && (
        <span className="mt-1 block text-xs text-[var(--danger-text)]">
          {form.formState.errors.content.contact[name]?.message}
        </span>
      )}
    </label>
  );

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <Link
        href="/launch"
        className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)]"
      >
        ← Back to Launch
      </Link>

      <div className="mb-8 mt-5">
        <h1 className="text-3xl font-semibold text-[var(--text-primary)]">
          {isEditing ? 'Edit resume' : 'Resume Builder'}
        </h1>
        <p className="mt-2 text-sm text-[var(--text-secondary)]">
          Keep your information accurate. Generated content remains editable.
        </p>
      </div>

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
            message={profilePreview.error.message}
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
          <div className="mb-6 rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-4">
            <h3 className="font-semibold text-[var(--text-primary)]">
              Complete your resume
            </h3>
            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Your profile is missing: {missingFields.join(', ')}.
              You can fill these fields in the form below.
            </p>
          </div>
        )}

      <form onSubmit={submit} className="grid gap-6 lg:grid-cols-[1.35fr_0.85fr]">
        <div className="space-y-6">
          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-7">
            <h2 className="mb-5 text-lg font-semibold text-[var(--text-primary)]">
              Resume details
            </h2>

            <label className={labelClass}>
              Resume title *
              <input
                {...form.register('title')}
                placeholder="e.g. Software Engineer Resume"
                className={inputClass}
              />
              {form.formState.errors.title?.message && (
                <span className="mt-1 block text-xs text-[var(--danger-text)]">
                  {form.formState.errors.title.message}
                </span>
              )}
            </label>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              {field('fullName', 'Full name *')}
              {field('email', 'Email *', 'email')}
              {field('phone', 'Phone')}
              {field('location', 'Location')}
              {field('linkedInUrl', 'LinkedIn URL', 'url')}
              {field('githubUrl', 'GitHub URL', 'url')}
              {field('portfolioUrl', 'Portfolio URL', 'url')}
            </div>

            <label className={`${labelClass} mt-4`}>
              Headline
              <input
                {...form.register('content.headline')}
                placeholder="Your professional headline"
                className={inputClass}
              />
            </label>

            <label className={`${labelClass} mt-4`}>
              Professional summary
              <textarea
                {...form.register('content.summary')}
                rows={4}
                className={inputClass}
                placeholder="Describe your experience and strengths accurately."
              />
            </label>

            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <label className={labelClass}>
                Target role (optional)
                <input
                  value={preferences.targetRole}
                  onChange={(e) =>
                    setPreferences((prev) => ({
                      ...prev,
                      targetRole: e.target.value,
                    }))
                  }
                  className={inputClass}
                  placeholder="e.g. Frontend Developer"
                />
              </label>

              <label className={labelClass}>
                Writing tone
                <select
                  value={preferences.tone}
                  onChange={(e) =>
                    setPreferences((prev) => ({
                      ...prev,
                      tone: e.target.value as 'professional' | 'concise',
                    }))
                  }
                  className={inputClass}
                >
                  <option value="professional">Professional</option>
                  <option value="concise">Concise</option>
                </select>
              </label>
            </div>
          </section>

          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-7">
            <SectionHeading
              title="Skills"
              onAdd={addSkill}
            />
            {skills.map((_, index) => (
              <div key={index} className="mb-3 flex gap-2">
                <input
                  {...form.register(`content.skills.${index}`)}
                  className={inputClass}
                  placeholder="Skill name"
                />
                <button
                  type="button"
                  onClick={() => removeSkill(index)}
                  aria-label="Remove skill"
                  className="rounded-lg border border-[var(--border)] px-3 text-[var(--danger-text)]"
                >
                  ×
                </button>
              </div>
            ))}
          </section>

          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-7">
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
              <div key={item.id} className="mb-5 rounded-xl border border-[var(--border)] p-4">
                <div className="mb-3 flex justify-between">
                  <p className="font-medium text-[var(--text-primary)]">
                    Education {index + 1}
                  </p>
                  <button type="button" onClick={() => education.remove(index)} className="text-sm text-[var(--danger-text)]">
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
                    ['grade', 'Grade'],
                  ] as const).map(([key, label]) => (
                    <label key={key} className={labelClass}>
                      {label}
                      <input
                        {...form.register(`content.education.${index}.${key}`)}
                        className={inputClass}
                      />
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </section>

          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-7">
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
              <div key={item.id} className="mb-5 rounded-xl border border-[var(--border)] p-4">
                <div className="mb-3 flex justify-between">
                  <p className="font-medium text-[var(--text-primary)]">
                    Experience {index + 1}
                  </p>
                  <button type="button" onClick={() => experience.remove(index)} className="text-sm text-[var(--danger-text)]">
                    Remove
                  </button>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  {([
                    ['company', 'Company'],
                    ['role', 'Role'],
                    ['location', 'Location'],
                    ['startDate', 'Start date'],
                    ['endDate', 'End date'],
                  ] as const).map(([key, label]) => (
                    <label key={key} className={labelClass}>
                      {label}
                      <input
                        {...form.register(`content.experience.${index}.${key}`)}
                        className={inputClass}
                      />
                    </label>
                  ))}
                </div>
                <label className="mt-3 flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                  <input type="checkbox" {...form.register(`content.experience.${index}.isCurrent`)} />
                  Current role
                </label>
                <label className={`${labelClass} mt-3`}>
                  Description
                  <textarea
                    {...form.register(`content.experience.${index}.description`)}
                    rows={3}
                    className={inputClass}
                  />
                </label>
              </div>
            ))}
          </section>

          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-7">
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
              <div key={item.id} className="mb-5 rounded-xl border border-[var(--border)] p-4">
                <div className="mb-3 flex justify-between">
                  <p className="font-medium text-[var(--text-primary)]">
                    Project {index + 1}
                  </p>
                  <button type="button" onClick={() => projects.remove(index)} className="text-sm text-[var(--danger-text)]">
                    Remove
                  </button>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <label className={labelClass}>
                    Project name *
                    <input {...form.register(`content.projects.${index}.name`)} className={inputClass} />
                  </label>
                  <label className={labelClass}>
                    Project URL
                    <input {...form.register(`content.projects.${index}.projectUrl`)} className={inputClass} />
                  </label>
                  <label className={labelClass}>
                    Technologies (comma-separated)
                    <input
                      value={form.watch(`content.projects.${index}.technologies`).join(', ')}
                      onChange={(e) =>
                        form.setValue(
                          `content.projects.${index}.technologies`,
                          e.target.value.split(',').map((v) => v.trim()).filter(Boolean),
                          { shouldDirty: true },
                        )
                      }
                      className={inputClass}
                    />
                  </label>
                  <label className={labelClass}>
                    Start date
                    <input {...form.register(`content.projects.${index}.startDate`)} className={inputClass} />
                  </label>
                  <label className={labelClass}>
                    End date
                    <input {...form.register(`content.projects.${index}.endDate`)} className={inputClass} />
                  </label>
                </div>
                <label className={`${labelClass} mt-3`}>
                  Description
                  <textarea {...form.register(`content.projects.${index}.description`)} rows={3} className={inputClass} />
                </label>
              </div>
            ))}
          </section>

          <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-7">
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
              <div key={item.id} className="mb-4 rounded-xl border border-[var(--border)] p-4">
                <div className="mb-3 flex justify-between">
                  <p className="font-medium text-[var(--text-primary)]">
                    Achievement {index + 1}
                  </p>
                  <button type="button" onClick={() => achievements.remove(index)} className="text-sm text-[var(--danger-text)]">
                    Remove
                  </button>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <label className={labelClass}>
                    Title *
                    <input {...form.register(`content.achievements.${index}.title`)} className={inputClass} />
                  </label>
                  <label className={labelClass}>
                    Date
                    <input {...form.register(`content.achievements.${index}.date`)} className={inputClass} />
                  </label>
                </div>
                <label className={`${labelClass} mt-3`}>
                  Description
                  <textarea {...form.register(`content.achievements.${index}.description`)} rows={2} className={inputClass} />
                </label>
              </div>
            ))}
          </section>

          {notice && (
            <div role="status" className="rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-4 text-sm text-[var(--text-primary)]">
              {notice}
            </div>
          )}

          {form.formState.errors.content && (
            <p className="text-sm text-[var(--danger-text)]">
              Please review the form. Some fields need attention.
            </p>
          )}

          <div className="flex flex-wrap gap-3">
            <button
              type="submit"
              disabled={isBusy || (mode === 'profile' && profilePreview.isPending)}
              className="rounded-xl bg-[var(--primary)] px-5 py-3 text-sm font-medium text-white hover:bg-[var(--primary-hover)] disabled:cursor-not-allowed disabled:opacity-60"
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
                  setNotice('You can review the current draft and generate again if needed.');
                }}
                className="rounded-xl border border-[var(--border)] px-5 py-3 text-sm text-[var(--text-primary)]"
              >
                Back to generation
              </button>
            )}
          </div>
        </div>

        <aside className="h-fit rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 lg:sticky lg:top-6">
          <h2 className="mb-5 text-lg font-semibold text-[var(--text-primary)]">
            Resume preview
          </h2>
          <div className="min-h-64 space-y-4 break-words text-sm text-[var(--text-secondary)]">
            <div className="border-b border-[var(--border)] pb-4">
              <h3 className="text-xl font-semibold text-[var(--text-primary)]">
                {contact.fullName || 'Your name'}
              </h3>
              <p className="mt-1">{form.watch('content.headline') || 'Professional headline'}</p>
              <p className="mt-2 text-xs">
                {[contact.email, contact.phone, contact.location].filter(Boolean).join(' · ') || 'Contact information'}
              </p>
            </div>

            <div>
              <h4 className="font-semibold text-[var(--text-primary)]">Summary</h4>
              <p className="mt-1 whitespace-pre-wrap">{form.watch('content.summary') || 'Your summary will appear here.'}</p>
            </div>

            <div>
              <h4 className="font-semibold text-[var(--text-primary)]">Skills</h4>
              <p className="mt-1">{skills.filter(Boolean).join(' · ') || 'Add your skills'}</p>
            </div>

            {form.watch('content.education').length > 0 && (
              <div>
                <h4 className="font-semibold text-[var(--text-primary)]">Education</h4>
                {form.watch('content.education').map((item) => (
                  <div key={item.id} className="mt-2">
                    <p className="font-medium text-[var(--text-primary)]">{item.institution || 'Institution'}</p>
                    <p>{[item.degree, item.fieldOfStudy].filter(Boolean).join(', ')}</p>
                    <p className="text-xs">{[item.startDate, item.endDate, item.grade].filter(Boolean).join(' · ')}</p>
                  </div>
                ))}
              </div>
            )}

            {form.watch('content.experience').length > 0 && (
              <div>
                <h4 className="font-semibold text-[var(--text-primary)]">Experience</h4>
                {form.watch('content.experience').map((item) => (
                  <div key={item.id} className="mt-2">
                    <p className="font-medium text-[var(--text-primary)]">{item.role || 'Role'} {item.company ? `· ${item.company}` : ''}</p>
                    <p className="whitespace-pre-wrap">{item.description}</p>
                  </div>
                ))}
              </div>
            )}

            {form.watch('content.projects').length > 0 && (
              <div>
                <h4 className="font-semibold text-[var(--text-primary)]">Projects</h4>
                {form.watch('content.projects').map((item) => (
                  <div key={item.id} className="mt-2">
                    <p className="font-medium text-[var(--text-primary)]">{item.name || 'Project'}</p>
                    <p className="whitespace-pre-wrap">{item.description}</p>
                    <p className="text-xs">{item.technologies.join(', ')}</p>
                  </div>
                ))}
              </div>
            )}

            {form.watch('content.achievements').length > 0 && (
              <div>
                <h4 className="font-semibold text-[var(--text-primary)]">Achievements</h4>
                {form.watch('content.achievements').map((item) => (
                  <div key={item.id} className="mt-2">
                    <p className="font-medium text-[var(--text-primary)]">{item.title}</p>
                    <p>{item.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </aside>
      </form>

      {!isEditing && (
        <section className="mt-12">
          <h2 className="mb-4 text-xl font-semibold text-[var(--text-primary)]">
            Saved resumes
          </h2>
          {resumeList.isPending ? (
            <LaunchLoadingState message="Loading saved resumes..." />
          ) : resumeList.isError ? (
            <LaunchErrorState message={resumeList.error.message} />
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
                  <p className="font-medium text-[var(--text-primary)]">{item.title}</p>
                  <p className="mt-1 text-xs text-[var(--text-secondary)]">{item.status} · {item.source}</p>
                </Link>
              ))}
            </div>
          )}
        </section>
      )}
    </main>
  );
}
