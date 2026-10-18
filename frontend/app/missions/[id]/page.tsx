'use client';

import { use } from 'react';
import { useRouter } from 'next/navigation';

import MissionCard from '@/components/roadmap/MissionCard';
import { useMission } from '@/hooks/useMission';

interface MissionsPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default function MissionsPage({
  params,
}: MissionsPageProps) {
  const { id } = use(params);
  const router = useRouter();

  const {
    mission,
    isLoading,
    error,
    startMission,
    completeMission,
    deferMission,
    skipMission,
    isStarting,
    isCompleting,
    isDeferring,
    isSkipping,
  } = useMission(id);

  const handleStart = async () => {
    if (!mission) return;

    try {
      await startMission(mission.id);

      const searchParams = new URLSearchParams({
        topic: mission.subject || mission.title,
        lesson_id: mission.id,
        mission_id: mission.id,
      });

      if (mission.roadmap_id) {
        searchParams.set('roadmap_id', mission.roadmap_id);
      }

      router.push(`/learning?${searchParams.toString()}`);
    } catch (error) {
      console.error('Failed to start mission:', error);
    }
  };

  if (isLoading) {
    return (
      <main className="min-h-screen px-6 py-8">
        <div className="mx-auto max-w-3xl">
          <p
            className="text-sm"
            style={{ color: 'var(--text-secondary)' }}
          >
            Loading mission...
          </p>
        </div>
      </main>
    );
  }

  if (error || !mission) {
    return (
      <main className="min-h-screen px-6 py-8">
        <div className="mx-auto max-w-3xl">
          <p
            className="text-sm"
            style={{ color: 'var(--danger)' }}
          >
            Failed to load mission.
          </p>

          {error && (
            <p
              className="mt-2 text-sm"
              style={{ color: 'var(--text-secondary)' }}
            >
              {error instanceof Error
                ? error.message
                : 'An unexpected error occurred.'}
            </p>
          )}

          <button
            type="button"
            onClick={() => router.push('/roadmap')}
            className="mt-4 rounded-lg border px-4 py-2 text-sm"
            style={{
              borderColor: 'var(--border)',
              color: 'var(--text-primary)',
            }}
          >
            Back to roadmap
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto max-w-3xl">
        <MissionCard
          mission={mission}
          onStart={handleStart}
          onComplete={() => completeMission(mission.id)}
          onDefer={() => deferMission(mission.id)}
          onSkip={() => skipMission(mission.id)}
          isStarting={isStarting}
          isCompleting={isCompleting}
          isDeferring={isDeferring}
          isSkipping={isSkipping}
        />
      </div>
    </main>
  );
}