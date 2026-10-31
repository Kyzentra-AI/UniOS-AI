'use client';

import { useMemo, useState, type FormEvent } from 'react';
import Link from 'next/link';
import { useBuild } from '@/hooks/useBuild';
import { Chevron, Node, ProgressRing, stagger } from '@/components/roadmap/UI';
import { BuildError, BuildLoading } from '../states/BuildStates';

const starters = [
  { label: 'Help me choose the next step', intent: 'NEXT_STEP', message: 'Based on my current project progress, what should I work on next and why?' },
  { label: 'Review my project plan', intent: 'PLAN_REVIEW', message: 'Review my current milestones and tasks. What gaps or risks should I address?' },
  { label: 'Explain a difficult concept', intent: 'EXPLANATION', message: 'Help me understand the key concept I need for this project. Start with the intuition, then give a practical example.' },
  { label: 'Improve the final deliverable', intent: 'DELIVERABLE_FEEDBACK', message: 'What should a strong final deliverable for this project contain, and how can I evaluate its quality?' },
];
const inputClass =
  'w-full rounded-2xl border border-[var(--border)] bg-[var(--background)] px-4 py-3 text-sm leading-6 text-[var(--foreground)] outline-none transition placeholder:text-[var(--muted-foreground)] focus:border-[var(--primary)] focus:shadow-[0_0_0_4px_var(--primary-soft)]';

function actionText(item: Record<string, unknown>): string {
  for (const key of ['title', 'description', 'action', 'task', 'text']) if (typeof item[key] === 'string') return item[key] as string;
  return JSON.stringify(item);
}

export default function BuildCoach({ projectId }: { projectId: string }) {
  const { getProject, getMilestones, getTasks, getArtifacts, loading, hydrated, error, busy, askCoach, refreshProjectData } = useBuild(projectId);
  const project = getProject(projectId); const milestones = getMilestones(projectId); const tasks = getTasks(projectId); const artifacts = getArtifacts(projectId);
  const [message, setMessage] = useState(''); const [reply, setReply] = useState(''); const [suggestions, setSuggestions] = useState<string[]>([]); const [actions, setActions] = useState<Record<string, unknown>[]>([]); const [requestError, setRequestError] = useState('');
  const completedTasks = tasks.filter((task) => task.status === 'COMPLETED').length;
  const context = useMemo(() => ({ project: project ? { id: project.id, title: project.title, type: project.type, goal: project.goal, skills: project.skills, status: project.status } : undefined, milestones: milestones.map(({ title, status, orderIdx }) => ({ title, status, orderIdx })), tasks: tasks.map(({ title, status, milestoneId }) => ({ title, status, milestoneId })), artifactCount: artifacts.length }), [project, milestones, tasks, artifacts.length]);

  async function send(event?: FormEvent, preset?: typeof starters[number]) {
    event?.preventDefault(); const text = preset?.message ?? message.trim(); if (!text) return;
    setRequestError(''); setReply(''); setSuggestions([]); setActions([]);
    try { const response = await askCoach(projectId, { intent: preset?.intent ?? 'PROJECT_GUIDANCE', message: text, context }); setReply(response.reply); setSuggestions(response.suggestions ?? []); setActions(response.actionItems ?? []); setMessage(''); }
    catch (cause) { setRequestError(cause instanceof Error ? cause.message : 'The Coach could not respond. Please try again.'); }
  }

  if (loading && !hydrated) return <BuildLoading label="Loading project context…" />;
  if (!project) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <BuildError message={error ?? 'This project could not be found.'} onRetry={() => void refreshProjectData(projectId)} />
        <Link href="/build" className="mt-4 inline-block text-sm font-medium text-[var(--primary)]">Back to Build</Link>
      </div>
    );
  }

  const progress = tasks.length ? Math.round((completedTasks / tasks.length) * 100) : 0;
  const thinking = busy === 'coach';

  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-10 lg:px-8">
      <Link href={`/build/${projectId}`} className="group inline-flex items-center gap-1 rounded-md py-1 text-sm font-medium text-[var(--primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]">
        <Chevron className="rotate-180 transition-transform duration-200 group-hover:-translate-x-0.5" />
        Back to workspace
      </Link>

      <div className="mt-5 grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-start">
        <section className="min-w-0">
          <header className="rise">
            <p className="text-sm text-[var(--muted-foreground)]">Build · Project Coach</p>
            <h1 className="mt-1 text-[28px] font-semibold leading-tight tracking-tight text-[var(--foreground)] sm:text-3xl">
              Think through the next move.
            </h1>
            <p className="mt-2 max-w-2xl text-[15px] leading-6 text-[var(--muted-foreground)]">
              Ask for guidance on your plan, a concept, or a deliverable. The current project context is included with your message.
            </p>
          </header>

          {error && <div className="mt-5"><BuildError message={error} onRetry={() => void refreshProjectData(projectId)} /></div>}

          <div className="rise mt-6 rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_8px_28px_rgba(24,52,58,0.04)] sm:p-6" style={stagger(1)}>
            <p className="mb-3 text-sm font-semibold text-[var(--foreground)]">Start with a prompt</p>
            <div className="grid gap-2.5 sm:grid-cols-2">
              {starters.map((starter) => (
                <button
                  key={starter.intent}
                  type="button"
                  onClick={() => void send(undefined, starter)}
                  disabled={thinking}
                  className="group flex items-start justify-between gap-3 rounded-2xl border border-[var(--border)] p-3.5 text-left text-sm font-medium text-[var(--foreground)] transition duration-200 hover:-translate-y-px hover:border-[var(--primary)] hover:shadow-[0_8px_22px_rgba(24,52,58,0.07)] active:scale-[0.99] disabled:opacity-60 disabled:hover:translate-y-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]"
                >
                  <span>
                    {starter.label}
                    <span className="mt-1 block text-xs font-normal text-[var(--muted-foreground)]">Send a contextual prompt</span>
                  </span>
                  <Chevron className="mt-0.5 shrink-0 text-[var(--muted-foreground)] transition-transform duration-200 group-hover:translate-x-0.5" />
                </button>
              ))}
            </div>

            <form onSubmit={(event) => void send(event)} className="mt-6 border-t border-[var(--border)] pt-5">
              <label htmlFor="coach-message" className="mb-2 block text-sm font-semibold text-[var(--foreground)]">Your question</label>
              <textarea
                id="coach-message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={4}
                maxLength={5000}
                className={inputClass}
                placeholder="Tell the Coach what you're trying to solve, what you've tried, or where you're stuck…"
              />
              <div className="mt-3 flex flex-col-reverse items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
                <span className="text-xs text-[var(--muted-foreground)]">{message.length}/5000 characters</span>
                <button
                  disabled={!message.trim() || thinking}
                  className="rounded-xl bg-[var(--primary)] px-5 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 active:scale-[0.98] disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2"
                >
                  {thinking ? 'Thinking…' : 'Ask Coach'}
                </button>
              </div>
            </form>

            {requestError && (
              <p role="alert" className="rise mt-4 rounded-2xl border border-red-500/30 bg-red-500/5 p-3.5 text-sm text-red-500">
                {requestError}
              </p>
            )}

            {thinking && (
              <div className="rise mt-6 border-t border-[var(--border)] pt-5" role="status" aria-live="polite">
                <div className="flex items-center gap-2 text-sm text-[var(--muted-foreground)]">
                  Coach is thinking
                  <span className="flex gap-1" aria-hidden="true">
                    {[0, 1, 2].map((n) => (
                      <span key={n} className="h-1.5 w-1.5 animate-bounce rounded-full bg-[var(--primary)]" style={{ animationDelay: `${n * 0.15}s` }} />
                    ))}
                  </span>
                </div>
                <div className="mt-4 space-y-2.5" aria-hidden="true">
                  <div className="skeleton h-4 w-full rounded-md" />
                  <div className="skeleton h-4 w-11/12 rounded-md" />
                  <div className="skeleton h-4 w-3/5 rounded-md" />
                </div>
              </div>
            )}

            {reply && (
              <div className="rise mt-6 border-t border-[var(--border)] pt-5">
                <h2 className="text-sm font-semibold text-[var(--foreground)]">Coach response</h2>
                <div className="mt-3 whitespace-pre-wrap break-words text-[15px] leading-7 text-[var(--foreground)]">{reply}</div>

                {suggestions.length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-sm font-semibold text-[var(--foreground)]">Suggested follow-ups</h3>
                    <div className="mt-2.5 flex flex-wrap gap-2">
                      {suggestions.map((suggestion, index) => (
                        <button
                          key={`${suggestion}-${index}`}
                          onClick={() => setMessage(suggestion)}
                          className="rise rounded-full border border-[var(--border)] px-3.5 py-1.5 text-left text-xs leading-5 text-[var(--foreground)] transition hover:border-[var(--primary)] hover:bg-[var(--primary-soft)] active:scale-[0.98]"
                          style={stagger(index)}
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {actions.length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-sm font-semibold text-[var(--foreground)]">Action items</h3>
                    <ol className="relative mt-3">
                      <span aria-hidden="true" className="line-grow absolute bottom-6 left-[14px] top-6 w-px bg-[var(--border)]" />
                      {actions.map((action, index) => (
                        <li key={index} className="rise relative pb-2.5 pl-11 last:pb-0" style={stagger(Math.min(index, 8))}>
                          <span className="absolute left-0 top-2"><Node state="idle">{index + 1}</Node></span>
                          <div className="rounded-2xl bg-[var(--background)] p-3.5 text-sm leading-6 text-[var(--foreground)]">{actionText(action)}</div>
                        </li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            )}
          </div>
        </section>

        <aside className="rise rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_8px_28px_rgba(24,52,58,0.04)] lg:sticky lg:top-6" style={stagger(2)}>
          <p className="text-sm text-[var(--muted-foreground)]">Project context</p>
          <h2 className="mt-1 text-lg font-semibold leading-snug text-[var(--foreground)]">{project.title}</h2>
          <p className="mt-1 text-sm leading-5 text-[var(--muted-foreground)]">{project.goal || project.description || 'No project goal has been set.'}</p>

          <div className="mt-5 flex items-center gap-4 border-t border-[var(--border)] pt-5">
            <ProgressRing value={progress} size={72} stroke={7} />
            <div className="min-w-0 flex-1 space-y-2.5">
              {[
                ['Type', project.type.toLowerCase()],
                ['Milestones', String(milestones.length)],
                ['Tasks complete', `${completedTasks}/${tasks.length}`],
                ['Artifacts', String(artifacts.length)],
              ].map(([label, value]) => (
                <div key={label} className="flex justify-between gap-3 text-sm">
                  <span className="text-[var(--muted-foreground)]">{label}</span>
                  <span className="text-right font-medium text-[var(--foreground)]">{value}</span>
                </div>
              ))}
            </div>
          </div>

          {project.skills.length > 0 && (
            <div className="mt-5 border-t border-[var(--border)] pt-5">
              <p className="text-sm font-semibold text-[var(--foreground)]">Skills</p>
              <div className="mt-2.5 flex flex-wrap gap-1.5">
                {project.skills.map((skill) => (
                  <span key={skill} className="rounded-lg bg-[var(--background)] px-2 py-1 text-xs text-[var(--muted-foreground)]">{skill}</span>
                ))}
              </div>
            </div>
          )}
        </aside>
      </div>
    </main>
  );
}