import { z } from 'zod';

export const competitionTypeSchema = z.enum([
  'HACKATHON',
  'CODING_COMPETITION',
  'INNOVATION_CHALLENGE',
  'STUDENT_CHALLENGE',
  'CASE_COMPETITION',
  'RESEARCH_CHALLENGE',
  'OTHER',
]);

export const competitionDomainSchema = z.enum([
  'AI_ML',
  'WEB_DEVELOPMENT',
  'DATA_SCIENCE',
  'CYBERSECURITY',
  'CLOUD_DEVOPS',
  'DESIGN',
  'BUSINESS',
  'ROBOTICS',
  'SUSTAINABILITY',
  'GENERAL',
]);

export const competitionDifficultySchema = z.enum([
  'BEGINNER',
  'INTERMEDIATE',
  'ADVANCED',
  'ALL_LEVELS',
]);

export const competitionGoalSchema = z.enum([
  'LEARNING',
  'PORTFOLIO',
  'PRIZES',
  'NETWORKING',
  'RESEARCH',
  'CAREER',
  'SOCIAL_IMPACT',
]);

export const competitionFiltersSchema = z.object({
  search: z.string().trim().max(120).optional(),
  types: z.array(competitionTypeSchema).optional(),
  domains: z.array(competitionDomainSchema).optional(),
  skills: z.array(z.string().trim().min(1).max(60)).max(20).optional(),
  difficulty: z.array(competitionDifficultySchema).optional(),
  goals: z.array(competitionGoalSchema).optional(),
  eligibility: z.array(z.enum(['ELIGIBLE', 'NOT_ELIGIBLE', 'NEEDS_REVIEW', 'UNKNOWN'])).optional(),
  status: z.array(z.enum(['UPCOMING', 'OPEN', 'CLOSING_SOON', 'CLOSED', 'ONGOING'])).optional(),
  deadlineBefore: z.string().datetime().optional(),
  page: z.number().int().min(1).optional(),
  pageSize: z.number().int().min(1).max(50).optional(),
  sort: z.enum(['deadline_asc', 'newest', 'recommended']).optional(),
});

export type CompetitionFiltersInput = z.infer<typeof competitionFiltersSchema>;
