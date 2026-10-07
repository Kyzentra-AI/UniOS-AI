'use client';

import MissionCard from '@/components/roadmap/MissionCard';
import { useMission } from '@/hooks/useMission';

interface MissionsPageProps {
  params: {
    id: string;
  };
}

export default function MissionsPage({
  params,
}: MissionsPageProps) {
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
  } = useMission(params.id);

  if (isLoading) {
    return (
      <main className="min-h-screen px-6 py-8">
        <div className="mx-auto max-w-3xl">
          <p
            className="text-sm"
            style={{
              color: 'var(--text-secondary)',
            }}
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
            style={{
              color: 'var(--danger)',
            }}
          >
            Failed to load mission.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto max-w-3xl">
        <MissionCard
          mission={mission}
          onStart={() => startMission(mission.id)}
          onComplete={() =>
            completeMission(mission.id)
          }
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
