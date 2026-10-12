import { z } from 'zod';

export const lessonBlockTypeSchema = z.enum([
  'text',
  'example',
  'code',
  'question',
  'practice',
  'diagram',
  'video',
  'voice',
]);

export const lessonBlockSchema = z.object({
  id: z.string().min(1),
  type: lessonBlockTypeSchema,

  title: z.string().optional(),
  content: z.string().optional(),

  code: z.string().optional(),
  language: z.string().optional(),

  options: z.array(z.string()).optional(),
  answer: z.string().optional(),
  explanation: z.string().optional(),

  url: z.string().optional(),
  caption: z.string().optional(),
});

export const lessonSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),

  objective: z.string().optional(),

  prerequisites: z.array(z.string()).optional(),

  blocks: z.array(lessonBlockSchema),
});

export type LessonValidation = z.infer<typeof lessonSchema>;
export type LessonBlockValidation = z.infer<
  typeof lessonBlockSchema
>;