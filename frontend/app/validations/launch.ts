import { z } from 'zod';

export const resumeSchema = z.object({
  fullName: z.string().trim().min(1, 'Name is required'),
  email: z.string().trim().email('Enter a valid email'),
  phone: z.string().trim(),
  location: z.string().trim(),
  headline: z.string().trim(),
  summary: z.string().trim(),
  skills: z.string().trim(),
  education: z.array(
    z.object({
      id: z.string(),
      institution: z.string().trim(),
      degree: z.string().trim(),
      startYear: z.string(),
      endYear: z.string(),
      grade: z.string().trim(),
    }),
  ),
  projects: z.array(
    z.object({
      id: z.string(),
      name: z.string().trim(),
      description: z.string().trim(),
      technologies: z.string().trim(),
      link: z.string().trim(),
    }),
  ),
  achievements: z.array(
    z.object({
      id: z.string(),
      title: z.string().trim(),
      description: z.string().trim(),
    }),
  ),
});

export type ResumeFormValues = z.infer<typeof resumeSchema>;

export const atsFileSchema = z.object({
  name: z.string().min(1),
  size: z.number().positive().max(
    5 * 1024 * 1024,
    'File must be 5 MB or smaller',
  ),
  type: z.enum([
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ]),
});