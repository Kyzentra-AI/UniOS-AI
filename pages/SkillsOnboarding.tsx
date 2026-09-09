
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import {
  skillsSchema,
  type SkillsFormData,
} from '@/app/validations/onboarding';

import { useOnboardingStore } from '@/stores/onboardingstore';

const skillOptions = [
  'JavaScript',
  'TypeScript',
  'React',
  'Next.js',
  'Node.js',
  'Python',
  'Java',
  'C++',
  'SQL',
  'PostgreSQL',
  'MongoDB',
  'FastAPI',
  'Machine Learning',
  'AI / LLMs',
  'Git / GitHub',
  'Docker',
];

export default function SkillsOnboarding() {
  const router = useRouter();

  const { skills, setSkills, setCurrentStep } =
    useOnboardingStore();

  const [projectInput, setProjectInput] = useState('');

  const {
    handleSubmit,
    setValue,
    watch,
    register,
    formState: { errors },
  } = useForm<SkillsFormData>({
    resolver: zodResolver(skillsSchema),
    defaultValues: {
      skills: skills.skills,
      experienceLevel:
      skills.experienceLevel === ''? undefined: skills.experienceLevel,
      projects: skills.projects,
      portfolioUrl: skills.portfolioUrl,
      githubUrl: skills.githubUrl,
    },
  });

  const selectedSkills = watch('skills');
  const experienceLevel = watch('experienceLevel');
  const projects = watch('projects');

  useEffect(() => {
    setCurrentStep(3);
  }, [setCurrentStep]);

  const toggleSkill = (skill: string) => {
    const currentSkills = selectedSkills ?? [];

    const updatedSkills = currentSkills.includes(skill)
      ? currentSkills.filter((item) => item !== skill)
      : [...currentSkills, skill];

    setValue('skills', updatedSkills, {
      shouldValidate: true,
    });
  };

  const addProject = () => {
    const project = projectInput.trim();

    if (!project) return;

    const currentProjects = projects ?? [];

    if (currentProjects.includes(project)) {
      setProjectInput('');
      return;
    }

    setValue(
      'projects',
      [...currentProjects, project],
      {
        shouldValidate: true,
      }
    );

    setProjectInput('');
  };

  const removeProject = (project: string) => {
    setValue(
      'projects',
      (projects ?? []).filter(
        (item) => item !== project
      ),
      {
        shouldValidate: true,
      }
    );
  };

  const onSubmit = (data: SkillsFormData) => {
    setSkills({
      skills: data.skills,
      experienceLevel: data.experienceLevel,
      projects: data.projects,
      portfolioUrl: data.portfolioUrl,
      githubUrl: data.githubUrl,
    });

    setCurrentStep(4);
    router.push('/onboarding/preferences');
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">
        <div className="mb-10">
          <p className="mb-2 text-sm font-semibold text-[var(--primary)]">
            Step 3 of 6
          </p>

          <h1 className="text-3xl font-bold tracking-tight text-[var(--text-primary)]">
            Tell us about your skills
          </h1>

          <p className="mt-2 text-[var(--text-secondary)]">
            Select the skills you already have and tell us
            about your experience.
          </p>
        </div>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-8"
        >
          {/* Skills */}
          <section>
            <label className="mb-4 block text-sm font-semibold text-[var(--text-label)]">
              Your Skills
            </label>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
              {skillOptions.map((skill) => {
                const selected =
                  selectedSkills?.includes(skill);

                return (
                  <button
                    key={skill}
                    type="button"
                    onClick={() => toggleSkill(skill)}
                    className={`rounded-xl border px-4 py-3 text-sm font-medium transition ${
                      selected
                        ? 'border-[var(--primary)] bg-[var(--primary-soft)] text-[var(--primary)]'
                        : 'border-[var(--border)] bg-[var(--surface)] text-[var(--text-secondary)] hover:border-[var(--primary)]'
                    }`}
                  >
                    {skill}
                  </button>
                );
              })}
            </div>

            {errors.skills && (
              <p className="mt-2 text-sm text-[var(--danger)]">
                {errors.skills.message}
              </p>
            )}
          </section>

          {/* Experience Level */}
          <section>
            <label className="mb-4 block text-sm font-semibold text-[var(--text-label)]">
              Experience Level
            </label>

            <div className="grid gap-3 sm:grid-cols-3">
              {[
                {
                  value: 'BEGINNER',
                  label: 'Beginner',
                  description:
                    'I am starting out and building my foundation.',
                },
                {
                  value: 'INTERMEDIATE',
                  label: 'Intermediate',
                  description:
                    'I can build projects independently.',
                },
                {
                  value: 'ADVANCED',
                  label: 'Advanced',
                  description:
                    'I have strong practical experience.',
                },
              ].map((level) => {
                const selected =
                  experienceLevel === level.value;

                return (
                  <button
                    key={level.value}
                    type="button"
                    onClick={() =>
                      setValue(
                        'experienceLevel',
                        level.value as SkillsFormData['experienceLevel'],
                        {
                          shouldValidate: true,
                        }
                      )
                    }
                    className={`rounded-xl border p-4 text-left transition ${
                      selected
                        ? 'border-[var(--primary)] bg-[var(--primary-soft)]'
                        : 'border-[var(--border)] bg-[var(--surface)] hover:border-[var(--primary)]'
                    }`}
                  >
                    <p className="font-semibold text-[var(--text-primary)]">
                      {level.label}
                    </p>

                    <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
                      {level.description}
                    </p>
                  </button>
                );
              })}
            </div>

            {errors.experienceLevel && (
              <p className="mt-2 text-sm text-[var(--danger)]">
                {errors.experienceLevel.message}
              </p>
            )}
          </section>

          {/* Projects */}
          <section>
            <label className="mb-2 block text-sm font-semibold text-[var(--text-label)]">
              Projects
            </label>

            <p className="mb-3 text-sm text-[var(--text-secondary)]">
              Add projects you have worked on.
            </p>

            <div className="flex gap-2">
              <input
                value={projectInput}
                onChange={(event) =>
                  setProjectInput(event.target.value)
                }
                onKeyDown={(event) => {
                  if (event.key === 'Enter') {
                    event.preventDefault();
                    addProject();
                  }
                }}
                placeholder="e.g. AI Career Recommender"
                className="flex-1 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] focus:border-[var(--primary)]"
              />

              <button
                type="button"
                onClick={addProject}
                className="rounded-xl border border-[var(--border)] px-5 py-3 text-sm font-semibold text-[var(--text-primary)] transition hover:border-[var(--primary)]"
              >
                Add
              </button>
            </div>

            {projects?.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {projects.map((project) => (
                  <div
                    key={project}
                    className="flex items-center gap-2 rounded-lg bg-[var(--primary-soft)] px-3 py-2 text-sm text-[var(--primary)]"
                  >
                    <span>{project}</span>

                    <button
                      type="button"
                      onClick={() =>
                        removeProject(project)
                      }
                      className="font-bold"
                      aria-label={`Remove ${project}`}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Portfolio */}
          <section>
            <label
              htmlFor="portfolioUrl"
              className="mb-2 block text-sm font-semibold text-[var(--text-label)]"
            >
              Portfolio URL
            </label>

            <input
              id="portfolioUrl"
              type="url"
              placeholder="https://yourportfolio.com"
              {...register('portfolioUrl')}
              className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] focus:border-[var(--primary)]"
            />

            {errors.portfolioUrl && (
              <p className="mt-2 text-sm text-[var(--danger)]">
                {errors.portfolioUrl.message}
              </p>
            )}
          </section>

          {/* GitHub */}
          <section>
            <label
              htmlFor="githubUrl"
              className="mb-2 block text-sm font-semibold text-[var(--text-label)]"
            >
              GitHub URL
            </label>

            <input
              id="githubUrl"
              type="url"
              placeholder="https://github.com/username"
              {...register('githubUrl')}
              className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] focus:border-[var(--primary)]"
            />

            {errors.githubUrl && (
              <p className="mt-2 text-sm text-[var(--danger)]">
                {errors.githubUrl.message}
              </p>
            )}
          </section>

          {/* Navigation */}
          <div className="flex items-center justify-between border-t border-[var(--border)] pt-6">
            <button
              type="button"
              onClick={() =>
                router.push('/onboarding/career')
              }
              className="text-sm font-semibold text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
            >
              ← Back to career goals
            </button>

            <button
              type="submit"
              className="rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[var(--primary-hover)]"
            >
              Continue →
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}


