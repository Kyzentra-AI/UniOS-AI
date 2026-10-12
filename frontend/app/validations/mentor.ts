import { z } from 'zod';

export const mentorModeSchema = z.enum([
  'tutor',
  'study-coach',
  'accountability',
  'motivation',
]);

export const mentorContextSchema = z.object({
  learnerId: z.string().optional(),
  roadmapId: z.string().optional(),
  missionId: z.string().optional(),
  lessonId: z.string().optional(),
  topic: z.string().optional(),
});

export const mentorMessageSchema = z.object({
  id: z.string().min(1),
  role: z.enum(['user', 'mentor']),
  content: z.string(),
  createdAt: z.string().optional(),
});

export const mentorConversationSchema = z.object({
  id: z.string().min(1),
  mode: mentorModeSchema,
  messages: z.array(mentorMessageSchema),
});

export type MentorValidation = z.infer<
  typeof mentorConversationSchema
>;