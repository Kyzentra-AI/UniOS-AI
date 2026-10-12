
import { z } from 'zod';

const optionalTrimmedString = (max: number, message: string) =>
  z.string().trim().max(max, message).optional();

export const createProjectSchema = z.object({
  title: z
    .string()
    .trim()
    .min(3, 'Project title must be at least 3 characters.')
    .max(100, 'Project title cannot exceed 100 characters.'),

  description: optionalTrimmedString(
    1000,
    'Description cannot exceed 1000 characters.',
  ),

  type: z.enum([
    'CODING',
    'RESEARCH',
    'BUSINESS',
    'ANALYSIS',
    'DESIGN',
    'OTHER',
  ]),

  domain: optionalTrimmedString(
    100,
    'Domain cannot exceed 100 characters.',
  ),

  goal: optionalTrimmedString(
    500,
    'Goal cannot exceed 500 characters.',
  ),

  skills: z
    .array(z.string().trim().min(1, 'Skill cannot be empty.'))
    .max(20, 'Maximum 20 skills allowed.')
    .default([]),
});

export const createMilestoneSchema = z.object({
  projectId: z.string().min(1, 'Project ID is required.'),

  title: z
    .string()
    .trim()
    .min(3, 'Milestone title must be at least 3 characters.')
    .max(150, 'Milestone title cannot exceed 150 characters.'),

  description: optionalTrimmedString(
    500,
    'Description cannot exceed 500 characters.',
  ),
});

export const createTaskSchema = z.object({
  projectId: z.string().min(1, 'Project ID is required.'),

  milestoneId: z.string().optional(),

  title: z
    .string()
    .trim()
    .min(3, 'Task title must be at least 3 characters.')
    .max(150, 'Task title cannot exceed 150 characters.'),

  description: optionalTrimmedString(
    500,
    'Description cannot exceed 500 characters.',
  ),
});

export const createArtifactSchema = z.object({
  projectId: z.string().min(1, 'Project ID is required.'),

  title: z
    .string()
    .trim()
    .min(3, 'Artifact title must be at least 3 characters.')
    .max(150, 'Artifact title cannot exceed 150 characters.'),

  description: optionalTrimmedString(
    1000,
    'Description cannot exceed 1000 characters.',
  ),

  type: z.enum([
    'DOCUMENT',
    'UPLOAD',
    'DELIVERABLE',
    'PRESENTATION',
    'EVIDENCE',
  ]),

  fileName: z.string().optional(),

  fileSize: z
    .number()
    .int()
    .nonnegative('File size cannot be negative.')
    .optional(),
});

export const createEvidenceSchema = z.object({
  projectId: z.string().min(1, 'Project ID is required.'),

  artifactId: z.string().optional(),

  title: z
    .string()
    .trim()
    .min(3, 'Evidence title must be at least 3 characters.')
    .max(150, 'Evidence title cannot exceed 150 characters.'),

  description: optionalTrimmedString(
    1000,
    'Description cannot exceed 1000 characters.',
  ),

  skills: z
    .array(z.string().trim().min(1, 'Skill cannot be empty.'))
    .max(20, 'Maximum 20 skills allowed.')
    .default([]),
});

export type CreateProjectForm = z.infer<typeof createProjectSchema>;
export type CreateMilestoneForm = z.infer<typeof createMilestoneSchema>;
export type CreateTaskForm = z.infer<typeof createTaskSchema>;
export type CreateArtifactForm = z.infer<typeof createArtifactSchema>;
export type CreateEvidenceForm = z.infer<typeof createEvidenceSchema>;
