import { z } from 'zod';

export const syllabusStatusSchema = z.enum([
  'PROCESSING',
  'WAITING_FOR_CONFIRMATION',
  'CONFIRMED',
  'FAILED',
]);

export const syllabusUploadResponseSchema = z.object({
  id: z.string(),
  status: syllabusStatusSchema,
});

export const syllabusStatusResponseSchema = z.object({
  id: z.string(),
  status: syllabusStatusSchema,
});

export const syllabusSubjectSchema = z.object({
  name: z.string(),
  topics: z.array(z.string()),
});

export const parsedSyllabusContentSchema = z.object({
  subjects: z.array(syllabusSubjectSchema),
});

export const syllabusSchema = z.object({
  id: z.string(),
  status: syllabusStatusSchema,
  parsed_content: parsedSyllabusContentSchema
    .nullable()
    .optional(),
});

export const syllabusMessageResponseSchema =
  z.object({
    message: z.string(),
    status: syllabusStatusSchema.optional(),
  });