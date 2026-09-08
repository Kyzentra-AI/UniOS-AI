import { z } from 'zod';

export const educationSchema = z
  .object({
    academicStatus: z.enum(
      ['BACHELOR', 'MASTER', 'RECENT_GRADUATE'],
      {
        message: 'Please select your academic status.',
      }
    ),

    university: z.string().trim(),

    degreeProgram: z.string().trim(),

    semester: z.string().trim(),

    currentSubjects: z.array(
      z.string().trim()
    ),

    graduationStatus: z.string().trim(),

    degreeBackground: z.string().trim(),

    passoutYear: z.string().trim(),
  })
  .superRefine((data, ctx) => {
    if (
      data.academicStatus === 'BACHELOR' ||
      data.academicStatus === 'MASTER'
    ) {
      if (!data.university) {
        ctx.addIssue({
          code: 'custom',
          path: ['university'],
          message: 'University name is required.',
        });
      }

      if (!data.degreeProgram) {
        ctx.addIssue({
          code: 'custom',
          path: ['degreeProgram'],
          message: 'Degree program is required.',
        });
      }

      if (!data.semester) {
        ctx.addIssue({
          code: 'custom',
          path: ['semester'],
          message: 'Please select your semester.',
        });
      }
    }

    if (
      data.academicStatus ===
      'RECENT_GRADUATE'
    ) {
      if (!data.graduationStatus) {
        ctx.addIssue({
          code: 'custom',
          path: ['graduationStatus'],
          message:
            'Graduation status is required.',
        });
      }

      if (!data.degreeBackground) {
        ctx.addIssue({
          code: 'custom',
          path: ['degreeBackground'],
          message:
            'Degree background is required.',
        });
      }

      if (!data.passoutYear) {
        ctx.addIssue({
          code: 'custom',
          path: ['passoutYear'],
          message:
            'Please select your passout year.',
        });
      }
    }
  });

export const careerGoalsSchema = z.object({
  primaryGoal: z
    .string()
    .trim()
    .min(1, 'Please select your primary career goal.'),

  targetRoles: z
    .array(z.string())
    .min(1, 'Select at least one target role.'),

  industries: z
    .array(z.string())
    .min(1, 'Select at least one industry.'),
});

export const skillsSchema = z.object({
  skills: z
    .array(z.string())
    .min(1, 'Add at least one skill.'),

  experienceLevel: z.enum(
    ['BEGINNER', 'INTERMEDIATE', 'ADVANCED'],
    {
      message:
        'Please select your experience level.',
    }
  ),

  projects: z.array(z.string()),

  portfolioUrl: z
    .string()
    .trim()
    .url('Please enter a valid portfolio URL.')
    .or(z.literal('')),

  githubUrl: z
    .string()
    .trim()
    .url('Please enter a valid GitHub URL.')
    .or(z.literal('')),
});

export const preferencesSchema = z.object({
  language: z.enum(
    [
      'ENGLISH',
      'HINDI',
      'MARATHI',
      'KANNADA',
      'TAMIL',
      'BENGALI',
      'TELUGU',
    ],
    {
      message:
        'Please select your learning language.',
    }
  ),

  learningModes: z
    .array(
      z.enum([
        'VISUAL',
        'STORY',
        'VOICE',
        'TEXT',
      ])
    )
    .min(
      1,
      'Select at least one learning mode.'
    ),
});

export type EducationFormData = z.infer<
  typeof educationSchema
>;

export type CareerGoalsFormData = z.infer<
  typeof careerGoalsSchema
>;

export type SkillsFormData = z.infer<
  typeof skillsSchema
>;

export type PreferencesFormData = z.infer<
  typeof preferencesSchema
>;