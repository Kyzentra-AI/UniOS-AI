
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
  markBlockComplete: (blockId: string) => void;
  isBlockCompleted: (blockId: string) => boolean;
  syncCheckpoint: () => Promise<void>;
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

      const checkpointIndex = loadedLesson.blocks.findIndex(
        (block) => block.id === latest.checkpoint_block_id,
      );

      if (checkpointIndex >= 0) {
        setCurrentBlockIndex(checkpointIndex);
      } else {
        setCurrentBlockIndex(0);
      }
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

    const validBlockIds = new Set(
      lesson.blocks.map((block) => block.id),
    );

    const completedCount = completedBlockIds.filter(
      (id) => validBlockIds.has(id),
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

      setCurrentBlockIndex(index);
    },
    [lesson],
  );

  const nextBlock = useCallback(() => {
    setCurrentBlockIndex((index) =>
      Math.min(index + 1, (lesson?.blocks.length ?? 1) - 1),
    );
  }, [lesson]);

  const previousBlock = useCallback(() => {
    setCurrentBlockIndex((index) => Math.max(0, index - 1));
  }, []);

  const markBlockComplete = useCallback((blockId: string) => {
    setCompletedBlockIds((previous) =>
      previous.includes(blockId)
        ? previous
        : [...previous, blockId],
    );
  }, []);

  const isBlockCompleted = useCallback(
    (blockId: string) => completedBlockIds.includes(blockId),
    [completedBlockIds],
  );

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

      setCompletedBlockIds(
        (latest.completed_block_ids ?? []).filter(
          (id) => validIds.has(id),
        ),
      );

      const index = updatedLesson.blocks.findIndex(
        (block) => block.id === latest.checkpoint_block_id,
      );

      if (index >= 0) {
        setCurrentBlockIndex(index);
      }
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
    refreshSession,
  };
}
