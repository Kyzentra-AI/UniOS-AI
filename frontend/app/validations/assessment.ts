import { z } from 'zod';

export const assessmentTypeSchema = z.enum([
  'mcq',
  'subjective',
  'viva',
  'case-study',
  'coding',
]);

export const assessmentOptionSchema = z.object({
  id: z.string().min(1),
  text: z.string().min(1),
});

export const assessmentQuestionSchema = z.object({
  id: z.string().min(1),
  type: assessmentTypeSchema,
  question: z.string().min(1),
  options: z.array(assessmentOptionSchema).optional(),
  code: z.string().optional(),
  language: z.string().optional(),
});

export const assessmentSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  type: assessmentTypeSchema,
  instructions: z.string().optional(),
  questions: z.array(assessmentQuestionSchema),
});

export const assessmentAnswerSchema = z.object({
  questionId: z.string().min(1),
  answer: z.string(),
});

export const assessmentAttemptSchema = z.object({
  assessmentId: z.string().min(1),
  answers: z.array(assessmentAnswerSchema),
});

export type AssessmentValidation = z.infer<
  typeof assessmentSchema
>;

export type AssessmentAttemptValidation = z.infer<
  typeof assessmentAttemptSchema
>;