import { apiRequest } from '@/lib/api';
import type {
  CompetitionDetailResponse,
  CompetitionFilters,
  CompetitionListResponse,
  CompetitionRecommendationResponse,
} from '@/types/compete';
import { competitionFiltersSchema } from '@/app/validations/compete';

const BASE = '/api/v1/compete';

function toQuery(filters: CompetitionFilters): string {
  const parsed = competitionFiltersSchema.safeParse(filters);
  if (!parsed.success) {
    throw new Error('Invalid competition filters. Please review the selected filters.');
  }

  const params = new URLSearchParams();
  const value = parsed.data;

  if (value.search) params.set('search', value.search);
  value.types?.forEach((item) => params.append('type', item));
  value.domains?.forEach((item) => params.append('domain', item));
  value.skills?.forEach((item) => params.append('skill', item));
  value.difficulty?.forEach((item) => params.append('difficulty', item));
  value.goals?.forEach((item) => params.append('goal', item));
  value.eligibility?.forEach((item) => params.append('eligibility', item));
  value.status?.forEach((item) => params.append('status', item));
  if (value.deadlineBefore) params.set('deadline_before', value.deadlineBefore);
  if (value.page) params.set('page', String(value.page));
  if (value.pageSize) params.set('page_size', String(value.pageSize));
  if (value.sort) params.set('sort', value.sort);

  return params.toString();
}

export const competeServices = {
  list(filters: CompetitionFilters = {}) {
    const query = toQuery(filters);
    return apiRequest<CompetitionListResponse>(
      `${BASE}/competitions${query ? `?${query}` : ''}`,
      { method: 'GET' },
    );
  },

  detail(competitionId: string) {
    return apiRequest<CompetitionDetailResponse>(
      `${BASE}/competitions/${encodeURIComponent(competitionId)}`,
      { method: 'GET' },
    );
  },

  recommendations(filters: CompetitionFilters = {}) {
    const query = toQuery(filters);
    return apiRequest<CompetitionRecommendationResponse>(
      `${BASE}/recommendations${query ? `?${query}` : ''}`,
      { method: 'GET' },
    );
  },
};
