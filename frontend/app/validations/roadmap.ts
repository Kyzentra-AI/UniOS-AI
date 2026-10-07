import { z } from 'zod';

const missionTypeSchema = z.enum([
  'LEARNING',
  'REVISION',
  'ASSIGNMENT',
  'PRACTICAL',
  'ARTIFACT',
  'CAREER',
]);

const missionStatusSchema = z.enum([
  'PENDING',
  'IN_PROGRESS',
  'COMPLETED',
  'DEFERRED',
  'SKIPPED',
]);

const roadmapMissionSchema = z.object({
  id: z.string(),
  roadmap_id: z.string(),
  title: z.string(),
  description: z.string(),
  mission_type: missionTypeSchema,
  subject: z.string().nullable().optional(),
  priority: z.string(),
  estimated_minutes: z.number(),
  week: z.number(),
  sequence: z.number(),
  status: missionStatusSchema,
});

const roadmapPlanMissionSchema = z.object({
  title: z.string(),
  type: missionTypeSchema,
  description: z.string(),
  priority: z.string(),
  estimated_minutes: z.number(),
  subject: z.string().nullable().optional(),
  week: z.number(),
  sequence: z.number(),
});

const roadmapSubjectSchema = z.object({
  name: z.string(),
  topics: z.array(z.string()),
});

const roadmapSemesterSchema = z.object({
  name: z.string(),
  subjects: z.array(roadmapSubjectSchema),
});

const roadmapCareerSchema = z.object({
  goals: z.array(z.string()),
});

const roadmapScopeDataSchema = z.object({
  scope: z.string(),
  semesters: z.array(roadmapSemesterSchema),
  career: roadmapCareerSchema.nullable().optional(),
  goals: z.array(z.string()),
  milestones: z.array(z.string()),
  missions: z.array(roadmapPlanMissionSchema),
});

const roadmapSchema = z.object({
  id: z.string(),
  version: z.number(),
  scope: z.enum(['ACADEMIC', 'CAREER', 'BOTH']),
  status: z.enum(['ACTIVE', 'INACTIVE']),
  scope_data: roadmapScopeDataSchema,
  missions: z.array(roadmapMissionSchema),
  created_at: z.string().nullable().optional(),
  updated_at: z.string().nullable().optional(),
});

export const roadmapResponseSchema = z.object({
  roadmap: roadmapSchema.nullable(),
});

export const roadmapGenerationResponseSchema = z.object({
  message: z.string(),
  status: z.literal('PROCESSING'),
});