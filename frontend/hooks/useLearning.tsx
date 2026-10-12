
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

  if (!data) return null;

  // Accept the direct lesson shape only when the response
  // actually contains the required Lesson fields.
  if (
    typeof data.id === 'string' &&
    typeof data.title === 'string' &&
    typeof data.objective === 'string' &&
    Array.isArray(data.blocks)
  ) {
    return data as unknown as Lesson;
  }

  return null;
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

      const existingLesson = getLessonFromSession(created);

      if (existingLesson) {
        setLesson(existingLesson);
      } else {
        const generated = await generateLesson(created.id, {
          topic: created.topic,
          lesson_id: created.lesson_id,
        });

        setLesson(generated);
      }

      const latest = await getLearningSession(created.id);
      setSessionData(latest);

      if (latest.checkpoint_block_id) {
        const currentLesson =
          getLessonFromSession(latest) ?? existingLesson;

        const index = currentLesson?.blocks.findIndex(
          (block) => block.id === latest.checkpoint_block_id,
        );

        if (index !== undefined && index >= 0) {
          setCurrentBlockIndex(index);
        }
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

    return Math.round(
      (completedBlockIds.length / lesson.blocks.length) * 100,
    );
  }, [completedBlockIds, lesson]);

  const currentBlock = lesson?.blocks[currentBlockIndex] ?? null;

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
          progress_percentage: progress,
          status: progress >= 100 ? 'COMPLETED' : 'IN_PROGRESS',
        },
      );

      setSessionData(updated);
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
  }, [sessionData, lesson, currentBlockIndex, progress]);

  const refreshSession = useCallback(async () => {
    if (!sessionData) return;

    const latest = await getLearningSession(sessionData.id);
    setSessionData(latest);

    const updatedLesson = getLessonFromSession(latest);

    if (updatedLesson) {
      setLesson(updatedLesson);
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