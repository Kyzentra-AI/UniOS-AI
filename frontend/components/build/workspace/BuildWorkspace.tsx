'use client';

import { useMemo, useState, type FormEvent } from 'react';
import Link from 'next/link';
import { useBuild } from '@/hooks/useBuild';
import type { ArtifactType, Project } from '@/types/build';
import { Chevron, Node, ProgressRing, stagger } from '@/components/roadmap/UI';
import { BuildEmpty, BuildError, BuildLoading } from '../states/BuildStates';

const inputClass =
  'w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3.5 py-2.5 text-sm text-[var(--foreground)] outline-none transition placeholder:text-[var(--muted-foreground)] focus:border-[var(--primary)] focus:shadow-[0_0_0_4px_var(--primary-soft)]';
const card =
  'rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_8px_28px_rgba(24,52,58,0.04)] sm:p-6';
const primaryBtn =
  'rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 active:scale-[0.98] disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2';
const ghostBtn =
  'rounded-xl border border-[var(--border)] px-4 py-2.5 text-sm font-semibold text-[var(--foreground)] transition hover:border-[var(--primary)] active:scale-[0.98] disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]';
const subtle = 'rounded-xl bg-[var(--background)] p-3';

function Spinner() {
  return <span className="mr-2 inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent align-[-2px]" />;
}

export default function BuildWorkspace({ project }: { project: Project }) {
  const { getMilestones, getTasks, getArtifacts, getEvidence, loading, hydrated, error, busy, addMilestone, toggleMilestone, addTask, updateTask, addArtifact, addEvidence, generatePlan, completeProject, refreshProjectData } = useBuild(project.id);
  const milestones = getMilestones(project.id); const tasks = getTasks(project.id); const artifacts = getArtifacts(project.id); const evidence = getEvidence(project.id);
  const [milestoneTitle, setMilestoneTitle] = useState(''); const [taskTitle, setTaskTitle] = useState(''); const [taskMilestone, setTaskMilestone] = useState('');
  const [artifactTitle, setArtifactTitle] = useState(''); const [artifactType, setArtifactType] = useState<ArtifactType>('DELIVERABLE');
  const [evidenceTitle, setEvidenceTitle] = useState(''); const [formError, setFormError] = useState(''); const [notice, setNotice] = useState('');
  const completedTasks = tasks.filter((task) => task.status === 'COMPLETED').length;
  const progress = tasks.length ? Math.round(completedTasks / tasks.length * 100) : 0;
  const tasksByMilestone = useMemo(() => new Map(milestones.map((milestone) => [milestone.id, tasks.filter((task) => task.milestoneId === milestone.id)])), [milestones, tasks]);

  async function submitMilestone(event: FormEvent) { event.preventDefault(); setFormError(''); try { await addMilestone({ projectId: project.id, title: milestoneTitle, orderIdx: milestones.length }); setMilestoneTitle(''); } catch (e) { setFormError(e instanceof Error ? e.message : 'Could not add milestone.'); } }
  async function submitTask(event: FormEvent) { event.preventDefault(); setFormError(''); try { await addTask({ projectId: project.id, title: taskTitle, milestoneId: taskMilestone || undefined, orderIdx: tasks.length }); setTaskTitle(''); } catch (e) { setFormError(e instanceof Error ? e.message : 'Could not add task.'); } }
  async function submitArtifact(event: FormEvent) { event.preventDefault(); setFormError(''); try { await addArtifact({ projectId: project.id, title: artifactTitle, type: artifactType }); setArtifactTitle(''); setNotice('Artifact record created. Add a version or evidence from the Artifacts page.'); } catch (e) { setFormError(e instanceof Error ? e.message : 'Could not add artifact.'); } }
  async function submitEvidence(event: FormEvent) { event.preventDefault(); setFormError(''); try { await addEvidence({ projectId: project.id, title: evidenceTitle, skills: project.skills }); setEvidenceTitle(''); setNotice('Evidence record added to this project.'); } catch (e) { setFormError(e instanceof Error ? e.message : 'Could not add evidence.'); } }
  async function createPlan() { setFormError(''); setNotice(''); try { await generatePlan(project.id); setNotice('Plan generation finished. Workspace data has been refreshed.'); } catch (e) { setFormError(e instanceof Error ? e.message : 'Could not generate the plan.'); } }
  async function markComplete() { setFormError(''); setNotice(''); try { await completeProject(project.id); setNotice('Project marked as completed.'); } catch (e) { setFormError(e instanceof Error ? e.message : 'The project cannot be completed yet. Check that all required tasks are complete.'); } }

  if (loading && !hydrated) return <BuildLoading label="Loading project workspace…" />;

  const unassigned = tasks.filter((task) => !task.milestoneId);
  const completedMilestones = milestones.filter((item) => item.status === 'COMPLETED').length;

  return (
    <div className="space-y-6">
      {error && <BuildError message={error} onRetry={() => void refreshProjectData(project.id)} />}

      {(formError || notice) && (
        <div
          key={formError || notice}
          className={`rise flex items-start gap-2.5 rounded-2xl border p-3.5 text-sm ${
            formError
              ? 'border-red-500/30 bg-red-500/5 text-red-500'
              : 'border-[var(--border)] bg-[var(--surface)] text-[var(--muted-foreground)]'
          }`}
          role={formError ? 'alert' : 'status'}
        >
          <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${formError ? 'bg-red-500' : 'bg-[var(--primary)]'}`} />
          {formError || notice}
        </div>
      )}

      {/* Overview */}
      <section className={`rise ${card} sm:p-7`}>
        <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-start">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full border border-[var(--border)] px-2.5 py-1 text-xs font-medium text-[var(--muted-foreground)]">
                {project.type.toLowerCase()}
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-[var(--surface-alt)] px-2.5 py-1 text-xs font-medium text-[var(--muted-foreground)]">
                <span className="h-1.5 w-1.5 rounded-full bg-current" />
                {project.status.replace('_', ' ')}
              </span>
            </div>
            <h2 className="mt-3 text-xl font-semibold text-[var(--foreground)]">Project progress</h2>
            <p className="mt-1 max-w-2xl text-sm leading-6 text-[var(--muted-foreground)]">
              {project.goal || project.description || 'Define the goal for this project and break the work into milestones.'}
            </p>
          </div>

          <div className="flex w-full shrink-0 flex-col gap-2 sm:w-auto sm:flex-row">
            <button type="button" onClick={() => void createPlan()} disabled={busy === 'generate-plan'} className={ghostBtn}>
              {busy === 'generate-plan' ? <><Spinner />Generating…</> : 'Generate plan'}
            </button>
            <button type="button" onClick={() => void markComplete()} disabled={project.status === 'COMPLETED' || busy === 'complete-project'} className={primaryBtn}>
              {project.status === 'COMPLETED' ? 'Completed' : busy === 'complete-project' ? <><Spinner />Completing…</> : 'Complete project'}
            </button>
          </div>
        </div>

        <div className="mt-6 flex flex-col items-center gap-6 border-t border-[var(--border)] pt-6 sm:flex-row sm:gap-8">
          <ProgressRing value={progress} size={112} stroke={10} />

          <div className="w-full min-w-0 flex-1">
            <div className="grid grid-cols-3 divide-x divide-[var(--border)] text-center sm:text-left">
              {[
                { label: 'Tasks done', value: completedTasks, of: tasks.length },
                { label: 'Milestones', value: completedMilestones, of: milestones.length },
                { label: 'Outputs', value: artifacts.length + evidence.length },
              ].map((stat, i) => (
                <div key={stat.label} className={i > 0 ? 'px-2 sm:px-5' : 'pr-2 sm:pr-5'}>
                  <p className="text-2xl font-bold tracking-tight text-[var(--foreground)] sm:text-3xl">
                    {stat.value}
                    {stat.of !== undefined && <span className="text-base font-normal text-[var(--muted-foreground)]"> / {stat.of}</span>}
                  </p>
                  <p className="mt-0.5 text-xs text-[var(--muted-foreground)]">{stat.label}</p>
                </div>
              ))}
            </div>

            {tasks.length > 0 && (
              <div className="mt-5 flex gap-[3px]" role="img" aria-label={`${completedTasks} of ${tasks.length} tasks completed`}>
                {tasks.map((task, i) => (
                  <span
                    key={task.id}
                    className="seg h-2 flex-1 rounded-full"
                    style={{ ...stagger(Math.min(i, 40)), backgroundColor: task.status === 'COMPLETED' ? 'var(--primary)' : 'var(--border)' }}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.25fr_0.75fr] xl:items-start">
        {/* Milestones & tasks */}
        <div className={`rise ${card}`} style={stagger(1)}>
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h2 className="text-lg font-semibold text-[var(--foreground)]">Milestones & tasks</h2>
              <p className="mt-1 text-sm text-[var(--muted-foreground)]">Track the work in small, verifiable steps.</p>
            </div>
            <span className="shrink-0 rounded-full border border-[var(--border)] px-2.5 py-1 text-xs font-medium text-[var(--muted-foreground)]">
              {completedTasks}/{tasks.length} tasks done
            </span>
          </div>

          {milestones.length ? (
            <ol className="relative mt-6">
              <span aria-hidden="true" className="line-grow absolute bottom-8 left-[14px] top-8 w-px bg-[var(--border)]" />

              {milestones.map((milestone, i) => {
                const items = tasksByMilestone.get(milestone.id) ?? [];
                const done = milestone.status === 'COMPLETED';
                const itemsDone = items.filter((task) => task.status === 'COMPLETED').length;
                const itemPct = items.length ? Math.round((itemsDone / items.length) * 100) : 0;

                return (
                  <li key={milestone.id} className="rise relative pb-3 pl-11 last:pb-0" style={stagger(Math.min(i, 8))}>
                    <button
                      type="button"
                      aria-label={`Mark milestone ${milestone.title} ${done ? 'pending' : 'completed'}`}
                      onClick={() => void toggleMilestone(milestone).catch((e) => setFormError(e instanceof Error ? e.message : 'Could not update milestone.'))}
                      className="absolute left-0 top-4 rounded-full transition active:scale-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2"
                    >
                      <Node state={done ? 'done' : milestone.status === 'IN_PROGRESS' ? 'active' : 'idle'}>{i + 1}</Node>
                    </button>

                    <div className="rounded-2xl border border-[var(--border)] p-4">
                      <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1">
                        <h3 className={`font-semibold leading-snug ${done ? 'text-[var(--muted-foreground)] line-through' : 'text-[var(--foreground)]'}`}>
                          {milestone.title}
                        </h3>
                        <span className="text-xs text-[var(--muted-foreground)]">{items.length} tasks</span>
                      </div>

                      {milestone.description && <p className="mt-1 text-sm leading-6 text-[var(--muted-foreground)]">{milestone.description}</p>}

                      {items.length > 0 && (
                        <>
                          <div className="mt-3 h-1 overflow-hidden rounded-full bg-[var(--border)]">
                            <div className="h-full rounded-full bg-[var(--primary)] transition-all duration-500" style={{ width: `${itemPct}%` }} />
                          </div>

                          <div className="mt-3 space-y-2">
                            {items.map((task) => (
                              <label key={task.id} className="flex cursor-pointer items-start gap-3 rounded-xl bg-[var(--background)] px-3 py-2.5 transition hover:bg-[var(--surface-hover)]">
                                <input
                                  type="checkbox"
                                  checked={task.status === 'COMPLETED'}
                                  onChange={(e) => void updateTask(task.id, { status: e.target.checked ? 'COMPLETED' : 'PENDING' }).catch((cause) => setFormError(cause instanceof Error ? cause.message : 'Could not update task.'))}
                                  className="mt-0.5 h-4 w-4 shrink-0 accent-[var(--primary)]"
                                />
                                <span className={`min-w-0 text-sm ${task.status === 'COMPLETED' ? 'text-[var(--muted-foreground)] line-through' : 'text-[var(--foreground)]'}`}>
                                  {task.title}
                                  {task.description && <span className="mt-0.5 block text-xs leading-5 text-[var(--muted-foreground)]">{task.description}</span>}
                                </span>
                              </label>
                            ))}
                          </div>
                        </>
                      )}
                    </div>
                  </li>
                );
              })}
            </ol>
          ) : (
            <div className="mt-6">
              <BuildEmpty title="No milestones yet" description="Generate a plan to ask the backend to create a structured plan, or add your own milestone below." />
            </div>
          )}

          <div className="mt-6 space-y-2.5 rounded-2xl bg-[var(--background)] p-3 sm:p-4">
            <form onSubmit={submitMilestone} className="flex gap-2">
              <input value={milestoneTitle} onChange={(e) => setMilestoneTitle(e.target.value)} required className={inputClass} placeholder="Add a milestone" />
              <button className={`${primaryBtn} shrink-0`}>Add</button>
            </form>

            <form onSubmit={submitTask} className="grid gap-2 sm:grid-cols-[1fr_0.8fr_auto]">
              <input value={taskTitle} onChange={(e) => setTaskTitle(e.target.value)} required className={inputClass} placeholder="Add a task" />
              <select value={taskMilestone} onChange={(e) => setTaskMilestone(e.target.value)} className={inputClass}>
                <option value="">No milestone</option>
                {milestones.map((milestone) => <option key={milestone.id} value={milestone.id}>{milestone.title}</option>)}
              </select>
              <button className={ghostBtn}>Add task</button>
            </form>
          </div>

          {unassigned.length > 0 && (
            <div className="mt-6">
              <p className="mb-2 text-sm font-semibold text-[var(--foreground)]">Unassigned tasks</p>
              {unassigned.map((task) => (
                <label key={task.id} className="mb-2 flex cursor-pointer items-start gap-3 rounded-xl bg-[var(--background)] px-3 py-2.5 transition hover:bg-[var(--surface-hover)]">
                  <input
                    type="checkbox"
                    checked={task.status === 'COMPLETED'}
                    onChange={(e) => void updateTask(task.id, { status: e.target.checked ? 'COMPLETED' : 'PENDING' })}
                    className="mt-0.5 h-4 w-4 shrink-0 accent-[var(--primary)]"
                  />
                  <span className="text-sm text-[var(--foreground)]">{task.title}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        {/* Side column */}
        <div className="space-y-6">
          <div className={`rise ${card}`} style={stagger(2)}>
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <h2 className="text-lg font-semibold text-[var(--foreground)]">Project artifacts</h2>
                <p className="mt-1 text-sm text-[var(--muted-foreground)]">Documents, deliverables, and recorded outputs.</p>
              </div>
              <Link href={`/build/${project.id}/artifacts`} className="group inline-flex shrink-0 items-center gap-0.5 rounded-md py-1 text-sm font-medium text-[var(--primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]">
                View all
                <Chevron className="transition-transform duration-200 group-hover:translate-x-0.5" />
              </Link>
            </div>

            {artifacts.length ? (
              <div className="mt-4 space-y-2">
                {artifacts.slice(0, 4).map((artifact) => (
                  <div key={artifact.id} className={subtle}>
                    <p className="text-sm font-medium text-[var(--foreground)]">{artifact.title}</p>
                    <p className="mt-1 text-xs text-[var(--muted-foreground)]">{artifact.type.toLowerCase()} · {artifact.versions?.length ?? 0} versions</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="mt-4 text-sm text-[var(--muted-foreground)]">No artifacts have been recorded yet.</p>
            )}

            <form onSubmit={submitArtifact} className="mt-4 space-y-2">
              <input value={artifactTitle} onChange={(e) => setArtifactTitle(e.target.value)} required className={inputClass} placeholder="Artifact title" />
              <div className="flex gap-2">
                <select value={artifactType} onChange={(e) => setArtifactType(e.target.value as ArtifactType)} className={inputClass}>
                  {(['DOCUMENT', 'UPLOAD', 'DELIVERABLE', 'PRESENTATION', 'EVIDENCE'] as ArtifactType[]).map((item) => <option key={item} value={item}>{item.toLowerCase()}</option>)}
                </select>
                <button className={`${ghostBtn} shrink-0`}>Add</button>
              </div>
              <p className="text-xs leading-5 text-[var(--muted-foreground)]">This creates an artifact record. Binary file storage is not exposed by the supplied API contract.</p>
            </form>
          </div>

          <div className={`rise ${card}`} style={stagger(3)}>
            <h2 className="text-lg font-semibold text-[var(--foreground)]">Evidence of learning</h2>
            <p className="mt-1 text-sm text-[var(--muted-foreground)]">Capture the output or skill evidence this project produces.</p>

            {evidence.length ? (
              <div className="mt-4 space-y-2">
                {evidence.slice(0, 3).map((item) => (
                  <div key={item.id} className={subtle}>
                    <p className="text-sm font-medium text-[var(--foreground)]">{item.title}</p>
                    {item.skills.length > 0 && <p className="mt-1 text-xs text-[var(--muted-foreground)]">{item.skills.join(' · ')}</p>}
                  </div>
                ))}
              </div>
            ) : (
              <p className="mt-4 text-sm text-[var(--muted-foreground)]">No evidence has been added yet.</p>
            )}

            <form onSubmit={submitEvidence} className="mt-4 flex gap-2">
              <input value={evidenceTitle} onChange={(e) => setEvidenceTitle(e.target.value)} required className={inputClass} placeholder="Evidence title" />
              <button className={`${primaryBtn} shrink-0`}>Add</button>
            </form>
          </div>

          <div className="rise rounded-3xl border border-[var(--border)] bg-[var(--primary-soft)] p-5 sm:p-6" style={stagger(4)}>
            <h2 className="text-lg font-semibold text-[var(--foreground)]">Need help moving forward?</h2>
            <p className="mt-1 text-sm leading-6 text-[var(--muted-foreground)]">
              Ask the project Coach for an explanation, a next step, or feedback grounded in this workspace.
            </p>
            <Link
              href={`/build/${project.id}/coach`}
              className="group mt-4 inline-flex w-full items-center justify-center gap-1 rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2 sm:w-auto"
            >
              Open project Coach
              <Chevron className="transition-transform duration-200 group-hover:translate-x-0.5" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}