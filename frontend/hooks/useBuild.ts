
'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { buildServices } from '@/services/buildServices';

import type {
  BuildCoachRequest,
  BuildState,
  CreateArtifactInput,
  CreateArtifactVersionInput,
  CreateEvidenceInput,
  CreateMilestoneInput,
  CreateProjectInput,
  CreateTaskInput,
  Milestone,
  Project,
  RecommendedProject,
  Task,
  UpdateMilestoneInput,
  UpdateProjectInput,
  UpdateTaskInput,
} from '@/types/build';

const EMPTY_STATE: BuildState = {
  projects: [],
  milestones: [],
  tasks: [],
  artifacts: [],
  evidence: [],
};

function errorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : 'Something went wrong. Please try again.';
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function isArrayOf<T>(
  value: unknown,
  isItem: (item: unknown) => item is T,
): value is T[] {
  return Array.isArray(value) && value.every(isItem);
}

function isMilestone(value: unknown): value is Milestone {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.projectId === 'string' &&
    typeof value.title === 'string' &&
    typeof value.status === 'string'
  );
}

function isTask(value: unknown): value is Task {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.projectId === 'string' &&
    typeof value.title === 'string' &&
    typeof value.status === 'string'
  );
}

export function useBuild(projectId?: string) {
  const [state, setState] = useState<BuildState>(EMPTY_STATE);

  const [recommendations, setRecommendations] = useState<
    RecommendedProject[]
  >([]);

  const [hydrated, setHydrated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Track overlapping requests so one completed request cannot
  // hide the loader while another request is still running.
  const activeRequestsRef = useRef(0);

  const beginLoading = useCallback(() => {
    activeRequestsRef.current += 1;
    setLoading(true);
  }, []);

  const endLoading = useCallback(() => {
    activeRequestsRef.current = Math.max(
      0,
      activeRequestsRef.current - 1,
    );

    setLoading(activeRequestsRef.current > 0);
  }, []);

  
const refreshProjectData = useCallback(async (id: string) => {
  const [milestones, tasks, artifacts, evidence] = await Promise.all([
    buildServices.listMilestones(id),
    buildServices.listTasks(id),
    buildServices.listArtifacts(id),
    buildServices.listEvidence(id),
  ]);

  setState((previous) => ({
    ...previous,
    milestones: [
      ...previous.milestones.filter((item) => item.projectId !== id),
      ...milestones,
    ],
    tasks: [
      ...previous.tasks.filter((item) => item.projectId !== id),
      ...tasks,
    ],
    artifacts: [
      ...previous.artifacts.filter((item) => item.projectId !== id),
      ...artifacts,
    ],
    evidence: [
      ...previous.evidence.filter((item) => item.projectId !== id),
      ...evidence,
    ],
  }));
}, []);


  const refreshProjects = useCallback(async () => {
    beginLoading();
    setError(null);

    try {
      const projects = await buildServices.listProjects();

      setState((previous) => ({
        ...previous,
        projects,
      }));

      if (projectId) {
  await refreshProjectData(projectId);
}

      return projects;
    } catch (err) {
      setError(errorMessage(err));
      throw err;
    } finally {
      endLoading();
    }
  }, [beginLoading, endLoading]);

  const refresh = useCallback(async () => {
    beginLoading();
    setHydrated(false);
    setError(null);

    try {
      const projects = await buildServices.listProjects();

      let nextProjects = projects;

      if (projectId) {
        const project = await buildServices.getProject(projectId);

        nextProjects = [
          ...projects.filter((item) => item.id !== project.id),
          project,
        ];
      }

      setState((previous) => ({
        ...previous,
        projects: nextProjects,
      }));

      return nextProjects;
    } catch (err) {
      setError(errorMessage(err));
      throw err;
    } finally {
      setHydrated(true);
      endLoading();
    }
  }, [projectId, beginLoading, endLoading,refreshProjectData]);

  // Load projects when the hook mounts or projectId changes.
  useEffect(() => {
    let cancelled = false;

    async function load() {
      beginLoading();
      setHydrated(false);
      setError(null);

      try {
        const projects = await buildServices.listProjects();

        let nextProjects = projects;

        if (projectId) {
          const project = await buildServices.getProject(projectId);

          nextProjects = [
            ...projects.filter((item) => item.id !== project.id),
            project,
          ];
        }

        if (!cancelled) {
          setState((previous) => ({
            ...previous,
            projects: nextProjects,
          }));
        }
      } catch (err) {
        if (!cancelled) {
          setError(errorMessage(err));
        }
      } finally {
        endLoading();

        if (!cancelled) {
          setHydrated(true);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [projectId, beginLoading, endLoading]);

  // Recommendations are loaded on the Build hub.
  useEffect(() => {
    if (projectId) return;

    let cancelled = false;

    buildServices
      .getRecommendations()
      .then((items) => {
        if (!cancelled) {
          setRecommendations(items);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(errorMessage(err));
        }
      });

    return () => {
      cancelled = true;
    };
  }, [projectId]);

  const runMutation = useCallback(
    async <T,>(action: () => Promise<T>): Promise<T> => {
      beginLoading();
      setError(null);

      try {
        return await action();
      } catch (err) {
        setError(errorMessage(err));
        throw err;
      } finally {
        endLoading();
      }
    },
    [beginLoading, endLoading],
  );

  const createProject = useCallback(
    (input: CreateProjectInput) =>
      runMutation(async () => {
        const project = await buildServices.createProject(input);

        setState((previous) => ({
          ...previous,
          projects: [
            ...previous.projects.filter((item) => item.id !== project.id),
            project,
          ],
        }));

        return project;
      }),
    [runMutation],
  );

  const updateProject = useCallback(
    (id: string, input: UpdateProjectInput) =>
      runMutation(async () => {
        const project = await buildServices.updateProject(id, input);

        setState((previous) => ({
          ...previous,
          projects: previous.projects.map((item) =>
            item.id === project.id ? project : item,
          ),
        }));

        return project;
      }),
    [runMutation],
  );

  const generatePlan = useCallback(
    () =>
      runMutation(async () => {
        if (!projectId) {
          throw new Error('Project ID is required.');
        }

        const result = await buildServices.generatePlan(projectId);
        await refreshProjectData(projectId);

        if (isRecord(result)) {
          const milestones = result.milestones;
          const tasks = result.tasks;

          if (isArrayOf(milestones, isMilestone)) {
            setState((previous) => ({
              ...previous,
              milestones: [
                ...previous.milestones.filter(
                  (item) => item.projectId !== projectId,
                ),
                ...milestones,
              ],
            }));
          }

          if (isArrayOf(tasks, isTask)) {
            setState((previous) => ({
              ...previous,
              tasks: [
                ...previous.tasks.filter(
                  (item) => item.projectId !== projectId,
                ),
                ...tasks,
              ],
            }));
          }
        }

        return result;
      }),
    [projectId, runMutation, refreshProjectData],
  );

  const addMilestone = useCallback(
    (input: CreateMilestoneInput) =>
      runMutation(async () => {
        const milestone = await buildServices.createMilestone(input);

        setState((previous) => ({
          ...previous,
          milestones: [
            ...previous.milestones.filter(
              (item) => item.id !== milestone.id,
            ),
            milestone,
          ],
        }));

        return milestone;
      }),
    [runMutation],
  );

  const updateMilestone = useCallback(
    (id: string, input: UpdateMilestoneInput) =>
      runMutation(async () => {
        const milestone = await buildServices.updateMilestone(id, input);

        setState((previous) => ({
          ...previous,
          milestones: previous.milestones.map((item) =>
            item.id === milestone.id ? milestone : item,
          ),
        }));

        return milestone;
      }),
    [runMutation],
  );

  const toggleMilestone = useCallback(
    (id: string) =>
      runMutation(async () => {
        const existing = state.milestones.find((item) => item.id === id);

        if (!existing) {
          throw new Error(
            'Milestone is not loaded. Refresh the project data and try again.',
          );
        }

        const status =
          existing.status === 'COMPLETED' ? 'PENDING' : 'COMPLETED';

        const milestone = await buildServices.updateMilestone(id, { status });

        setState((previous) => ({
          ...previous,
          milestones: previous.milestones.map((item) =>
            item.id === milestone.id ? milestone : item,
          ),
        }));

        return milestone;
      }),
    [runMutation, state.milestones],
  );

  const addTask = useCallback(
    (input: CreateTaskInput) =>
      runMutation(async () => {
        const task = await buildServices.createTask(input);

        setState((previous) => ({
          ...previous,
          tasks: [
            ...previous.tasks.filter((item) => item.id !== task.id),
            task,
          ],
        }));

        return task;
      }),
    [runMutation],
  );

  const updateTask = useCallback(
    (id: string, input: UpdateTaskInput) =>
      runMutation(async () => {
        const task = await buildServices.updateTask(id, input);

        setState((previous) => ({
          ...previous,
          tasks: previous.tasks.map((item) =>
            item.id === task.id ? task : item,
          ),
        }));

        return task;
      }),
    [runMutation],
  );

  const addArtifact = useCallback(
    (input: CreateArtifactInput) =>
      runMutation(async () => {
        const artifact = await buildServices.createArtifact(input);

        setState((previous) => ({
          ...previous,
          artifacts: [
            ...previous.artifacts.filter(
              (item) => item.id !== artifact.id,
            ),
            artifact,
          ],
        }));

        return artifact;
      }),
    [runMutation],
  );

  const addArtifactVersion = useCallback(
    (artifactId: string, input: CreateArtifactVersionInput) =>
      runMutation(async () => {
        const version = await buildServices.createArtifactVersion(
          artifactId,
          input,
        );

        setState((previous) => ({
          ...previous,
          artifacts: previous.artifacts.map((artifact) =>
            artifact.id === artifactId
              ? {
                  ...artifact,
                  updatedAt: version.createdAt,
                  versions: [...(artifact.versions ?? []), version],
                }
              : artifact,
          ),
        }));

        return version;
      }),
    [runMutation],
  );

  const addEvidence = useCallback(
    (input: CreateEvidenceInput) =>
      runMutation(async () => {
        const evidence = await buildServices.createEvidence(input);

        setState((previous) => ({
          ...previous,
          evidence: [
            ...previous.evidence.filter(
              (item) => item.id !== evidence.id,
            ),
            evidence,
          ],
        }));

        return evidence;
      }),
    [runMutation],
  );

  const askCoach = useCallback(
    (input: BuildCoachRequest) =>
      runMutation(async () => {
        if (!projectId) {
          throw new Error('Project ID is required.');
        }

        return buildServices.askCoach(projectId, input);
      }),
    [projectId, runMutation],
  );

  const completeProject = useCallback(
    (id: string) =>
      runMutation(async () => {
        const project = await buildServices.completeProject(id);

        setState((previous) => ({
          ...previous,
          projects: previous.projects.map((item) =>
            item.id === project.id ? project : item,
          ),
        }));

        return project;
      }),
    [runMutation],
  );

  const getProject = useCallback(
    (id: string) => state.projects.find((item) => item.id === id),
    [state.projects],
  );

  const getMilestones = useCallback(
    (id: string) =>
      state.milestones
        .filter((item) => item.projectId === id)
        .sort((a, b) => a.orderIdx - b.orderIdx),
    [state.milestones],
  );

  const getTasks = useCallback(
    (id: string) =>
      state.tasks
        .filter((item) => item.projectId === id)
        .sort((a, b) => a.orderIdx - b.orderIdx),
    [state.tasks],
  );

  const getArtifacts = useCallback(
    (id: string) =>
      state.artifacts.filter((item) => item.projectId === id),
    [state.artifacts],
  );

  const getEvidence = useCallback(
    (id: string) =>
      state.evidence.filter((item) => item.projectId === id),
    [state.evidence],
  );

  const projects = useMemo(
    () =>
      state.projects.map((project) => {
        const projectTasks = state.tasks.filter(
          (task) => task.projectId === project.id,
        );

        const completed = projectTasks.filter(
          (task) => task.status === 'COMPLETED',
        ).length;

        return {
          ...project,
          progress: projectTasks.length
            ? Math.round((completed / projectTasks.length) * 100)
            : 0,
        };
      }),
    [state.projects, state.tasks],
  );

  return {
    hydrated,
    loading,
    error,
    recommendations,
    projects,

    milestones: state.milestones,
    tasks: state.tasks,
    artifacts: state.artifacts,
    evidence: state.evidence,

    refresh,
    refreshProjects,

    createProject,
    updateProject,

    generatePlan,

    addMilestone,
    updateMilestone,
    toggleMilestone,

    addTask,
    updateTask,

    addArtifact,
    addArtifactVersion,
    addEvidence,

    askCoach,
    completeProject,

    getProject,
    getMilestones,
    getTasks,
    getArtifacts,
    getEvidence,
  };
}
