'use client';

import { useEffect } from 'react';

import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import { useOnboardingStore } from '@/stores/onboardingstore';

import {
  completeOnboarding,
  getKIEQuestions,
  getOnboardingState,
  initializeOnboarding,
  submitKIEAnswers,
  updateOnboarding,
} from '@/services/onboardingServices';

import type {
  OnboardingAnswersPayload,
  OnboardingPayload,
} from '@/types/onboarding';

export function useOnboarding() {
  const queryClient = useQueryClient();

  const hydrateFromBackend =
  useOnboardingStore(
    (state) => state.hydrateFromBackend
  );

  const onboardingQuery = useQuery({
    queryKey: ['onboarding'],
    queryFn: getOnboardingState,
    retry: false,

    
  });
  useEffect(() => {
  const data = onboardingQuery.data;

  if (!data?.raw_data) {
    return;
  }

  hydrateFromBackend(data.raw_data);
}, [
  onboardingQuery.data,
  hydrateFromBackend,
]);


  const initializeMutation = useMutation({
    mutationFn: (payload: OnboardingPayload) =>
      initializeOnboarding(payload),

    onSuccess: (data) => {
      queryClient.setQueryData(['onboarding'], data);
    },
  });

  const updateMutation = useMutation({
    mutationFn: (payload: OnboardingPayload) =>
      updateOnboarding(payload),

    onSuccess: (data) => {
      queryClient.setQueryData(['onboarding'], data);
    },
  });

  const completeMutation = useMutation({
    mutationFn: completeOnboarding,

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['onboarding'],
      });
    },
  });

  const questionsMutation = useMutation({
    mutationFn: getKIEQuestions,
  });

  const answersMutation = useMutation({
    mutationFn: (payload: OnboardingAnswersPayload) =>
      submitKIEAnswers(payload),
  });

  return {
    onboarding: onboardingQuery.data,
    isLoading: onboardingQuery.isLoading,
    onboardingError: onboardingQuery.error,

    initializeOnboarding:
      initializeMutation.mutateAsync,

    updateOnboarding:
      updateMutation.mutateAsync,

    completeOnboarding:
      completeMutation.mutateAsync,

    getKIEQuestions:
      questionsMutation.mutateAsync,

    submitKIEAnswers:
      answersMutation.mutateAsync,

    isSaving:
      initializeMutation.isPending ||
      updateMutation.isPending,

    isCompleting:
      completeMutation.isPending,

    isGettingQuestions:
      questionsMutation.isPending,

    isSubmittingAnswers:
      answersMutation.isPending,

    saveError:
      initializeMutation.error ||
      updateMutation.error,

    completeError:
      completeMutation.error,

    questionsError:
      questionsMutation.error,

    answersError:
      answersMutation.error,
  };
}
