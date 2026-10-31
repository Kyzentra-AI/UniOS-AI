'use client';

import { useState, type FormEvent } from 'react';
import Link from 'next/link';
import { useBuild } from '@/hooks/useBuild';
import type { ArtifactType } from '@/types/build';
import { Chevron, stagger } from '@/components/roadmap/UI';
import { BuildEmpty, BuildError, BuildLoading } from '../states/BuildStates';

const inputClass =
  'w-full rounded-xl border border-[var(--border)] bg-[var(--background)] px-3.5 py-2.5 text-sm text-[var(--foreground)] outline-none transition placeholder:text-[var(--muted-foreground)] focus:border-[var(--primary)] focus:shadow-[0_0_0_4px_var(--primary-soft)]';
const card =
  'rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-[0_8px_28px_rgba(24,52,58,0.04)] sm:p-6';
const primaryBtn =
  'rounded-xl bg-[var(--primary)] px-4 py-2.5 text-sm font-semibold text-white transition hover:opacity-90 active:scale-[0.98] disabled:opacity-60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2';
const ghostBtn =
  'rounded-xl border border-[var(--border)] px-4 py-2.5 text-sm font-semibold text-[var(--foreground)] transition hover:border-[var(--primary)] active:scale-[0.98] disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]';

export default function BuildArtifacts({ projectId }: { projectId: string }) {
  const { getProject, getArtifacts, getEvidence, loading, hydrated, error, busy, addArtifact, addArtifactVersion, addEvidence, refreshProjectData } = useBuild(projectId);
  const project = getProject(projectId); const artifacts = getArtifacts(projectId); const evidence = getEvidence(projectId);
  const [title, setTitle] = useState(''); const [description, setDescription] = useState(''); const [type, setType] = useState<ArtifactType>('DELIVERABLE');
  const [versionArtifactId, setVersionArtifactId] = useState(''); const [fileName, setFileName] = useState(''); const [fileSize, setFileSize] = useState('');
  const [evidenceTitle, setEvidenceTitle] = useState(''); const [evidenceDescription, setEvidenceDescription] = useState(''); const [errorText, setErrorText] = useState(''); const [success, setSuccess] = useState('');

  async function createArtifact(event: FormEvent) { event.preventDefault(); setErrorText(''); setSuccess(''); try { await addArtifact({ projectId, title, description, type }); setTitle(''); setDescription(''); setSuccess('Artifact record created.'); } catch (e) { setErrorText(e instanceof Error ? e.message : 'Could not create artifact.'); } }
  async function createVersion(event: FormEvent) { event.preventDefault(); setErrorText(''); setSuccess(''); if (!versionArtifactId) { setErrorText('Choose an artifact first.'); return; } try { await addArtifactVersion(versionArtifactId, { fileName: fileName || undefined, fileSize: fileSize ? Number(fileSize) : undefined }); setFileName(''); setFileSize(''); setSuccess('Artifact version metadata saved. No file binary was uploaded by this request.'); } catch (e) { setErrorText(e instanceof Error ? e.message : 'Could not add version.'); } }
  async function createEvidence(event: FormEvent) { event.preventDefault(); setErrorText(''); setSuccess(''); try { await addEvidence({ projectId, title: evidenceTitle, description: evidenceDescription, skills: project?.skills ?? [] }); setEvidenceTitle(''); setEvidenceDescription(''); setSuccess('Evidence record created.'); } catch (e) { setErrorText(e instanceof Error ? e.message : 'Could not add evidence.'); } }

  if (loading && !hydrated) return <BuildLoading label="Loading project artifacts…" />;

  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-10 lg:px-8">
      <Link href={`/build/${projectId}`} className="group inline-flex items-center gap-1 rounded-md py-1 text-sm font-medium text-[var(--primary)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)]">
        <Chevron className="rotate-180 transition-transform duration-200 group-hover:-translate-x-0.5" />
        Back to workspace
      </Link>

      <header className="rise mt-5">
        <p className="text-sm text-[var(--muted-foreground)]">Project outputs</p>
        <h1 className="mt-1 text-[28px] font-semibold leading-tight tracking-tight text-[var(--foreground)] sm:text-3xl">Artifacts & evidence</h1>
        <p className="mt-2 max-w-2xl text-[15px] leading-6 text-[var(--muted-foreground)]">
          Keep a structured record of deliverables, document versions, and evidence linked to the skills practiced in this project.
        </p>
      </header>

      {error && <div className="mt-6"><BuildError message={error} onRetry={() => void refreshProjectData(projectId)} /></div>}

      {(errorText || success) && (
        <p
          key={errorText || success}
          role={errorText ? 'alert' : 'status'}
          className={`rise mt-5 flex items-start gap-2.5 rounded-2xl border p-3.5 text-sm ${
            errorText ? 'border-red-500/30 bg-red-500/5 text-red-500' : 'border-[var(--border)] bg-[var(--surface)] text-[var(--muted-foreground)]'
          }`}
        >
          <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${errorText ? 'bg-red-500' : 'bg-[var(--primary)]'}`} />
          {errorText || success}
        </p>
      )}

      <div className="mt-7 grid gap-6 lg:grid-cols-2 lg:items-start">
        {/* Artifacts */}
        <section className={`rise ${card}`} style={stagger(1)}>
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold text-[var(--foreground)]">Artifacts</h2>
            <span className="rounded-full border border-[var(--border)] px-2.5 py-1 text-xs font-medium text-[var(--muted-foreground)]">{artifacts.length}</span>
          </div>

          {artifacts.length ? (
            <div className="mt-4 space-y-3">
              {artifacts.map((artifact, i) => (
                <article key={artifact.id} className="rise rounded-2xl border border-[var(--border)] p-4" style={stagger(Math.min(i, 8))}>
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <h3 className="font-semibold leading-snug text-[var(--foreground)]">{artifact.title}</h3>
                      <p className="mt-1 text-xs text-[var(--muted-foreground)]">{artifact.type.toLowerCase()} · {artifact.versions?.length ?? 0} version(s)</p>
                    </div>
                    <span className="shrink-0 rounded-lg bg-[var(--background)] px-2 py-1 text-xs text-[var(--muted-foreground)]">
                      {new Date(artifact.updatedAt || artifact.createdAt).toLocaleDateString()}
                    </span>
                  </div>

                  {artifact.description && <p className="mt-2 text-sm leading-6 text-[var(--muted-foreground)]">{artifact.description}</p>}

                  {artifact.versions?.length ? (
                    <ol className="mt-3 space-y-1.5 border-t border-[var(--border)] pt-3">
                      {artifact.versions.map((version) => (
                        <li key={version.id} className="flex items-center gap-2.5 text-xs text-[var(--muted-foreground)]">
                          <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--primary)]" />
                          <span className="min-w-0 break-words">
                            v{version.version}
                            {version.fileName ? ` · ${version.fileName}` : ''}
                            {typeof version.fileSize === 'number' ? ` · ${Math.round(version.fileSize / 1024)} KB` : ''}
                          </span>
                        </li>
                      ))}
                    </ol>
                  ) : null}
                </article>
              ))}
            </div>
          ) : (
            <div className="mt-4">
              <BuildEmpty title="No artifacts yet" description="Create a record for a report, presentation, deliverable, or other project output." />
            </div>
          )}

          <form onSubmit={createArtifact} className="mt-6 space-y-3 border-t border-[var(--border)] pt-5">
            <h3 className="text-sm font-semibold text-[var(--foreground)]">Add artifact record</h3>
            <input required value={title} onChange={(e) => setTitle(e.target.value)} className={inputClass} placeholder="Title" />
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} className={inputClass} rows={2} placeholder="Description (optional)" />
            <div className="flex flex-col gap-2 sm:flex-row">
              <select value={type} onChange={(e) => setType(e.target.value as ArtifactType)} className={inputClass}>
                {(['DOCUMENT', 'UPLOAD', 'DELIVERABLE', 'PRESENTATION', 'EVIDENCE'] as ArtifactType[]).map((value) => <option key={value} value={value}>{value.toLowerCase()}</option>)}
              </select>
              <button disabled={busy === 'add-artifact'} className={`${primaryBtn} shrink-0`}>
                {busy === 'add-artifact' ? 'Adding…' : 'Add record'}
              </button>
            </div>
          </form>
        </section>

        <section className="space-y-6">
          {/* Version */}
          <div className={`rise ${card}`} style={stagger(2)}>
            <h2 className="text-lg font-semibold text-[var(--foreground)]">Record a version</h2>
            <p className="mt-1 text-sm leading-6 text-[var(--muted-foreground)]">
              The supplied backend exposes version metadata, not a binary upload endpoint. Add a filename and optional size for a version that has already been stored by a supported workflow.
            </p>

            <form onSubmit={createVersion} className="mt-5 space-y-4">
              <label className="block text-sm font-medium text-[var(--foreground)]">
                Artifact
                <select required value={versionArtifactId} onChange={(e) => setVersionArtifactId(e.target.value)} className={`${inputClass} mt-1.5`}>
                  <option value="">Select artifact</option>
                  {artifacts.map((artifact) => <option key={artifact.id} value={artifact.id}>{artifact.title}</option>)}
                </select>
              </label>
              <label className="block text-sm font-medium text-[var(--foreground)]">
                File name
                <input value={fileName} onChange={(e) => setFileName(e.target.value)} className={`${inputClass} mt-1.5`} placeholder="research-notes.pdf" />
              </label>
              <label className="block text-sm font-medium text-[var(--foreground)]">
                File size in bytes
                <input type="number" min="0" value={fileSize} onChange={(e) => setFileSize(e.target.value)} className={`${inputClass} mt-1.5`} placeholder="Optional" />
              </label>
              <button disabled={!artifacts.length || busy === 'add-artifact-version'} className={`${ghostBtn} w-full sm:w-auto`}>
                {busy === 'add-artifact-version' ? 'Saving…' : 'Save version metadata'}
              </button>
            </form>
          </div>

          {/* Evidence */}
          <div className={`rise ${card}`} style={stagger(3)}>
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-semibold text-[var(--foreground)]">Evidence of learning</h2>
              <span className="rounded-full border border-[var(--border)] px-2.5 py-1 text-xs font-medium text-[var(--muted-foreground)]">{evidence.length}</span>
            </div>

            {evidence.length ? (
              <div className="mt-4 space-y-2">
                {evidence.map((item, i) => (
                  <article key={item.id} className="rise rounded-2xl bg-[var(--background)] p-3.5" style={stagger(Math.min(i, 8))}>
                    <h3 className="text-sm font-semibold text-[var(--foreground)]">{item.title}</h3>
                    {item.description && <p className="mt-1 text-sm leading-6 text-[var(--muted-foreground)]">{item.description}</p>}
                    {item.skills.length > 0 && (
                      <div className="mt-2.5 flex flex-wrap gap-1.5">
                        {item.skills.map((skill) => (
                          <span key={skill} className="rounded-lg bg-[var(--surface)] px-2 py-1 text-xs text-[var(--muted-foreground)]">{skill}</span>
                        ))}
                      </div>
                    )}
                  </article>
                ))}
              </div>
            ) : (
              <p className="mt-3 text-sm text-[var(--muted-foreground)]">No evidence has been recorded yet.</p>
            )}

            <form onSubmit={createEvidence} className="mt-5 space-y-3 border-t border-[var(--border)] pt-5">
              <input required value={evidenceTitle} onChange={(e) => setEvidenceTitle(e.target.value)} className={inputClass} placeholder="Evidence title" />
              <textarea value={evidenceDescription} onChange={(e) => setEvidenceDescription(e.target.value)} className={inputClass} rows={2} placeholder="What does this demonstrate?" />
              <button className={`${primaryBtn} w-full sm:w-auto`}>Add evidence</button>
            </form>
          </div>
        </section>
      </div>
    </main>
  );
}