import { z } from 'zod';
/*Education*/
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

    domain: z
      .string()
      .trim()
      .min(1, 'Domain is required.'),

    currentYear: z.string().trim(),

    subjects: z.array(
      z.string().trim()
    ),

    graduationYear: z.string().trim(),

    degree: z.string().trim(),
  })
  .superRefine((data, ctx) => {
    const isStudent =
      data.academicStatus === 'BACHELOR' ||
      data.academicStatus === 'MASTER';

    /* ---------- BACHELOR / MASTER ---------- */

    if (isStudent) {
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

      if (!data.currentYear) {
        ctx.addIssue({
          code: 'custom',
          path: ['currentYear'],
          message: 'Please select your current year.',
        });
      }

      if (data.subjects.length === 0) {
        ctx.addIssue({
          code: 'custom',
          path: ['subjects'],
          message: 'Please add at least one subject.',
        });
      }
    }

    /* ---------- RECENT GRADUATE ---------- */

    if (data.academicStatus === 'RECENT_GRADUATE') {
      if (!data.degree) {
        ctx.addIssue({
          code: 'custom',
          path: ['degree'],
          message: 'Degree is required.',
        });
      }

      if (!data.graduationYear) {
        ctx.addIssue({
          code: 'custom',
          path: ['graduationYear'],
          message: 'Please select your graduation year.',
        });
      }
    }
  });

export type EducationFormData = z.infer<
  typeof educationSchema
>;

/*Career goals*/

export const careerGoalsSchema = z.object({
  primaryGoal: z
    .string()
    .trim()
    .min(1, 'Please enter your primary goal.'),

  targetSkills: z
    .array(z.string().trim().min(1))
    .min(1, 'Add at least one target skill.'),
});

export type CareerGoalsFormData = z.infer<
  typeof careerGoalsSchema
>;

/*Skills*/
export const skillsSchema = z.object({
  skills: z
    .array(z.string().trim().min(1))
    .min(1, 'Add at least one skill.'),

  projects: z.array(
    z.string().trim().min(1)
  ),

  research: z
    .string()
    .trim(),

  experience: z
    .string()
    .trim(),
});

export type SkillsFormData = z.infer<
  typeof skillsSchema
>;

/*Preferences*/
export const preferencesSchema = z.object({
  dailyStudyHours: z.enum(
    [
      'LESS_THAN_1',
      '1_2',
      '2_3',
      '3_4',
      '4_PLUS',
    ],
    {
      message: 'Please select your daily study time.',
    }
  ),

  learningDepth: z.enum(
    ['QUICK', 'BALANCED', 'DEEP'],
    {
      message:
        'Please select your preferred learning depth.',
    }
  ),
});

export type PreferencesFormData = z.infer<
  typeof preferencesSchema
>;

/* =========================================================
   OLD / MAIN ONBOARDING SCHEMA
   Kept for compatibility
========================================================= */

export const onboardingMainSchema = z.object({
  academicStatus: z.enum(
    ['BACHELOR', 'MASTER', 'RECENT_GRADUATE'],
    {
      message: 'Please select your academic status.',
    }
  ),

  primaryGoal: z
    .string()
    .trim()
    .min(1, 'Please enter your primary goal.'),

  targetSkills: z
    .array(z.string().trim().min(1))
    .min(1, 'Add at least one target skill.'),

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

export type OnboardingMainFormData = z.infer<
  typeof onboardingMainSchema
>;

/*Profile*/

export const profileReviewSchema = z.object({
  education: educationSchema,

  careerGoals: careerGoalsSchema,

  skills: skillsSchema,

  preferences: preferencesSchema,
});

export type ProfileReviewData = z.infer<
  typeof profileReviewSchema
>;