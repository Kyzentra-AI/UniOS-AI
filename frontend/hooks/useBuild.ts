'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { buildServices } from '@/services/buildServices';
import type {
  Artifact, BuildCoachRequest, BuildCoachResponse, BuildState, CreateArtifactInput,
  CreateArtifactVersionInput, CreateEvidenceInput, CreateMilestoneInput, CreateProjectInput,
  CreateTaskInput, Evidence, Milestone, Project, RecommendedProject, Task,
  UpdateMilestoneInput, UpdateProjectInput, UpdateTaskInput,
} from '@/types/build';

const EMPTY_STATE: BuildState = { projects: [], milestones: [], tasks: [], artifacts: [], evidence: [] };

export function useBuild(projectId?: string) {
  const [state, setState] = useState<BuildState>(EMPTY_STATE);
  const [recommendations, setRecommendations] = useState<RecommendedProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [hydrated, setHydrated] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const requestId = useRef(0);

  const load = useCallback(async (id?: string) => {
    const current = ++requestId.current;
    setLoading(true); setError(null);
    try {
      const projects = await buildServices.listProjects();
      let next: BuildState = { ...EMPTY_STATE, projects };
      if (id) {
        const [project, milestones, tasks, artifacts, evidence] = await Promise.all([
          buildServices.getProject(id), buildServices.getMilestones(id), buildServices.getTasks(id),
          buildServices.getArtifacts(id), buildServices.getEvidence(id),
        ]);
        next = {
          projects: projects.some((item) => item.id === project.id) ? projects.map((item) => item.id === project.id ? project : item) : [project, ...projects],
          milestones, tasks, artifacts, evidence,
        };
      }
      if (current === requestId.current) setState(next);
      if (!id) {
        try { setRecommendations(await buildServices.getRecommendations()); }
        catch { setRecommendations([]); }
      }
    } catch (cause) {
      if (current === requestId.current) setError(cause instanceof Error ? cause.message : 'Unable to load Build data.');
    } finally {
      if (current === requestId.current) { setLoading(false); setHydrated(true); }
    }
  }, []);

  useEffect(() => { void load(projectId); return () => { requestId.current += 1; }; }, [load, projectId]);

  const refresh = useCallback(async () => { await load(projectId); }, [load, projectId]);
  const run = useCallback(async <T,>(key: string, action: () => Promise<T>): Promise<T> => {
    setBusy(key); setError(null);
    try { return await action(); }
    catch (cause) {
      const message = cause instanceof Error ? cause.message : 'The request failed.';
      setError(message); throw cause;
    } finally { setBusy(null); }
  }, []);

  const refreshProjectData = useCallback(async (id = projectId) => {
    if (!id) { await load(); return; }
    const [project, milestones, tasks, artifacts, evidence] = await Promise.all([
      buildServices.getProject(id), buildServices.getMilestones(id), buildServices.getTasks(id),
      buildServices.getArtifacts(id), buildServices.getEvidence(id),
    ]);
    setState((previous) => ({
      ...previous,
      projects: previous.projects.some((item) => item.id === project.id) ? previous.projects.map((item) => item.id === project.id ? project : item) : [project, ...previous.projects],
      milestones, tasks, artifacts, evidence,
    }));
    return project;
  }, [load, projectId]);

  const createProject = useCallback((input: CreateProjectInput) => run('create-project', async () => {
    const project = await buildServices.createProject(input);
    setState((previous) => ({ ...previous, projects: [project, ...previous.projects.filter((item) => item.id !== project.id)] }));
    return project;
  }), [run]);
  const updateProject = useCallback((id: string, input: UpdateProjectInput) => run('update-project', async () => {
    const project = await buildServices.updateProject(id, input);
    setState((previous) => ({ ...previous, projects: previous.projects.map((item) => item.id === id ? project : item) }));
    return project;
  }), [run]);
  const generatePlan = useCallback((id: string) => run('generate-plan', async () => {
    const result = await buildServices.generatePlan(id);
    await refreshProjectData(id);
    return result;
  }), [refreshProjectData, run]);
  const addMilestone = useCallback((input: CreateMilestoneInput) => run('add-milestone', async () => {
    const created = await buildServices.createMilestone(input);
    setState((previous) => ({ ...previous, milestones: [...previous.milestones.filter((item) => item.id !== created.id), created] }));
    return created;
  }), [run]);
  const updateMilestone = useCallback((id: string, input: UpdateMilestoneInput) => run('update-milestone', async () => {
    const updated = await buildServices.updateMilestone(id, input);
    setState((previous) => ({ ...previous, milestones: previous.milestones.map((item) => item.id === id ? updated : item) }));
    return updated;
  }), [run]);
  const toggleMilestone = useCallback((milestone: Milestone) => updateMilestone(milestone.id, { status: milestone.status === 'COMPLETED' ? 'PENDING' : 'COMPLETED' }), [updateMilestone]);
  const addTask = useCallback((input: CreateTaskInput) => run('add-task', async () => {
    const created = await buildServices.createTask(input);
    setState((previous) => ({ ...previous, tasks: [...previous.tasks.filter((item) => item.id !== created.id), created] }));
    return created;
  }), [run]);
  const updateTask = useCallback((id: string, input: UpdateTaskInput) => run('update-task', async () => {
    const updated = await buildServices.updateTask(id, input);
    setState((previous) => ({ ...previous, tasks: previous.tasks.map((item) => item.id === id ? updated : item) }));
    return updated;
  }), [run]);
  const addArtifact = useCallback((input: CreateArtifactInput) => run('add-artifact', async () => {
    const created = await buildServices.createArtifact(input);
    setState((previous) => ({ ...previous, artifacts: [...previous.artifacts.filter((item) => item.id !== created.id), created] }));
    return created;
  }), [run]);
  const addArtifactVersion = useCallback((artifactId: string, input: CreateArtifactVersionInput) => run('add-artifact-version', async () => {
    const version = await buildServices.createArtifactVersion(artifactId, input);
    setState((previous) => ({ ...previous, artifacts: previous.artifacts.map((artifact) => artifact.id === artifactId ? { ...artifact, versions: [...(artifact.versions ?? []).filter((item) => item.id !== version.id), version] } : artifact) }));
    return version;
  }), [run]);
  const addEvidence = useCallback((input: CreateEvidenceInput) => run('add-evidence', async () => {
    const created = await buildServices.createEvidence(input);
    setState((previous) => ({ ...previous, evidence: [...previous.evidence.filter((item) => item.id !== created.id), created] }));
    return created;
  }), [run]);
  const askCoach = useCallback((id: string, input: BuildCoachRequest): Promise<BuildCoachResponse> => run('coach', () => buildServices.askCoach(id, input)), [run]);
  const completeProject = useCallback((id: string) => run('complete-project', async () => {
    const completed = await buildServices.completeProject(id);
    setState((previous) => ({ ...previous, projects: previous.projects.map((item) => item.id === id ? completed : item) }));
    return completed;
  }), [run]);

  const getProject = useCallback((id: string) => state.projects.find((item) => item.id === id), [state.projects]);
  const getMilestones = useCallback((id: string) => state.milestones.filter((item) => item.projectId === id).sort((a, b) => a.orderIdx - b.orderIdx), [state.milestones]);
  const getTasks = useCallback((id: string) => state.tasks.filter((item) => item.projectId === id).sort((a, b) => a.orderIdx - b.orderIdx), [state.tasks]);
  const getArtifacts = useCallback((id: string) => state.artifacts.filter((item) => item.projectId === id).sort((a, b) => b.createdAt.localeCompare(a.createdAt)), [state.artifacts]);
  const getEvidence = useCallback((id: string) => state.evidence.filter((item) => item.projectId === id).sort((a, b) => b.createdAt.localeCompare(a.createdAt)), [state.evidence]);
  const progress = useMemo(() => {
    const tasks = projectId ? state.tasks.filter((task) => task.projectId === projectId) : state.tasks;
    return tasks.length ? Math.round((tasks.filter((task) => task.status === 'COMPLETED').length / tasks.length) * 100) : 0;
  }, [projectId, state.tasks]);

  return {
    ...state, recommendations, loading, hydrated, error, busy, refresh, refreshProjects: refresh,
    refreshProjectData, createProject, updateProject, generatePlan, addMilestone, updateMilestone,
    toggleMilestone, addTask, updateTask, addArtifact, addArtifactVersion, addEvidence,
    askCoach, completeProject, getProject, getMilestones, getTasks, getArtifacts, getEvidence, progress,
  };
}
