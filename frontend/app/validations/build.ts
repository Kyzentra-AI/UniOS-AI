import { z } from 'zod';

const optionalText = z.string().trim().optional().or(z.literal(''));
export const projectTypes = ['CODING', 'RESEARCH', 'BUSINESS', 'ANALYSIS', 'DESIGN', 'OTHER'] as const;
export const projectStatuses = ['DRAFT', 'ACTIVE', 'COMPLETED', 'ARCHIVED'] as const;
export const artifactTypes = ['DOCUMENT', 'UPLOAD', 'DELIVERABLE', 'PRESENTATION', 'EVIDENCE'] as const;

export const createProjectSchema = z.object({
  title: z.string().trim().min(3, 'Enter a project title of at least 3 characters.').max(120, 'Keep the title under 120 characters.'),
  description: optionalText,
  type: z.enum(projectTypes),
  domain: optionalText,
  goal: optionalText,
  skills: z.array(z.string().trim().min(1)).default([]),
});
export const updateProjectSchema = createProjectSchema.partial().extend({ status: z.enum(projectStatuses).optional() });
export const createMilestoneSchema = z.object({ title: z.string().trim().min(2).max(160), description: optionalText, orderIdx: z.number().int().min(0).optional() });
export const createTaskSchema = z.object({ title: z.string().trim().min(2).max(160), description: optionalText, milestoneId: z.string().optional(), orderIdx: z.number().int().min(0).optional() });
export const createArtifactSchema = z.object({ title: z.string().trim().min(2).max(160), description: optionalText, type: z.enum(artifactTypes) });
export const createEvidenceSchema = z.object({ title: z.string().trim().min(2).max(160), description: optionalText, artifactId: z.string().optional(), skills: z.array(z.string().trim().min(1)).default([]) });
export const buildCoachSchema = z.object({ intent: z.string().trim().min(1), message: z.string().trim().min(1).max(5000) });

export type CreateProjectFormValues = z.infer<typeof createProjectSchema>;
