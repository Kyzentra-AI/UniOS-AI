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

export default function SkillsOnboarding() {
  const router = useRouter();

  const { skills, setSkills, setCurrentStep } =
    useOnboardingStore();

  const [skillInput, setSkillInput] = useState('');
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
      projects: skills.projects,
      research: skills.research,
      experience: skills.experience,
    },
  });

  const selectedSkills = watch('skills') ?? [];
  const projects = watch('projects') ?? [];

  useEffect(() => {
    setCurrentStep(3);
  }, [setCurrentStep]);

 //Skills
  const addSkill = () => {
    const skill = skillInput.trim();

    if (!skill) return;

    const alreadyExists = selectedSkills.some(
      (item) => item.toLowerCase() === skill.toLowerCase()
    );

    if (alreadyExists) {
      setSkillInput('');
      return;
    }

    setValue(
      'skills',
      [...selectedSkills, skill],
      {
        shouldValidate: true,
      }
    );

    setSkillInput('');
  };

  const removeSkill = (skill: string) => {
    setValue(
      'skills',
      selectedSkills.filter((item) => item !== skill),
      {
        shouldValidate: true,
      }
    );
  };

   //Projects
  const addProject = () => {
    const project = projectInput.trim();

    if (!project) return;

    const alreadyExists = projects.some(
      (item) =>
        item.toLowerCase() === project.toLowerCase()
    );

    if (alreadyExists) {
      setProjectInput('');
      return;
    }

    setValue(
      'projects',
      [...projects, project]
    );

    setProjectInput('');
  };

  const removeProject = (project: string) => {
    setValue(
      'projects',
      projects.filter((item) => item !== project)
    );
  };

 //Submission

  const onSubmit = (data: SkillsFormData) => {
  setSkills({
    skills: data.skills,
    projects: data.projects,
    research: data.research,
    experience: data.experience,
  });

  setCurrentStep(4);
  router.push('/onboarding/preferences');
};

  return (
    <div className="min-h-[calc(100vh-4rem)] px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-3xl">

        {/* Header */}
        <div className="mb-10">
          <p className="mb-2 text-sm font-semibold text-[var(--primary)]">
            Step 3 of 6
          </p>

          <h1 className="text-3xl font-bold tracking-tight text-[var(--text-primary)]">
            Tell us about your skills
          </h1>

          <p className="mt-2 text-[var(--text-secondary)]">
            Add the skills you already have and optionally
            tell us about your projects, research, and experience.
          </p>
        </div>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-8"
        >

          {/* Skills */}
          <section>
            <label className="mb-2 block text-sm font-semibold text-[var(--text-label)]">
              Your Skills
            </label>

            <p className="mb-3 text-sm text-[var(--text-secondary)]">
              Add the technical or professional skills you already have.
            </p>

            <div className="flex gap-2">
              <input
                value={skillInput}
                onChange={(event) =>
                  setSkillInput(event.target.value)
                }
                onKeyDown={(event) => {
                  if (event.key === 'Enter') {
                    event.preventDefault();
                    addSkill();
                  }
                }}
                placeholder="e.g. React"
                className="flex-1 rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] focus:border-[var(--primary)]"
              />

              <button
                type="button"
                onClick={addSkill}
                className="rounded-xl border border-[var(--border)] px-5 py-3 text-sm font-semibold text-[var(--text-primary)] transition hover:border-[var(--primary)]"
              >
                Add
              </button>
            </div>

            {selectedSkills.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {selectedSkills.map((skill) => (
                  <div
                    key={skill}
                    className="flex items-center gap-2 rounded-lg bg-[var(--primary-soft)] px-3 py-2 text-sm text-[var(--primary)]"
                  >
                    <span>{skill}</span>

                    <button
                      type="button"
                      onClick={() => removeSkill(skill)}
                      className="font-bold"
                      aria-label={`Remove ${skill}`}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}

            {errors.skills && (
              <p className="mt-2 text-sm text-[var(--danger)]">
                {errors.skills.message}
              </p>
            )}
          </section>

          {/* Projects */}
          <section>
            <label className="mb-2 block text-sm font-semibold text-[var(--text-label)]">
              Projects
              <span className="ml-2 font-normal text-[var(--text-muted)]">
                (Optional)
              </span>
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

            {projects.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {projects.map((project) => (
                  <div
                    key={project}
                    className="flex items-center gap-2 rounded-lg bg-[var(--primary-soft)] px-3 py-2 text-sm text-[var(--primary)]"
                  >
                    <span>{project}</span>

                    <button
                      type="button"
                      onClick={() => removeProject(project)}
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

          {/* Research */}
          <section>
            <label
              htmlFor="research"
              className="mb-2 block text-sm font-semibold text-[var(--text-label)]"
            >
              Research Experience
              <span className="ml-2 font-normal text-[var(--text-muted)]">
                (Optional)
              </span>
            </label>

            <textarea
              id="research"
              rows={4}
              placeholder="Describe any research work, papers, experiments, or research interests..."
              {...register('research')}
              className="w-full resize-none rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] focus:border-[var(--primary)]"
            />
          </section>

          {/* Experience */}
          <section>
            <label
              htmlFor="experience"
              className="mb-2 block text-sm font-semibold text-[var(--text-label)]"
            >
              Work / Internship Experience
              <span className="ml-2 font-normal text-[var(--text-muted)]">
                (Optional)
              </span>
            </label>

            <textarea
              id="experience"
              rows={4}
              placeholder="Describe any internship, job, freelance, or other practical experience..."
              {...register('experience')}
              className="w-full resize-none rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)] focus:border-[var(--primary)]"
            />
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