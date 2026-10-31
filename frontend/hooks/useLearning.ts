
'use client';

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react';

import type {
  LearningSession,
  LearningSessionCreate,
  Lesson,
} from '@/types/learning';

import {
  createLearningSession,
  generateLesson,
  getLearningSession,
  saveLearningCheckpoint,
  saveLearningCheckpointOnExit,
} from '@/services/learningServices';

interface UseLearningOptions {
  session: LearningSessionCreate;
}

interface UseLearningResult {
  sessionData: LearningSession | null;
  lesson: Lesson | null;
  currentBlockIndex: number;
  completedBlockIds: string[];
  progress: number;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  currentBlock: Lesson['blocks'][number] | null;
  goToBlock: (index: number) => void;
  nextBlock: () => void;
  previousBlock: () => void;
  markBlockComplete: (blockId: string) => Promise<void>;
  isBlockCompleted: (blockId: string) => boolean;
  syncCheckpoint: () => Promise<void>;
  pauseSession: () => Promise<void>;
  pauseSessionOnExit: () => void;
  refreshSession: () => Promise<void>;
}

function getLessonFromSession(
  session: LearningSession,
): Lesson | null {
  const data = session.lesson_data;

  if (
    !data ||
    typeof data.id !== 'string' ||
    typeof data.title !== 'string' ||
    typeof data.objective !== 'string' ||
    !Array.isArray(data.blocks)
  ) {
    return null;
  }

  return data as unknown as Lesson;
}

/**
 * Resolve the section to display.
 *
 * Priority:
 * 1. Valid, incomplete saved checkpoint.
 * 2. First incomplete section.
 * 3. First section if the lesson is fully completed.
 */
function getResumeBlockIndex(
  lesson: Lesson,
  completedIds: string[],
  checkpointBlockId?: string | null,
): number {
  const checkpointIndex = lesson.blocks.findIndex(
    (block) => block.id === checkpointBlockId,
  );

  if (
    checkpointIndex >= 0 &&
    !completedIds.includes(lesson.blocks[checkpointIndex].id)
  ) {
    return checkpointIndex;
  }

  const firstIncompleteIndex = lesson.blocks.findIndex(
    (block) => !completedIds.includes(block.id),
  );

  return firstIncompleteIndex >= 0 ? firstIncompleteIndex : 0;
}

export function useLearning({
  session,
}: UseLearningOptions): UseLearningResult {
  const [sessionData, setSessionData] =
    useState<LearningSession | null>(null);

  const [lesson, setLesson] = useState<Lesson | null>(null);

  const [currentBlockIndex, setCurrentBlockIndex] = useState(0);

  const [completedBlockIds, setCompletedBlockIds] =
    useState<string[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSession = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const created = await createLearningSession(session);

      setSessionData(created);

      let loadedLesson = getLessonFromSession(created);

      if (!loadedLesson) {
        loadedLesson = await generateLesson(created.id, {
          topic: created.topic,
          lesson_id: created.lesson_id,
        });
      }

      setLesson(loadedLesson);

      const latest = await getLearningSession(created.id);

      setSessionData(latest);

      const validBlockIds = new Set(
        loadedLesson.blocks.map((block) => block.id),
      );

      const savedCompletedIds = (
        latest.completed_block_ids ?? []
      ).filter((id) => validBlockIds.has(id));

      setCompletedBlockIds(savedCompletedIds);

      const resumeIndex = getResumeBlockIndex(
        loadedLesson,
        savedCompletedIds,
        latest.checkpoint_block_id,
      );

      setCurrentBlockIndex(resumeIndex);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load the learning session.',
      );
    } finally {
      setIsLoading(false);
    }
  }, [session]);

  useEffect(() => {
    void loadSession();
  }, [loadSession]);

  const progress = useMemo(() => {
    if (!lesson?.blocks.length) return 0;

    const completedCount = lesson.blocks.filter((block) =>
      completedBlockIds.includes(block.id),
    ).length;

    return Math.round(
      (completedCount / lesson.blocks.length) * 100,
    );
  }, [completedBlockIds, lesson]);

  const currentBlock =
    lesson?.blocks[currentBlockIndex] ?? null;

  const goToBlock = useCallback(
    (index: number) => {
      if (!lesson || index < 0 || index >= lesson.blocks.length) {
        return;
      }

      const firstIncomplete = lesson.blocks.findIndex(
        (block) => !completedBlockIds.includes(block.id),
      );

      const lastUnlockedIndex =
        firstIncomplete === -1
          ? lesson.blocks.length - 1
          : firstIncomplete;

      if (index <= lastUnlockedIndex) {
        setCurrentBlockIndex(index);
      }
    },
    [lesson, completedBlockIds],
  );

  const nextBlock = useCallback(() => {
    if (!lesson) return;

    const current = lesson.blocks[currentBlockIndex];

    if (!current || !completedBlockIds.includes(current.id)) {
      return;
    }

    setCurrentBlockIndex((index) =>
      Math.min(index + 1, lesson.blocks.length - 1),
    );
  }, [lesson, currentBlockIndex, completedBlockIds]);

  const previousBlock = useCallback(() => {
    setCurrentBlockIndex((index) => Math.max(index - 1, 0));
  }, []);

  const markBlockComplete = useCallback(
    async (blockId: string) => {
      if (!sessionData || !lesson || isSaving) {
        return;
      }

      const blockIndex = lesson.blocks.findIndex(
        (block) => block.id === blockId,
      );

      if (blockIndex < 0) {
        throw new Error('Lesson section not found.');
      }

      if (completedBlockIds.includes(blockId)) {
        return;
      }

      if (blockIndex !== currentBlockIndex) {
        throw new Error('Complete the current section first.');
      }

      const nextCompletedIds = [
        ...completedBlockIds,
        blockId,
      ];

      const nextProgress = Math.round(
        (nextCompletedIds.length / lesson.blocks.length) * 100,
      );

      const nextIndex = Math.min(
        blockIndex + 1,
        lesson.blocks.length - 1,
      );

      const nextBlockId = lesson.blocks[nextIndex]?.id;

      setIsSaving(true);
      setError(null);

      try {
        const updated = await saveLearningCheckpoint(
          sessionData.id,
          {
            checkpoint_block_id: nextBlockId,
            completed_block_ids: nextCompletedIds,
            progress_percentage: nextProgress,
            status:
              nextProgress >= 100 ? 'COMPLETED' : 'IN_PROGRESS',
          },
        );

        setSessionData(updated);

        const savedIds = (
          updated.completed_block_ids ?? nextCompletedIds
        ).filter((id) =>
          lesson.blocks.some((block) => block.id === id),
        );

        setCompletedBlockIds(savedIds);

        if (nextProgress < 100) {
          setCurrentBlockIndex(nextIndex);
        } else {
          setCurrentBlockIndex(blockIndex);
        }
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : 'Unable to save your progress. Please try again.';

        setError(message);
        throw err;
      } finally {
        setIsSaving(false);
      }
    },
    [
      sessionData,
      lesson,
      isSaving,
      completedBlockIds,
      currentBlockIndex,
    ],
  );

  const isBlockCompleted = useCallback(
    (blockId: string) => completedBlockIds.includes(blockId),
    [completedBlockIds],
  );

  // Save Progress: saves the checkpoint but keeps the session active.
  const syncCheckpoint = useCallback(async () => {
    if (!sessionData || !lesson) {
      throw new Error('Learning session or lesson is not loaded.');
    }

    setIsSaving(true);
    setError(null);

    try {
      const block = lesson.blocks[currentBlockIndex];

      const updated = await saveLearningCheckpoint(
        sessionData.id,
        {
          checkpoint_block_id: block?.id,
          completed_block_ids: completedBlockIds,
          progress_percentage: progress,
          status: progress >= 100 ? 'COMPLETED' : 'IN_PROGRESS',
        },
      );

      setSessionData(updated);

      if (updated.completed_block_ids) {
        setCompletedBlockIds(updated.completed_block_ids);
      }
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : 'Unable to save learning progress.';

      setError(message);
      throw err;
    } finally {
      setIsSaving(false);
    }
  }, [
    sessionData,
    lesson,
    currentBlockIndex,
    completedBlockIds,
    progress,
  ]);

  // Explicit Pause & Exit: wait for the backend to confirm the pause.
  const pauseSession = useCallback(async () => {
    if (!sessionData || !lesson) {
      throw new Error('Learning session or lesson is not loaded.');
    }

    setIsSaving(true);
    setError(null);

    try {
      const block = lesson.blocks[currentBlockIndex];

      const updated = await saveLearningCheckpoint(
        sessionData.id,
        {
          checkpoint_block_id: block?.id,
          completed_block_ids: completedBlockIds,
          progress_percentage: progress,
          status: progress >= 100 ? 'COMPLETED' : 'PAUSED',
        },
      );

      setSessionData(updated);

      if (updated.completed_block_ids) {
        setCompletedBlockIds(updated.completed_block_ids);
      }
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : 'Unable to pause your learning session.';

      setError(message);
      throw err;
    } finally {
      setIsSaving(false);
    }
  }, [
    sessionData,
    lesson,
    currentBlockIndex,
    completedBlockIds,
    progress,
  ]);

  // Browser Back / tab close: fire a keepalive request without waiting.
  const pauseSessionOnExit = useCallback(() => {
    if (!sessionData || !lesson) {
      return;
    }

    const block = lesson.blocks[currentBlockIndex];

    saveLearningCheckpointOnExit(
      sessionData.id,
      {
        checkpoint_block_id: block?.id,
        completed_block_ids: completedBlockIds,
        progress_percentage: progress,
        status: progress >= 100 ? 'COMPLETED' : 'PAUSED',
      },
    );
  }, [
    sessionData,
    lesson,
    currentBlockIndex,
    completedBlockIds,
    progress,
  ]);

  const refreshSession = useCallback(async () => {
    if (!sessionData) return;

    const latest = await getLearningSession(sessionData.id);

    setSessionData(latest);

    const updatedLesson = getLessonFromSession(latest);

    if (updatedLesson) {
      setLesson(updatedLesson);

      const validIds = new Set(
        updatedLesson.blocks.map((block) => block.id),
      );

      const savedIds = (
        latest.completed_block_ids ?? []
      ).filter((id) => validIds.has(id));

      setCompletedBlockIds(savedIds);

      const resumeIndex = getResumeBlockIndex(
        updatedLesson,
        savedIds,
        latest.checkpoint_block_id,
      );

      setCurrentBlockIndex(resumeIndex);
    }
  }, [sessionData]);

  return {
    sessionData,
    lesson,
    currentBlockIndex,
    completedBlockIds,
    progress,
    isLoading,
    isSaving,
    error,
    currentBlock,
    goToBlock,
    nextBlock,
    previousBlock,
    markBlockComplete,
    isBlockCompleted,
    syncCheckpoint,
    pauseSession,
    pauseSessionOnExit,
    refreshSession,
  };
}
