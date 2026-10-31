'use client';

import { useState, type FormEvent } from 'react';
import Link from 'next/link';
import { useBuild } from '@/hooks/useBuild';
import { createProjectSchema } from '@/app/validations/build';
import type { CreateProjectInput, ProjectType, RecommendedProject } from '@/types/build';
import { Chevron, stagger } from '@/components/roadmap/UI';
import { BuildEmpty, BuildError, BuildLoading } from '../states/BuildStates';

const typeOptions: { value: ProjectType; label: string }[] = [
  { value: 'CODING', label: 'Coding / software' }, { value: 'RESEARCH', label: 'Research' },
  { value: 'BUSINESS', label: 'Business' }, { value: 'ANALYSIS', label: 'Data analysis' },
  { value: 'DESIGN', label: 'Design' }, { value: 'OTHER', label: 'Other' },
];

const fieldClass =
  'mt-1.5 w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-3.5 py-2.5 text-sm text-[var(--foreground)] outline-none transition placeholder:text-[var(--muted-foreground)] focus:border-[var(--primary)] focus:shadow-[0_0_0_4px_var(--primary-soft)]';
const primaryBtn =
  'rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 active:scale-[0.98] disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2';
const chip =
  'rounded-full border border-[var(--border)] px-2.5 py-1 text-xs font-medium text-[var(--muted-foreground)]';

const statusTone = (status: string) =>
  status === 'COMPLETED'
    ? { bg: 'var(--primary-soft)', fg: 'var(--primary)' }
    : status === 'IN_PROGRESS'
      ? { bg: 'var(--feature-blue-soft)', fg: 'var(--feature-blue)' }
      : { bg: 'var(--surface-alt)', fg: 'var(--muted-foreground)' };

export default function BuildProjects() {
  const { projects, recommendations, loading, hydrated, error, busy, refresh, createProject } = useBuild();
  const [showCreate, setShowCreate] = useState(false);
  const [formError, setFormError] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState<ProjectType>('CODING');
  const [domain, setDomain] = useState('');
  const [goal, setGoal] = useState('');
  const [skillsText, setSkillsText] = useState('');

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setFormError('');
    const payload: CreateProjectInput = { title, description, type, domain, goal, skills: skillsText.split(',').map((skill) => skill.trim()).filter(Boolean) };
    const parsed = createProjectSchema.safeParse(payload);
    if (!parsed.success) { setFormError(parsed.error.issues[0]?.message ?? 'Please check the form.'); return; }
    try { await createProject(parsed.data); setTitle(''); setDescription(''); setDomain(''); setGoal(''); setSkillsText(''); setType('CODING'); setShowCreate(false); await refresh(); }
    catch (cause) { setFormError(cause instanceof Error ? cause.message : 'Could not create this project.'); }
  }
  async function useRecommendation(item: RecommendedProject) {
    try { const project = await createProject({ title: item.title, description: item.description, type: item.type, skills: item.skills }); window.location.href = `/build/${project.id}`; }
    catch (cause) { setFormError(cause instanceof Error ? cause.message : 'Could not create this project.'); }
  }

  return (
    <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-10 lg:px-8">
      <header className="rise flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div className="min-w-0">
          <h1 className="text-[28px] font-semibold leading-tight tracking-tight text-[var(--foreground)] sm:text-4xl">
            Turn your learning into proof.
          </h1>
          <p className="mt-3 max-w-2xl text-[15px] leading-6 text-[var(--muted-foreground)]">
            Plan and complete real projects, collect artifacts, and keep evidence of the skills you build along the way.
          </p>
        </div>

        <button
          type="button"
          aria-expanded={showCreate}
          onClick={() => setShowCreate((value) => !value)}
          className={`${primaryBtn} w-full shrink-0 sm:w-auto`}
        >
          {showCreate ? 'Close form' : 'Create project'}
        </button>
      </header>

      {formError && !showCreate && (
        <p role="alert" className="rise mt-5 rounded-2xl border border-red-500/30 bg-red-500/5 p-3.5 text-sm text-red-500">
          {formError}
        </p>
      )}

      {showCreate && (
        <form
          onSubmit={submit}
          className="rise mt-7 rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_8px_28px_rgba(24,52,58,0.04)] sm:p-7"
        >
          <h2 className="text-lg font-semibold text-[var(--foreground)]">New project</h2>
          <p className="mt-1 text-sm text-[var(--muted-foreground)]">
            Start with a clear goal. You can generate a plan after creating it.
          </p>

          <div className="mt-6 grid gap-5 sm:grid-cols-2">
            <label className="text-sm font-medium text-[var(--foreground)] sm:col-span-2">
              Project title
              <input required value={title} onChange={(e) => setTitle(e.target.value)} className={fieldClass} placeholder="e.g. Research a retrieval evaluation method" />
            </label>

            <div className="sm:col-span-2" role="radiogroup" aria-label="Project type">
              <p className="text-sm font-medium text-[var(--foreground)]">Project type</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {typeOptions.map((option) => {
                  const active = type === option.value;
                  return (
                    <button
                      key={option.value}
                      type="button"
                      role="radio"
                      aria-checked={active}
                      onClick={() => setType(option.value)}
                      className={`rounded-full border px-3.5 py-1.5 text-sm font-medium transition active:scale-[0.97] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] ${
                        active
                          ? 'border-[var(--primary)] bg-[var(--primary-soft)] text-[var(--primary)]'
                          : 'border-[var(--border)] text-[var(--muted-foreground)] hover:border-[var(--primary)] hover:text-[var(--foreground)]'
                      }`}
                    >
                      {option.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <label className="text-sm font-medium text-[var(--foreground)]">
              Domain
              <input value={domain} onChange={(e) => setDomain(e.target.value)} className={fieldClass} placeholder="e.g. AI, climate, product design" />
            </label>

            <label className="text-sm font-medium text-[var(--foreground)]">
              Skills to practice <span className="font-normal text-[var(--muted-foreground)]">(comma-separated)</span>
              <input value={skillsText} onChange={(e) => setSkillsText(e.target.value)} className={fieldClass} placeholder="Python, research, communication" />
            </label>

            <label className="text-sm font-medium text-[var(--foreground)] sm:col-span-2">
              Description
              <textarea value={description} onChange={(e) => setDescription(e.target.value)} className={fieldClass} rows={2} placeholder="What are you planning to make or investigate?" />
            </label>

            <label className="text-sm font-medium text-[var(--foreground)] sm:col-span-2">
              Goal
              <textarea value={goal} onChange={(e) => setGoal(e.target.value)} className={fieldClass} rows={2} placeholder="What should be true when this project is finished?" />
            </label>
          </div>

          {formError && <p role="alert" className="mt-4 text-sm text-red-500">{formError}</p>}

          <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={() => setShowCreate(false)}
              className="rounded-xl border border-[var(--border)] px-4 py-2.5 text-sm font-semibold text-[var(--foreground)] transition hover:bg-[var(--surface-hover)]"
            >
              Cancel
            </button>
            <button disabled={busy === 'create-project'} className={primaryBtn}>
              {busy === 'create-project' ? 'Creating…' : 'Create project'}
            </button>
          </div>
        </form>
      )}

      {error && !loading && <div className="mt-6"><BuildError message={error} onRetry={() => void refresh()} /></div>}

      <section className="mt-10">
        <div className="mb-5 flex items-end justify-between gap-4">
          <div className="min-w-0">
            <h2 className="text-xl font-semibold text-[var(--foreground)]">Your projects</h2>
            <p className="mt-1 text-sm text-[var(--muted-foreground)]">A single workspace for plans, work, and evidence.</p>
          </div>
          <span className={`${chip} shrink-0`}>{projects.length} total</span>
        </div>

        {loading && !hydrated ? (
          <BuildLoading label="Loading projects…" />
        ) : projects.length ? (
          <ul className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {projects.map((project, i) => {
              const tone = statusTone(project.status);
              return (
                <li key={project.id} className="rise" style={stagger(Math.min(i, 8))}>
                  <Link
                    href={`/build/${project.id}`}
                    className="group flex h-full flex-col rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5 transition duration-200 hover:-translate-y-0.5 hover:border-[var(--primary)] hover:shadow-[0_12px_30px_rgba(24,52,58,0.08)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <span className={chip}>{project.type.toLowerCase().replace('_', ' ')}</span>
                      <span
                        className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium"
                        style={{ backgroundColor: tone.bg, color: tone.fg }}
                      >
                        <span className="h-1.5 w-1.5 rounded-full bg-current" />
                        {project.status.replace('_', ' ')}
                      </span>
                    </div>

                    <h3 className="mt-4 text-lg font-semibold leading-snug text-[var(--foreground)]">
                      {project.title}
                    </h3>

                    <p className="mt-2 line-clamp-2 min-h-10 text-sm leading-5 text-[var(--muted-foreground)]">
                      {project.description || project.goal || 'Add a goal and generate a plan to get started.'}
                    </p>

                    {project.skills.length > 0 && (
                      <div className="mt-4 flex flex-wrap gap-1.5">
                        {project.skills.slice(0, 4).map((skill) => (
                          <span key={skill} className="rounded-lg bg-[var(--background)] px-2 py-1 text-xs text-[var(--muted-foreground)]">
                            {skill}
                          </span>
                        ))}
                      </div>
                    )}

                    <div className="mt-auto pt-5">
                      <div className="flex items-center justify-between border-t border-[var(--border)] pt-3.5 text-sm">
                        <span className="font-medium text-[var(--foreground)]">Open workspace</span>
                        <Chevron className="text-[var(--primary)] transition-transform duration-200 group-hover:translate-x-1" />
                      </div>
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        ) : (
          <BuildEmpty
            title="Your first project starts here"
            description="Create a project from your own idea, or choose a recommendation below to start with a useful direction."
            action={<button onClick={() => setShowCreate(true)} className={primaryBtn}>Create a project</button>}
          />
        )}
      </section>

      {recommendations.length > 0 && (
        <section className="mt-12">
          <div className="mb-5">
            <h2 className="text-xl font-semibold text-[var(--foreground)]">Recommended starting points</h2>
            <p className="mt-1 text-sm text-[var(--muted-foreground)]">Suggestions returned by your Build recommendation service.</p>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {recommendations.map((item, index) => (
              <article
                key={`${item.title}-${index}`}
                className="rise flex flex-col rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5"
                style={stagger(Math.min(index, 8))}
              >
                <span className={`${chip} w-fit`}>{item.type.toLowerCase()}</span>
                <h3 className="mt-3 font-semibold leading-snug text-[var(--foreground)]">{item.title}</h3>
                <p className="mt-2 flex-1 text-sm leading-6 text-[var(--muted-foreground)]">{item.description}</p>

                <div className="mt-3 flex flex-wrap gap-1.5">
                  {item.skills.map((skill) => (
                    <span key={skill} className="rounded-lg bg-[var(--background)] px-2 py-1 text-xs text-[var(--muted-foreground)]">{skill}</span>
                  ))}
                </div>

                <button
                  type="button"
                  disabled={busy === 'create-project'}
                  onClick={() => void useRecommendation(item)}
                  className="mt-5 rounded-xl border border-[var(--border)] px-3 py-2.5 text-sm font-semibold text-[var(--foreground)] transition hover:border-[var(--primary)] hover:bg-[var(--primary-soft)] active:scale-[0.98] disabled:opacity-60"
                >
                  Use this idea
                </button>
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}