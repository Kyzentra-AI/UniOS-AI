
'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import LearningWorkspace from '@/components/learning/LearningWorkspace';

function LearningPageContent() {
  const searchParams = useSearchParams();

  const topic = searchParams?.get('topic') ?? '';
  const lessonId = searchParams?.get('lesson_id') ?? '';
  const roadmapId = searchParams?.get('roadmap_id') ?? undefined;
  const missionId = searchParams?.get('mission_id') ?? undefined;

  if (!topic.trim() || !lessonId.trim()) {
    return (
      <main className="flex min-h-screen items-center justify-center p-6">
        <div className="max-w-md text-center">
          <h1 className="text-xl font-semibold">
            Learning details missing
          </h1>

          <p className="mt-2 text-sm text-gray-500">
            Please open this page from a valid learning lesson.
            The topic or lesson ID is missing from the URL.
          </p>
        </div>
      </main>
    );
  }

  return (
    <LearningWorkspace
      topic={topic}
      lessonId={lessonId}
      roadmapId={roadmapId}
      missionId={missionId}
    />
    
  );
}

export default function LearningPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center p-6">
          <p className="text-sm text-gray-500">
            Loading learning workspace...
          </p>
        </main>
      }
    >
      <LearningPageContent />
    </Suspense>
  );
}