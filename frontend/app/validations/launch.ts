
import { z } from 'zod';

const text = z.string().trim();

const optionalUrl = text.refine(
  (value) => !value || z.string().url().safeParse(value).success,
  'Enter a valid URL',
);

export const resumeContactSchema = z.object({
  fullName: text.min(1, 'Full name is required'),
  email: z.string().trim().email('Enter a valid email'),
  phone: text,
  location: text,
  linkedInUrl: optionalUrl,
  githubUrl: optionalUrl,
  portfolioUrl: optionalUrl,
});

export const resumeEducationSchema = z.object({
  id: z.string().min(1),
  institution: text,
  degree: text,
  fieldOfStudy: text,
  startDate: text,
  endDate: text,
  grade: text,
});

export const resumeExperienceSchema = z.object({
  id: z.string().min(1),
  company: text,
  role: text,
  location: text,
  startDate: text,
  endDate: text,
  isCurrent: z.boolean(),
  description: text,
});

export const resumeProjectSchema = z.object({
  id: z.string().min(1),
  name: text.min(1, 'Project name is required'),
  description: text,
  technologies: z.array(text),
  projectUrl: optionalUrl,
  startDate: text,
  endDate: text,
});

export const resumeAchievementSchema = z.object({
  id: z.string().min(1),
  title: text.min(1, 'Achievement title is required'),
  description: text,
  date: text,
});

export const resumeDraftSchema = z.object({
  contact: resumeContactSchema,
  headline: text,
  summary: text,
  skills: z.array(text),
  education: z.array(resumeEducationSchema),
  experience: z.array(resumeExperienceSchema),
  projects: z.array(resumeProjectSchema),
  achievements: z.array(resumeAchievementSchema),
});

export const resumePreferencesSchema = z.object({
  targetRole: text.optional(),
  tone: z.enum(['professional', 'concise']).optional(),
});

export const generateResumeSchema = z.object({
  title: text.min(1, 'Resume title is required'),
  source: z.enum(['profile', 'manual']),
  content: resumeDraftSchema,
  preferences: resumePreferencesSchema.optional(),
});

export const updateResumeSchema = z.object({
  title: text.min(1, 'Resume title is required'),
  content: resumeDraftSchema,
});

export const atsScoreSchema = z.object({
  value: z.number().min(0),
  maxValue: z.number().positive(),
  methodology: text.min(1),
  methodologyVersion: text.min(1),
}).refine(
  (score) => score.value <= score.maxValue,
  'Score cannot exceed its maximum',
);

export const atsFindingSchema = z.object({
  id: z.string().min(1),
  category: z.enum([
    'structure',
    'content',
    'formatting',
    'contact_information',
    'missing_information',
    'readability',
  ]),
  severity: z.enum(['info', 'warning', 'critical']),
  title: text.min(1),
  description: text.min(1),
  recommendation: text.min(1),
});

export const atsAnalysisSchema = z.object({
  analysis: z.object({
    id: z.string().min(1),
    status: z.enum(['completed', 'failed']),
    document: z.object({
      fileName: z.string(),
      fileType: z.enum(['pdf', 'docx']),
      pageCount: z.number().nullable(),
      extractedCharacterCount: z.number().min(0),
    }),
    score: atsScoreSchema.nullable(),
    summary: z.string(),
    findings: z.array(atsFindingSchema),
    createdAt: z.string(),
  }),
});

export type ResumeDraftInput = z.infer<typeof resumeDraftSchema>;
export type GenerateResumeInput = z.infer<typeof generateResumeSchema>;
export type UpdateResumeInput = z.infer<typeof updateResumeSchema>;
