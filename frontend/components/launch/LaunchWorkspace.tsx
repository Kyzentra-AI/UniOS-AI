
'use client';

import { useRef, useState } from 'react';
import type {
  LaunchTab,
  ResumeDraft,
  ResumeEducation,
  ResumeProject,
  ResumeAchievement,
} from '@/types/launch';
import { resumeSchema, atsFileSchema } from '@/app/validations/launch';

const initialResume: ResumeDraft = {
  fullName: '',
  email: '',
  phone: '',
  location: '',
  headline: '',
  summary: '',
  skills: '',
  education: [
    {
      id: 'education-1',
      institution: '',
      degree: '',
      startYear: '',
      endYear: '',
      grade: '',
    },
  ],
  projects: [
    {
      id: 'project-1',
      name: '',
      description: '',
      technologies: '',
      link: '',
    },
  ],
  achievements: [],
};

const navItems: { id: LaunchTab; label: string }[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'resume', label: 'Resume Builder' },
  { id: 'ats', label: 'ATS Checker' },
];

const inputClass =
  'w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--foreground)] outline-none transition placeholder:text-[var(--text-muted)] focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/10';

const buttonPrimary =
  'inline-flex items-center justify-center gap-2 rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[var(--primary-hover)] disabled:cursor-not-allowed disabled:opacity-50';

const buttonSecondary =
  'inline-flex items-center justify-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-2.5 text-sm font-medium text-[var(--foreground)] transition hover:bg-[var(--surface-alt)]';

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = 'text',
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: string;
}) {
  return (
    <label className="block min-w-0 space-y-1.5">
      <span className="text-sm font-medium text-[var(--text-label)]">
        {label}
      </span>
      <input
        className={inputClass}
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
      />
    </label>
  );
}

function TextAreaField({
  label,
  value,
  onChange,
  placeholder,
  rows = 3,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  rows?: number;
}) {
  return (
    <label className="block min-w-0 space-y-1.5">
      <span className="text-sm font-medium text-[var(--text-label)]">
        {label}
      </span>
      <textarea
        className={`${inputClass} resize-y`}
        rows={rows}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
      />
    </label>
  );
}

function SectionHeading({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h3 className="font-semibold text-[var(--foreground)]">{title}</h3>
        {description && (
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            {description}
          </p>
        )}
      </div>
      {action}
    </div>
  );
}

function EmptyState({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-dashed border-[var(--border)] px-5 py-9 text-center">
      <div className="mx-auto mb-3 flex size-11 items-center justify-center rounded-2xl bg-[var(--primary-soft)] text-xl text-[var(--primary)]">
        +
      </div>
      <p className="font-medium">{title}</p>
      <p className="mx-auto mt-1 max-w-sm text-sm text-[var(--text-secondary)]">
        {description}
      </p>
    </div>
  );
}

export default function LaunchWorkspace() {
  const [activeTab, setActiveTab] = useState<LaunchTab>('overview');
  const [resume, setResume] = useState<ResumeDraft>(initialResume);
  const [notice, setNotice] = useState('');
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const updateResume = <K extends keyof ResumeDraft>(
    key: K,
    value: ResumeDraft[K],
  ) => {
    setResume((current) => ({ ...current, [key]: value }));
    setNotice('');
  };

  const updateEducation = (
    id: string,
    key: keyof ResumeEducation,
    value: string,
  ) => {
    updateResume(
      'education',
      resume.education.map((item) =>
        item.id === id ? { ...item, [key]: value } : item,
      ),
    );
  };

  const updateProject = (
    id: string,
    key: keyof ResumeProject,
    value: string,
  ) => {
    updateResume(
      'projects',
      resume.projects.map((item) =>
        item.id === id ? { ...item, [key]: value } : item,
      ),
    );
  };

  const updateAchievement = (
    id: string,
    key: keyof ResumeAchievement,
    value: string,
  ) => {
    updateResume(
      'achievements',
      resume.achievements.map((item) =>
        item.id === id ? { ...item, [key]: value } : item,
      ),
    );
  };

  const validateResume = () => {
    const result = resumeSchema.safeParse(resume);

    if (!result.success) {
      setValidationErrors(
        result.error.issues.map(
          (issue) => `${issue.path.join('.')}: ${issue.message}`,
        ),
      );
      setNotice('');
      return false;
    }

    setValidationErrors([]);
    return true;
  };

  const handleDraftPreview = () => {
    if (!validateResume()) return;

    setNotice(
      'Preview updated. Saving and AI generation will be connected to the backend later.',
    );
  };

  const handleFile = (file?: File) => {
    setFileError('');
    setSelectedFile(null);

    if (!file) return;

    const result = atsFileSchema.safeParse({
      name: file.name,
      size: file.size,
      type: file.type,
    });

    if (!result.success) {
      setFileError(
        result.error.issues[0]?.message ??
          'Choose a supported PDF or DOCX file.',
      );
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    setSelectedFile(file);
  };

  const filledSections = [
    resume.fullName,
    resume.email,
    resume.headline,
    resume.summary,
    resume.skills,
    ...resume.education.map((item) => item.institution),
    ...resume.projects.map((item) => item.name),
  ].filter((value) => value.trim()).length;

  const completion = Math.round((filledSections / 10) * 100);
  const skills = resume.skills
    .split(',')
    .map((skill) => skill.trim())
    .filter(Boolean);

  const goTo = (tab: LaunchTab) => {
    setActiveTab(tab);
    setNotice('');
    setValidationErrors([]);
  };

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <main className="mx-auto w-full max-w-[1440px] px-4 py-6 sm:px-6 lg:px-9 lg:py-9">
        {/* Header */}
        <header className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="mb-2 flex items-center gap-2 text-xs font-medium uppercase tracking-[0.16em] text-[var(--text-secondary)]">
              <span className="size-2 rounded-full bg-[var(--feature-blue)]" />
              UniOS / Career
            </div>
            <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Launch
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--text-secondary)]">
              Turn your learning, projects and achievements into career-ready
              assets.
            </p>
          </div>

          <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2 text-xs text-[var(--text-secondary)]">
            V1 · Career tools
          </div>
        </header>

        {/* Navigation */}
        <nav className="mb-7 flex gap-1 overflow-x-auto rounded-2xl border border-[var(--border)] bg-[var(--surface-alt)] p-1.5">
          {navItems.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => goTo(item.id)}
              className={`shrink-0 rounded-xl px-4 py-2.5 text-sm font-medium transition ${
                activeTab === item.id
                  ? 'bg-[var(--primary)] text-white shadow-sm'
                  : 'text-[var(--text-secondary)] hover:bg-[var(--surface)] hover:text-[var(--foreground)]'
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>

        {/* Overview */}
        {activeTab === 'overview' && (
          <div className="space-y-7">
            <section className="relative overflow-hidden rounded-3xl bg-[var(--primary)] p-6 text-white sm:p-9">
              <div className="pointer-events-none absolute -right-12 -top-20 size-64 rounded-full border border-white/10" />
              <div className="pointer-events-none absolute -right-1 top-10 size-36 rounded-full border border-white/10" />

              <div className="relative max-w-2xl">
                <span className="inline-flex rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs text-white/85">
                  Your next step starts here
                </span>
                <h2 className="mt-5 text-2xl font-semibold leading-tight sm:text-3xl">
                  Make your work speak for you.
                </h2>
                <p className="mt-3 max-w-xl text-sm leading-6 text-white/75">
                  Build a resume from your experience and projects, then review
                  its structure and content before applying.
                </p>
                <button
                  type="button"
                  onClick={() => goTo('resume')}
                  className="mt-6 rounded-xl bg-[var(--surface)] px-4 py-3 text-sm font-semibold text-[var(--primary)] transition hover:opacity-90"
                >
                  Build your resume <span aria-hidden="true">→</span>
                </button>
              </div>
            </section>

            <section>
              <SectionHeading
                title="Career toolkit"
                description="Two focused tools to prepare your next application."
              />

              <div className="mt-4 grid gap-4 lg:grid-cols-2">
                <button
                  type="button"
                  onClick={() => goTo('resume')}
                  className="group rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 text-left transition hover:-translate-y-0.5 hover:border-[var(--feature-blue)] sm:p-6"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex size-12 items-center justify-center rounded-2xl bg-[var(--feature-blue-soft)] text-xl text-[var(--feature-blue)]">
                      ▤
                    </div>
                    <span className="text-lg text-[var(--text-muted)] transition group-hover:translate-x-1">
                      →
                    </span>
                  </div>
                  <h3 className="mt-5 text-lg font-semibold">
                    AI Resume Builder
                  </h3>
                  <p className="mt-2 max-w-md text-sm leading-6 text-[var(--text-secondary)]">
                    Organize your education, skills, projects and achievements
                    into a structured resume.
                  </p>
                  <div className="mt-5 flex flex-wrap gap-2">
                    {['Editable sections', 'Live preview', 'Profile-ready'].map(
                      (label) => (
                        <span
                          key={label}
                          className="rounded-full bg-[var(--feature-blue-soft)] px-2.5 py-1 text-xs text-[var(--feature-blue)]"
                        >
                          {label}
                        </span>
                      ),
                    )}
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => goTo('ats')}
                  className="group rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 text-left transition hover:-translate-y-0.5 hover:border-[var(--feature-orange)] sm:p-6"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex size-12 items-center justify-center rounded-2xl bg-[var(--feature-orange-soft)] text-xl text-[var(--feature-orange)]">
                      ◉
                    </div>
                    <span className="text-lg text-[var(--text-muted)] transition group-hover:translate-x-1">
                      →
                    </span>
                  </div>
                  <h3 className="mt-5 text-lg font-semibold">
                    ATS Resume Checker
                  </h3>
                  <p className="mt-2 max-w-md text-sm leading-6 text-[var(--text-secondary)]">
                    Upload an existing resume to review its structure, content
                    and areas that need improvement.
                  </p>
                  <div className="mt-5 flex flex-wrap gap-2">
                    {['Resume review', 'Missing information', 'Suggestions'].map(
                      (label) => (
                        <span
                          key={label}
                          className="rounded-full bg-[var(--feature-orange-soft)] px-2.5 py-1 text-xs text-[var(--feature-orange)]"
                        >
                          {label}
                        </span>
                      ),
                    )}
                  </div>
                </button>
              </div>
            </section>

            <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
              <SectionHeading
                title="Resume workspace"
                description="Your current editing progress on this page."
                action={
                  <button
                    type="button"
                    onClick={() => goTo('resume')}
                    className={buttonSecondary}
                  >
                    Open editor →
                  </button>
                }
              />

              <div className="mt-5 grid gap-4 sm:grid-cols-3">
                <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                  <p className="text-sm text-[var(--text-secondary)]">
                    Sections started
                  </p>
                  <p className="mt-2 text-2xl font-semibold">
                    {filledSections}
                  </p>
                </div>
                <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                  <p className="text-sm text-[var(--text-secondary)]">
                    Draft completeness
                  </p>
                  <p className="mt-2 text-2xl font-semibold">{completion}%</p>
                </div>
                <div className="rounded-xl bg-[var(--surface-alt)] p-4">
                  <p className="text-sm text-[var(--text-secondary)]">
                    ATS reports
                  </p>
                  <p className="mt-2 text-2xl font-semibold">—</p>
                  <p className="mt-1 text-xs text-[var(--text-muted)]">
                    No analysis run yet
                  </p>
                </div>
              </div>
            </section>
          </div>
        )}

        {/* Resume Builder */}
        {activeTab === 'resume' && (
          <div className="space-y-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <button
                  type="button"
                  onClick={() => goTo('overview')}
                  className="mb-3 text-sm text-[var(--text-secondary)] hover:text-[var(--primary)]"
                >
                  ← Back to Launch
                </button>
                <h2 className="text-2xl font-semibold">Resume Builder</h2>
                <p className="mt-2 text-sm text-[var(--text-secondary)]">
                  Add your information and preview the structure as you edit.
                </p>
              </div>

              <button
                type="button"
                onClick={handleDraftPreview}
                className={buttonPrimary}
              >
                Validate & preview
              </button>
            </div>

            {notice && (
              <div
                role="status"
                className="rounded-xl border border-[var(--border)] bg-[var(--primary-soft)] p-3 text-sm text-[var(--primary)]"
              >
                {notice}
              </div>
            )}

            {validationErrors.length > 0 && (
              <div
                role="alert"
                className="rounded-xl border border-[var(--danger-border)] bg-[var(--danger-soft)] p-4 text-sm text-[var(--danger-text)]"
              >
                <p className="font-semibold">
                  Please fix these validation errors:
                </p>
                <ul className="mt-2 list-inside list-disc space-y-1">
                  {validationErrors.slice(0, 6).map((error, index) => (
                    <li key={`${error}-${index}`}>{error}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(360px,0.85fr)]">
              <div className="min-w-0 space-y-5">
                <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
                  <SectionHeading
                    title="Personal information"
                    description="The essential details recruiters need."
                  />
                  <div className="mt-5 grid gap-4 sm:grid-cols-2">
                    <Field
                      label="Full name *"
                      value={resume.fullName}
                      onChange={(v) => updateResume('fullName', v)}
                      placeholder="Your full name"
                    />
                    <Field
                      label="Email *"
                      value={resume.email}
                      onChange={(v) => updateResume('email', v)}
                      placeholder="you@example.com"
                      type="email"
                    />
                    <Field
                      label="Phone"
                      value={resume.phone}
                      onChange={(v) => updateResume('phone', v)}
                      placeholder="+91 ..."
                    />
                    <Field
                      label="Location"
                      value={resume.location}
                      onChange={(v) => updateResume('location', v)}
                      placeholder="City, country"
                    />
                    <div className="sm:col-span-2">
                      <Field
                        label="Professional headline"
                        value={resume.headline}
                        onChange={(v) => updateResume('headline', v)}
                        placeholder="e.g. Software Developer"
                      />
                    </div>
                    <div className="sm:col-span-2">
                      <TextAreaField
                        label="Professional summary"
                        value={resume.summary}
                        onChange={(v) => updateResume('summary', v)}
                        placeholder="Summarize your experience, strengths and interests..."
                      />
                    </div>
                    <div className="sm:col-span-2">
                      <Field
                        label="Skills"
                        value={resume.skills}
                        onChange={(v) => updateResume('skills', v)}
                        placeholder="Python, React, SQL, ..."
                      />
                      <p className="mt-1.5 text-xs text-[var(--text-muted)]">
                        Separate skills with commas.
                      </p>
                    </div>
                  </div>
                </section>

                <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
                  <SectionHeading
                    title="Education"
                    description="Add your academic background."
                    action={
                      <button
                        type="button"
                        className={buttonSecondary}
                        onClick={() =>
                          updateResume('education', [
                            ...resume.education,
                            {
                              id: crypto.randomUUID(),
                              institution: '',
                              degree: '',
                              startYear: '',
                              endYear: '',
                              grade: '',
                            },
                          ])
                        }
                      >
                        + Add
                      </button>
                    }
                  />

                  <div className="mt-5 space-y-5">
                    {resume.education.map((item, index) => (
                      <div
                        key={item.id}
                        className="rounded-xl border border-[var(--border)] p-4"
                      >
                        <div className="mb-4 flex items-center justify-between">
                          <p className="text-sm font-medium">
                            Education {index + 1}
                          </p>
                          {resume.education.length > 1 && (
                            <button
                              type="button"
                              onClick={() =>
                                updateResume(
                                  'education',
                                  resume.education.filter(
                                    (entry) => entry.id !== item.id,
                                  ),
                                )
                              }
                              className="text-xs text-[var(--danger-text)]"
                            >
                              Remove
                            </button>
                          )}
                        </div>
                        <div className="grid gap-4 sm:grid-cols-2">
                          <Field
                            label="Institution"
                            value={item.institution}
                            onChange={(v) =>
                              updateEducation(item.id, 'institution', v)
                            }
                            placeholder="University or college"
                          />
                          <Field
                            label="Degree / qualification"
                            value={item.degree}
                            onChange={(v) =>
                              updateEducation(item.id, 'degree', v)
                            }
                            placeholder="B.Tech Computer Science"
                          />
                          <Field
                            label="Start year"
                            value={item.startYear}
                            onChange={(v) =>
                              updateEducation(item.id, 'startYear', v)
                            }
                            placeholder="2024"
                          />
                          <Field
                            label="End year"
                            value={item.endYear}
                            onChange={(v) =>
                              updateEducation(item.id, 'endYear', v)
                            }
                            placeholder="2028 or Present"
                          />
                          <div className="sm:col-span-2">
                            <Field
                              label="Grade / CGPA"
                              value={item.grade}
                              onChange={(v) =>
                                updateEducation(item.id, 'grade', v)
                              }
                              placeholder="Optional"
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
                  <SectionHeading
                    title="Projects"
                    description="Highlight work you have actually completed."
                    action={
                      <button
                        type="button"
                        className={buttonSecondary}
                        onClick={() =>
                          updateResume('projects', [
                            ...resume.projects,
                            {
                              id: crypto.randomUUID(),
                              name: '',
                              description: '',
                              technologies: '',
                              link: '',
                            },
                          ])
                        }
                      >
                        + Add
                      </button>
                    }
                  />

                  <div className="mt-5 space-y-5">
                    {resume.projects.map((item, index) => (
                      <div
                        key={item.id}
                        className="rounded-xl border border-[var(--border)] p-4"
                      >
                        <div className="mb-4 flex items-center justify-between">
                          <p className="text-sm font-medium">
                            Project {index + 1}
                          </p>
                          {resume.projects.length > 1 && (
                            <button
                              type="button"
                              onClick={() =>
                                updateResume(
                                  'projects',
                                  resume.projects.filter(
                                    (entry) => entry.id !== item.id,
                                  ),
                                )
                              }
                              className="text-xs text-[var(--danger-text)]"
                            >
                              Remove
                            </button>
                          )}
                        </div>
                        <div className="space-y-4">
                          <Field
                            label="Project name"
                            value={item.name}
                            onChange={(v) =>
                              updateProject(item.id, 'name', v)
                            }
                            placeholder="Project title"
                          />
                          <TextAreaField
                            label="Description"
                            value={item.description}
                            onChange={(v) =>
                              updateProject(item.id, 'description', v)
                            }
                            placeholder="Problem, implementation and actual results..."
                          />
                          <Field
                            label="Technologies"
                            value={item.technologies}
                            onChange={(v) =>
                              updateProject(item.id, 'technologies', v)
                            }
                            placeholder="React, FastAPI, PostgreSQL"
                          />
                          <Field
                            label="Project link"
                            value={item.link}
                            onChange={(v) =>
                              updateProject(item.id, 'link', v)
                            }
                            placeholder="https://..."
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
                  <SectionHeading
                    title="Achievements"
                    description="Include relevant awards, certifications and accomplishments."
                    action={
                      <button
                        type="button"
                        className={buttonSecondary}
                        onClick={() =>
                          updateResume('achievements', [
                            ...resume.achievements,
                            {
                              id: crypto.randomUUID(),
                              title: '',
                              description: '',
                            },
                          ])
                        }
                      >
                        + Add
                      </button>
                    }
                  />

                  {resume.achievements.length === 0 ? (
                    <div className="mt-4">
                      <EmptyState
                        title="No achievements added"
                        description="Add a certification, competition result or other relevant accomplishment."
                      />
                    </div>
                  ) : (
                    <div className="mt-5 space-y-4">
                      {resume.achievements.map((item, index) => (
                        <div
                          key={item.id}
                          className="space-y-4 rounded-xl border border-[var(--border)] p-4"
                        >
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium">
                              Achievement {index + 1}
                            </p>
                            <button
                              type="button"
                              onClick={() =>
                                updateResume(
                                  'achievements',
                                  resume.achievements.filter(
                                    (entry) => entry.id !== item.id,
                                  ),
                                )
                              }
                              className="text-xs text-[var(--danger-text)]"
                            >
                              Remove
                            </button>
                          </div>
                          <Field
                            label="Title"
                            value={item.title}
                            onChange={(v) =>
                              updateAchievement(item.id, 'title', v)
                            }
                            placeholder="Award or certification"
                          />
                          <TextAreaField
                            label="Details"
                            value={item.description}
                            onChange={(v) =>
                              updateAchievement(item.id, 'description', v)
                            }
                            placeholder="Relevant details"
                          />
                        </div>
                      ))}
                    </div>
                  )}
                </section>

                <div className="flex flex-wrap gap-3">
                  <button
                    type="button"
                    onClick={handleDraftPreview}
                    className={buttonPrimary}
                  >
                    Validate & preview
                  </button>
                  <button
                    type="button"
                    onClick={() => goTo('ats')}
                    className={buttonSecondary}
                  >
                    Check an existing resume →
                  </button>
                </div>
              </div>

              {/* Live resume preview */}
              <aside className="min-w-0 xl:sticky xl:top-6">
                <div className="mb-3 flex items-center justify-between gap-3">
                  <div>
                    <h3 className="font-semibold">Live preview</h3>
                    <p className="mt-1 text-xs text-[var(--text-secondary)]">
                      Updates as you edit
                    </p>
                  </div>
                  <span className="rounded-full bg-[var(--primary-soft)] px-2.5 py-1 text-xs text-[var(--primary)]">
                    Draft
                  </span>
                </div>

                <div className="min-h-[560px] overflow-hidden rounded-lg border border-[var(--border)] bg-white p-6 text-slate-800 shadow-sm sm:p-8">
                  <h2 className="break-words text-2xl font-bold">
                    {resume.fullName || 'Your Name'}
                  </h2>
                  <p className="mt-1 text-sm font-medium text-slate-600">
                    {resume.headline || 'Professional headline'}
                  </p>

                  <div className="mt-3 flex flex-wrap gap-x-3 gap-y-1 text-xs text-slate-500">
                    {resume.email && <span>{resume.email}</span>}
                    {resume.phone && <span>{resume.phone}</span>}
                    {resume.location && <span>{resume.location}</span>}
                  </div>

                  {resume.summary && (
                    <div className="mt-6">
                      <h3 className="border-b border-slate-300 pb-1 text-xs font-bold uppercase tracking-wider">
                        Profile
                      </h3>
                      <p className="mt-2 whitespace-pre-wrap text-xs leading-5">
                        {resume.summary}
                      </p>
                    </div>
                  )}

                  <div className="mt-6">
                    <h3 className="border-b border-slate-300 pb-1 text-xs font-bold uppercase tracking-wider">
                      Education
                    </h3>
                    <div className="mt-3 space-y-3">
                      {resume.education
                        .filter((item) => item.institution || item.degree)
                        .map((item) => (
                          <div key={item.id}>
                            <p className="text-sm font-semibold">
                              {item.degree || 'Qualification'}
                            </p>
                            <p className="mt-0.5 text-xs text-slate-600">
                              {item.institution}
                            </p>
                            <p className="mt-0.5 text-xs text-slate-500">
                              {[item.startYear, item.endYear]
                                .filter(Boolean)
                                .join(' – ')}
                              {item.grade && ` · ${item.grade}`}
                            </p>
                          </div>
                        ))}
                    </div>
                  </div>

                  {skills.length > 0 && (
                    <div className="mt-6">
                      <h3 className="border-b border-slate-300 pb-1 text-xs font-bold uppercase tracking-wider">
                        Skills
                      </h3>
                      <p className="mt-2 text-xs leading-5">
                        {skills.join(' · ')}
                      </p>
                    </div>
                  )}

                  <div className="mt-6">
                    <h3 className="border-b border-slate-300 pb-1 text-xs font-bold uppercase tracking-wider">
                      Projects
                    </h3>
                    <div className="mt-3 space-y-4">
                      {resume.projects
                        .filter((item) => item.name || item.description)
                        .map((item) => (
                          <div key={item.id}>
                            <p className="text-sm font-semibold">
                              {item.name || 'Project'}
                            </p>
                            {item.technologies && (
                              <p className="mt-0.5 text-xs text-slate-500">
                                {item.technologies}
                              </p>
                            )}
                            {item.description && (
                              <p className="mt-1 whitespace-pre-wrap text-xs leading-5">
                                {item.description}
                              </p>
                            )}
                            {item.link && (
                              <p className="mt-1 break-all text-xs text-slate-600">
                                {item.link}
                              </p>
                            )}
                          </div>
                        ))}
                    </div>
                  </div>

                  {resume.achievements.some(
                    (item) => item.title || item.description,
                  ) && (
                    <div className="mt-6">
                      <h3 className="border-b border-slate-300 pb-1 text-xs font-bold uppercase tracking-wider">
                        Achievements
                      </h3>
                      <div className="mt-3 space-y-3">
                        {resume.achievements
                          .filter((item) => item.title || item.description)
                          .map((item) => (
                            <div key={item.id}>
                              <p className="text-xs font-semibold">
                                {item.title}
                              </p>
                              {item.description && (
                                <p className="mt-1 text-xs leading-5">
                                  {item.description}
                                </p>
                              )}
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                </div>

                <p className="mt-3 text-xs leading-5 text-[var(--text-muted)]">
                  Preview only. Resume generation, persisted drafts and file
                  export will be connected when the corresponding backend
                  contracts are available.
                </p>
              </aside>
            </div>
          </div>
        )}

        {/* ATS Checker */}
        {activeTab === 'ats' && (
          <div className="mx-auto max-w-4xl space-y-6">
            <div>
              <button
                type="button"
                onClick={() => goTo('overview')}
                className="mb-3 text-sm text-[var(--text-secondary)] hover:text-[var(--primary)]"
              >
                ← Back to Launch
              </button>
              <h2 className="text-2xl font-semibold">ATS Resume Checker</h2>
              <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                Prepare your resume for review. The analysis service will be
                connected after the backend contract is available.
              </p>
            </div>

            <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-8">
              <div className="mb-5">
                <div className="flex size-12 items-center justify-center rounded-2xl bg-[var(--feature-orange-soft)] text-xl text-[var(--feature-orange)]">
                  ↑
                </div>
                <h3 className="mt-4 text-lg font-semibold">
                  Upload your resume
                </h3>
                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                  Choose a PDF or DOCX file up to 5 MB.
                </p>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                className="sr-only"
                onChange={(event) => handleFile(event.target.files?.[0])}
              />

              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex min-h-52 w-full flex-col items-center justify-center rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface-alt)] p-6 text-center transition hover:border-[var(--primary)] hover:bg-[var(--primary-soft)]/40"
              >
                <span className="flex size-12 items-center justify-center rounded-full bg-[var(--surface)] text-2xl text-[var(--primary)]">
                  ↑
                </span>
                <span className="mt-4 font-medium">
                  {selectedFile ? 'Choose another file' : 'Select a resume'}
                </span>
                <span className="mt-1 text-sm text-[var(--text-secondary)]">
                  Browse files from your device
                </span>
                <span className="mt-3 text-xs text-[var(--text-muted)]">
                  PDF / DOCX · Maximum 5 MB
                </span>
              </button>

              {selectedFile && (
                <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
                  <div className="min-w-0">
                    <p className="break-all text-sm font-medium">
                      {selectedFile.name}
                    </p>
                    <p className="mt-1 text-xs text-[var(--text-secondary)]">
                      {(selectedFile.size / 1024).toFixed(1)} KB · Selected
                      locally
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedFile(null);
                      setFileError('');
                      if (fileInputRef.current) {
                        fileInputRef.current.value = '';
                      }
                    }}
                    className="text-sm text-[var(--danger-text)]"
                  >
                    Remove
                  </button>
                </div>
              )}

              {fileError && (
                <p role="alert" className="mt-3 text-sm text-[var(--danger-text)]">
                  {fileError}
                </p>
              )}

              <div className="mt-5 flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  disabled={!selectedFile}
                  className={buttonPrimary}
                  onClick={() =>
                    setFileError(
                      'The analysis API is not connected yet. Your file has not been uploaded.',
                    )
                  }
                >
                  Check resume
                </button>
                <span className="text-xs text-[var(--text-muted)]">
                  Analysis unavailable until backend integration
                </span>
              </div>
            </section>

            <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-7">
              <SectionHeading
                title="What the analysis will cover"
                description="Planned checks for the V1 workflow."
              />

              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                {[
                  {
                    title: 'Structure and sections',
                    detail: 'Review organization and missing resume sections.',
                  },
                  {
                    title: 'Content quality',
                    detail: 'Identify unclear, vague or incomplete descriptions.',
                  },
                  {
                    title: 'ATS-oriented formatting',
                    detail: 'Flag potential readability and formatting issues.',
                  },
                  {
                    title: 'Actionable suggestions',
                    detail: 'Provide specific, understandable improvement steps.',
                  },
                ].map((item) => (
                  <div
                    key={item.title}
                    className="rounded-xl border border-[var(--border)] bg-[var(--surface-alt)] p-4"
                  >
                    <div className="flex items-start gap-3">
                      <span className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-[var(--primary-soft)] text-sm text-[var(--primary)]">
                        ✓
                      </span>
                      <div>
                        <h4 className="text-sm font-medium">{item.title}</h4>
                        <p className="mt-1 text-sm leading-5 text-[var(--text-secondary)]">
                          {item.detail}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-5 rounded-xl border border-[var(--border)] p-4">
                <p className="text-sm font-medium">Analysis results</p>
                <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
                  No report yet. Findings, missing information and improvement
                  suggestions will appear here once real analysis is available.
                </p>
              </div>
            </section>
          </div>
        )}

        <footer className="mt-10 border-t border-[var(--border)] pt-5 text-xs leading-5 text-[var(--text-muted)]">
          UniOS Launch · Career assets and preparation tools
        </footer>
      </main>
    </div>
  );
}
