import { z } from 'zod';

export const missionStatusSchema = z.enum([
  'PENDING',
  'IN_PROGRESS',
  'COMPLETED',
  'DEFERRED',
  'SKIPPED',
]);

export const missionTypeSchema = z.enum([
  'LEARNING',
  'REVISION',
  'ASSIGNMENT',
  'PRACTICAL',
  'ARTIFACT',
  'CAREER',
]);

export const missionSchema = z.object({
  id: z.string(),
  roadmap_id: z.string(),
  title: z.string(),
  description: z.string().nullable().optional(),
  mission_type: missionTypeSchema,
  subject: z.string().nullable().optional(),
  priority: z.string().nullable().optional(),
  estimated_minutes: z.number().nullable().optional(),
  week: z.number().nullable().optional(),
  sequence: z.number().nullable().optional(),
  status: missionStatusSchema,
});

export const missionResponseSchema = missionSchema;

export const completeMissionResponseSchema = missionSchema;