
'use client';

import { useOnboardingStore } from '@/stores/onboardingstore';

export default function OnboardingDebugPage() {
  const state = useOnboardingStore();

  return (
    <main className="min-h-screen bg-white p-6 text-black">
      <h1 className="mb-4 text-xl font-bold">
        Onboarding Store Debug
      </h1>

      <pre className="whitespace-pre-wrap break-words rounded-lg bg-gray-100 p-4 text-sm">
        {JSON.stringify(
          {
            currentStep: state.currentStep,
            education: state.education,
            careerGoals: state.careerGoals,
            skills: state.skills,
            preferences: state.preferences,
          },
          null,
          2
        )}
      </pre>
    </main>
  );
}
