'use client';

import { useQuery } from '@tanstack/react-query';
import { competeServices } from '@/services/competeServices';
import type { CompetitionFilters } from '@/types/compete';

export const competeKeys = {
  all: ['compete'] as const,
  lists: () => [...competeKeys.all, 'list'] as const,
  list: (filters: CompetitionFilters) => [...competeKeys.lists(), filters] as const,
  detail: (id: string) => [...competeKeys.all, 'detail', id] as const,
  recommendations: (filters: CompetitionFilters) =>
    [...competeKeys.all, 'recommendations', filters] as const,
};

export function useCompetitions(filters: CompetitionFilters = {}) {
  return useQuery({
    queryKey: competeKeys.list(filters),
    queryFn: () => competeServices.list(filters),
    staleTime: 60_000,
    retry: 1,
  });
}

export function useCompetition(competitionId?: string) {
  return useQuery({
    queryKey: competeKeys.detail(competitionId ?? ''),
    queryFn: () => competeServices.detail(competitionId as string),
    enabled: Boolean(competitionId),
    staleTime: 60_000,
    retry: 1,
  });
}

export function useCompetitionRecommendations(filters: CompetitionFilters = {}) {
  return useQuery({
    queryKey: competeKeys.recommendations(filters),
    queryFn: () => competeServices.recommendations(filters),
    staleTime: 60_000,
    retry: 1,
  });
}
