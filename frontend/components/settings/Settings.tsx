
'use client';

import { useEffect, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';

import { apiRequest } from '@/lib/api';
import { clearSession } from '@/lib/auth';

import {
  useDeleteSettingsAccount,
  useSettingsAccount,
  useSettingsContext,
  useSettingsFiles,
  useSettingsPreferences,
  useSettingsProfile,
  useUpdateSettingsPreferences,
  useUpdateSettingsProfile,
  useUploadSettingsAvatar,
} from '@/hooks/useSettings';

import {
  clearOnboardingDraft,
  useOnboardingStore,
} from '@/stores/onboardingstore';

import type {
  DeleteAccountPayload,
  FileCategory,
  SettingsPreferencesPatch,
} from '@/types/settings';

type SettingsTab =
  | 'profile'
  | 'context'
  | 'files'
  | 'preferences'
  | 'account';

const tabs: { id: SettingsTab; label: string }[] = [
  { id: 'profile', label: 'Profile' },
  { id: 'context', label: 'AI Context' },
  { id: 'files', label: 'My Files' },
  { id: 'preferences', label: 'Preferences' },
  { id: 'account', label: 'Account & Security' },
];

function formatDate(value?: string | null) {
  if (!value) return '—';

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

function formatFileSize(bytes?: number | null) {
  if (bytes == null) return '—';
  if (bytes < 1024) return `${bytes} B`;

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function parseCommaSeparated(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function SectionHeading({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <div className="mb-6">
      <h2 className="text-xl font-semibold text-[var(--foreground)]">
        {title}
      </h2>

      {description && (
        <p className="mt-1 text-sm text-[var(--muted-foreground)]">
          {description}
        </p>
      )}
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = 'text',
  readOnly = false,
}: {
  label: string;
  value: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  type?: string;
  readOnly?: boolean;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-[var(--foreground)]">
        {label}
      </span>

      <input
        type={type}
        value={value}
        readOnly={readOnly}
        placeholder={placeholder}
        onChange={(event) => onChange?.(event.target.value)}
        className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--foreground)] outline-none transition focus:border-[var(--primary)] read-only:opacity-70"
      />
    </label>
  );
}

function InfoRow({
  label,
  value,
}: {
  label: string;
  value?: string | number | null;
}) {
  return (
    <div className="flex flex-col gap-1 border-b border-[var(--border)] py-3 last:border-0 sm:flex-row sm:items-center sm:justify-between">
      <span className="text-sm text-[var(--muted-foreground)]">
        {label}
      </span>

      <span className="break-words text-sm font-medium text-[var(--foreground)] sm:text-right">
        {value || '—'}
      </span>
    </div>
  );
}

function formatContextLabel(value: string): string {
  return value
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/[_-]/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function isContextRecord(
  value: unknown
): value is Record<string, unknown> {
  return (
    typeof value === 'object' &&
    value !== null &&
    !Array.isArray(value)
  );
}

function ContextValue({
  value,
  depth = 0,
}: {
  value: unknown;
  depth?: number;
}) {
  if (value === null || value === undefined || value === '') {
    return (
      <p className="text-sm text-[var(--muted-foreground)]">
        Not available
      </p>
    );
  }

  if (typeof value === 'boolean') {
    return (
      <span className="text-sm font-medium text-[var(--foreground)]">
        {value ? 'Enabled' : 'Disabled'}
      </span>
    );
  }

  if (typeof value === 'string' || typeof value === 'number') {
    const date =
      typeof value === 'string' &&
      /^\d{4}-\d{2}-\d{2}T/.test(value)
        ? formatDate(value)
        : String(value);

    return (
      <span className="break-words text-sm text-[var(--foreground)]">
        {date}
      </span>
    );
  }

  if (Array.isArray(value)) {
    if (value.length === 0) {
      return (
        <p className="text-sm text-[var(--muted-foreground)]">
          No information available
        </p>
      );
    }

    const primitiveItems = value.every(
      (item) =>
        typeof item === 'string' ||
        typeof item === 'number'
    );

    if (primitiveItems) {
      return (
        <div className="flex flex-wrap gap-2">
          {value.map((item, index) => (
            <span
              key={`${String(item)}-${index}`}
              className="rounded-full border border-[var(--border)] bg-[var(--background)] px-3 py-1.5 text-xs font-medium text-[var(--foreground)]"
            >
              {String(item)}
            </span>
          ))}
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {value.map((item, index) => (
          <div
            key={index}
            className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-3"
          >
            <ContextValue value={item} depth={depth + 1} />
          </div>
        ))}
      </div>
    );
  }

  if (isContextRecord(value)) {
    const entries = Object.entries(value).filter(
      ([, item]) =>
        item !== null &&
        item !== undefined &&
        item !== ''
    );

    if (entries.length === 0) {
      return (
        <p className="text-sm text-[var(--muted-foreground)]">
          No information available
        </p>
      );
    }

    return (
      <div
        className={
          depth === 0
            ? 'grid gap-4 sm:grid-cols-2'
            : 'space-y-4'
        }
      >
        {entries.map(([key, item]) => (
          <div key={key} className="min-w-0">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--muted-foreground)]">
              {formatContextLabel(key)}
            </p>
            <ContextValue value={item} depth={depth + 1} />
          </div>
        ))}
      </div>
    );
  }

  return (
    <p className="text-sm text-[var(--muted-foreground)]">
      Not available
    </p>
  );
}

function ActiveSyllabusCard({
  value,
}: {
  value: unknown;
}) {
  if (!isContextRecord(value)) {
    return (
      <p className="text-sm text-[var(--muted-foreground)]">
        No active syllabus available.
      </p>
    );
  }

  const fileName =
    typeof value.fileName === 'string'
      ? value.fileName
      : 'Uploaded syllabus';

  const confirmedAt =
    typeof value.confirmedAt === 'string'
      ? value.confirmedAt
      : null;

  const subjectNames = Array.isArray(value.subjectNames)
    ? value.subjectNames.filter(
        (item): item is string => typeof item === 'string'
      )
    : [];

  const subjectsCount =
    typeof value.subjectsCount === 'number'
      ? value.subjectsCount
      : subjectNames.length;

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[var(--background)] text-[var(--primary)]">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.7"
              className="h-6 w-6"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M7 3.75h7l5 5v11.5H7a2 2 0 0 1-2-2v-12.5a2 2 0 0 1 2-2Z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M14 3.75v5h5M9 13h6M9 16.5h6"
              />
            </svg>
          </div>

          <div className="min-w-0">
            <p className="break-words font-semibold text-[var(--foreground)]">
              {fileName}
            </p>
            <p className="mt-1 text-xs text-[var(--muted-foreground)]">
              Active syllabus
            </p>
          </div>
        </div>

        <span className="w-fit shrink-0 rounded-full bg-green-500/10 px-3 py-1 text-xs font-semibold text-green-600">
          Confirmed
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-xl bg-[var(--background)] p-4">
          <p className="text-xs font-medium text-[var(--muted-foreground)]">
            Total subjects
          </p>
          <p className="mt-1 text-2xl font-bold text-[var(--foreground)]">
            {subjectsCount}
          </p>
        </div>

        <div className="rounded-xl bg-[var(--background)] p-4">
          <p className="text-xs font-medium text-[var(--muted-foreground)]">
            Confirmed on
          </p>
          <p className="mt-2 text-sm font-semibold text-[var(--foreground)]">
            {confirmedAt ? formatDate(confirmedAt) : '—'}
          </p>
        </div>
      </div>

      <div>
        <h4 className="mb-3 text-sm font-semibold text-[var(--foreground)]">
          Subjects included
        </h4>

        {subjectNames.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {subjectNames.map((subject, index) => (
              <span
                key={`${subject}-${index}`}
                className="rounded-full border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-xs font-medium text-[var(--foreground)]"
              >
                {subject}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-[var(--muted-foreground)]">
            Subject details are not available.
          </p>
        )}
      </div>
    </div>
  );
}

function ContextCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-[var(--border)] p-5">
      <h3 className="mb-4 text-base font-semibold text-[var(--foreground)]">
        {title}
      </h3>
      {children}
    </div>
  );
}

export default function Settings() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] =
    useState<SettingsTab>('profile');

  const [fileCategory, setFileCategory] =
    useState<FileCategory>('ALL');

  // Personal information
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [bio, setBio] = useState('');
  const [timezone, setTimezone] = useState('');

  // Career and skills
  const [primaryGoal, setPrimaryGoal] = useState('');
  const [targetSkills, setTargetSkills] = useState('');
  const [skills, setSkills] = useState('');
  const [experience, setExperience] = useState('');
  const [research, setResearch] = useState('');

  // Academic information
  const [academicStatus, setAcademicStatus] = useState('');
  const [university, setUniversity] = useState('');
  const [degreeProgram, setDegreeProgram] = useState('');
  const [domain, setDomain] = useState('');
  const [currentYear, setCurrentYear] = useState('');
  const [graduationYear, setGraduationYear] = useState('');
  const [subjects, setSubjects] = useState('');

  // Learning preferences
  const [dailyStudyHours, setDailyStudyHours] = useState('');
  const [learningDepth, setLearningDepth] = useState('');

  // Account deletion
  const [deleteDialogOpen, setDeleteDialogOpen] =
    useState(false);
  const [confirmationText, setConfirmationText] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');

  const profileQuery = useSettingsProfile();
  const contextQuery = useSettingsContext();
  const filesQuery = useSettingsFiles(fileCategory);
  const preferencesQuery = useSettingsPreferences();
  const accountQuery = useSettingsAccount();

  const updateProfile = useUpdateSettingsProfile();
  const uploadAvatar = useUploadSettingsAvatar();
  const updatePreferences = useUpdateSettingsPreferences();
  const deleteAccount = useDeleteSettingsAccount();

  const profile = profileQuery.data;
  const preferences = preferencesQuery.data;
  const account = accountQuery.data;

  // Populate all editable fields from the backend profile.
  useEffect(() => {
    if (!profile) return;

    setFullName(profile.account.fullName ?? '');
    setPhone(profile.account.phone ?? '');
    setBio(profile.account.bio ?? '');
    setTimezone(profile.account.timezone ?? '');

    setPrimaryGoal(profile.learner.primaryGoal ?? '');
    setTargetSkills(profile.learner.targetSkills?.join(', ') ?? '');
    setSkills(profile.learner.skills?.join(', ') ?? '');
    setExperience(profile.learner.experience ?? '');
    setResearch(profile.learner.research ?? '');

    setAcademicStatus(profile.academic.academicStatus ?? '');
    setUniversity(profile.academic.university ?? '');
    setDegreeProgram(profile.academic.degreeProgram ?? '');
    setDomain(profile.academic.domain ?? '');
    setCurrentYear(profile.academic.currentYear ?? '');

    setGraduationYear(
      profile.academic.graduationYear?.toString() ?? ''
    );

    setSubjects(profile.academic.subjects?.join(', ') ?? '');

    setDailyStudyHours(
      profile.learningPreferences.dailyStudyHours ?? ''
    );

    setLearningDepth(
      profile.learningPreferences.learningDepth ?? ''
    );
  }, [profile]);

  const isInitialLoading =
    profileQuery.isLoading &&
    contextQuery.isLoading &&
    preferencesQuery.isLoading &&
    accountQuery.isLoading;

  // Save all editable profile fields through one PATCH request.
  function handleProfileSave(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    const parsedGraduationYear = graduationYear.trim()
      ? Number(graduationYear)
      : null;

    if (
      parsedGraduationYear !== null &&
      (!Number.isInteger(parsedGraduationYear) ||
        parsedGraduationYear < 1900 ||
        parsedGraduationYear > 2200)
    ) {
      alert('Please enter a valid graduation year.');
      return;
    }

    updateProfile.mutate({
      account: {
        fullName: fullName.trim(),
        phone: phone.trim() || null,
        bio: bio.trim() || null,
        timezone: timezone.trim(),
      },

      learner: {
        primaryGoal: primaryGoal.trim() || null,
        targetSkills: parseCommaSeparated(targetSkills),
        skills: parseCommaSeparated(skills),
        experience: experience.trim() || null,
        research: research.trim() || null,
      },

      academic: {
        academicStatus: academicStatus.trim() || null,
        university: university.trim() || null,
        degreeProgram: degreeProgram.trim() || null,
        domain: domain.trim() || null,
        currentYear: currentYear.trim() || null,
        graduationYear: parsedGraduationYear,
        subjects: parseCommaSeparated(subjects),
      },

      learningPreferences: {
        dailyStudyHours: dailyStudyHours.trim() || null,
        learningDepth: learningDepth.trim() || null,
      },
    });
  }

  function handleAvatarChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0];

    if (!file) return;

    const allowedTypes = [
      'image/jpeg',
      'image/png',
      'image/webp',
    ];

    if (!allowedTypes.includes(file.type)) {
      alert('Please select a JPEG, PNG or WebP image.');
      event.target.value = '';
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      alert('Avatar image must be smaller than 2 MB.');
      event.target.value = '';
      return;
    }

    uploadAvatar.mutate(file);
    event.target.value = '';
  }

  async function handleFileDownload(
    category: string,
    fileId: string
  ) {
    try {
      if (
        category !== 'SYLLABUS' &&
        category !== 'BUILD_ARTIFACT' &&
        category !== 'RESUME'
      ) {
        return;
      }

      const response = await import(
        '@/services/settingsServices'
      );

      const download = await response.getSettingsFileDownload(
        category,
        fileId
      );

      if (!download.isApiExport) {
        window.open(
          download.url,
          '_blank',
          'noopener,noreferrer'
        );
        return;
      }

      const blob = await apiRequest<Blob>(
        download.url,
        { method: 'POST' },
        { responseType: 'blob' }
      );

      const objectUrl = URL.createObjectURL(blob);
      const anchor = document.createElement('a');

      anchor.href = objectUrl;
      anchor.download = download.fileName;

      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();

      URL.revokeObjectURL(objectUrl);
    } catch (error) {
      console.error('File download failed:', error);

      alert(
        error instanceof Error
          ? error.message
          : 'Unable to download this file.'
      );
    }
  }

  function handlePreferenceChange(
    key: keyof SettingsPreferencesPatch,
    value: boolean
  ) {
    updatePreferences.mutate({
      [key]: value,
    } as SettingsPreferencesPatch);
  }

  async function handleAccountDeletion(
    event: React.FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (confirmationText !== 'DELETE') return;

    const payload: DeleteAccountPayload = {
      confirmationText: 'DELETE',
    };

    if (account?.hasPasswordAuth) {
      payload.currentPassword = currentPassword;
    }

    if (account?.mfaEnabled) {
      payload.totpCode = totpCode;
    }

    try {
      await deleteAccount.mutateAsync(payload);

      // Clear client-side user data after successful deletion.
      queryClient.clear();

      useOnboardingStore.getState().resetOnboarding();
      useOnboardingStore.persist.clearStorage();
      clearOnboardingDraft();

      clearSession();

      router.replace('/login');
    } catch (error) {
      console.error('Account deletion failed:', error);

      alert(
        error instanceof Error
          ? error.message
          : 'Unable to delete your account.'
      );
    }
  }

  if (isInitialLoading) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-10">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-48 rounded-lg bg-[var(--border)]" />
          <div className="h-32 rounded-2xl bg-[var(--surface)]" />
          <div className="h-72 rounded-2xl bg-[var(--surface)]" />
        </div>
      </div>
    );
  }

  return (
    <main className="mx-auto min-h-screen w-full max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-[var(--foreground)]">
          Settings
        </h1>

        <p className="mt-2 text-sm text-[var(--muted-foreground)]">
          Manage your profile, learning preferences and account.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[230px_minmax(0,1fr)]">
        <aside className="h-fit rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-2">
          <nav className="flex gap-1 overflow-x-auto lg:flex-col">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`shrink-0 rounded-xl px-4 py-3 text-left text-sm font-medium transition ${
                  activeTab === tab.id
                    ? 'bg-[var(--primary)] text-white'
                    : 'text-[var(--muted-foreground)] hover:bg-[var(--background)] hover:text-[var(--foreground)]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </aside>

        <section className="min-w-0 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-7">
          {activeTab === 'profile' && (
            <div>
              <SectionHeading
                title="Profile"
                description="Manage your personal, academic and learning profile."
              />

              {profileQuery.isError ? (
                <p className="text-sm text-red-500">
                  Unable to load your profile.
                </p>
              ) : profile ? (
                <>
                  <div className="mb-8 flex flex-wrap items-center gap-4">
                    <div className="flex h-16 w-16 items-center justify-center overflow-hidden rounded-full bg-[var(--background)] text-xl font-semibold text-[var(--foreground)]">
                      {profile.account.avatarUrl ? (
                        <img
                          src={profile.account.avatarUrl}
                          alt="Profile avatar"
                          className="h-full w-full object-cover"
                        />
                      ) : (
                        (
                          profile.account.fullName?.[0] ?? 'U'
                        ).toUpperCase()
                      )}
                    </div>

                    <div>
                      <p className="font-semibold text-[var(--foreground)]">
                        {profile.account.fullName}
                      </p>

                      <p className="text-sm text-[var(--muted-foreground)]">
                        {profile.account.email}
                      </p>

                      <label className="mt-2 inline-block cursor-pointer text-sm font-medium text-[var(--primary)]">
                        {uploadAvatar.isPending
                          ? 'Uploading...'
                          : 'Change avatar'}

                        <input
                          type="file"
                          accept="image/jpeg,image/png,image/webp"
                          className="hidden"
                          disabled={uploadAvatar.isPending}
                          onChange={handleAvatarChange}
                        />
                      </label>

                      {uploadAvatar.isError && (
                        <p className="mt-1 text-xs text-red-500">
                          Avatar upload failed.
                        </p>
                      )}

                      {uploadAvatar.isSuccess && (
                        <p className="mt-1 text-xs text-green-600">
                          Avatar updated successfully.
                        </p>
                      )}
                    </div>
                  </div>

                  <form onSubmit={handleProfileSave}>
                    {/* Personal information */}
                    <SectionHeading
                      title="Personal information"
                      description="Update your basic account details."
                    />

                    <div className="grid gap-5 sm:grid-cols-2">
                      <Field
                        label="Full name"
                        value={fullName}
                        onChange={setFullName}
                        placeholder="Enter your full name"
                      />

                      <Field
                        label="Email address"
                        value={profile.account.email}
                        readOnly
                      />

                      <Field
                        label="Phone"
                        value={phone}
                        onChange={setPhone}
                        placeholder="Enter phone number"
                      />

                      <Field
                        label="Timezone"
                        value={timezone}
                        onChange={setTimezone}
                        placeholder="e.g. Asia/Kolkata"
                      />
                    </div>

                    <label className="mt-5 block">
                      <span className="mb-2 block text-sm font-medium text-[var(--foreground)]">
                        Bio
                      </span>

                      <textarea
                        value={bio}
                        onChange={(event) =>
                          setBio(event.target.value)
                        }
                        rows={3}
                        placeholder="Tell us about yourself..."
                        className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--foreground)] outline-none focus:border-[var(--primary)]"
                      />
                    </label>

                    {/* Career and skills */}
                    <div className="mt-9 border-t border-[var(--border)] pt-7">
                      <SectionHeading
                        title="Career and skills"
                        description="Manage your career goals, skills and experience."
                      />

                      <div className="grid gap-5 sm:grid-cols-2">
                        <Field
                          label="Primary career goal"
                          value={primaryGoal}
                          onChange={setPrimaryGoal}
                          placeholder="e.g. AI Engineer"
                        />

                        <Field
                          label="Experience"
                          value={experience}
                          onChange={setExperience}
                          placeholder="Describe your experience"
                        />

                        <Field
                          label="Target skills"
                          value={targetSkills}
                          onChange={setTargetSkills}
                          placeholder="Python, Machine Learning, React"
                        />

                        <Field
                          label="Current skills"
                          value={skills}
                          onChange={setSkills}
                          placeholder="C++, Python, SQL"
                        />
                      </div>

                      <p className="mt-2 text-xs text-[var(--muted-foreground)]">
                        Separate multiple skills with commas.
                      </p>

                      <label className="mt-5 block">
                        <span className="mb-2 block text-sm font-medium text-[var(--foreground)]">
                          Research interests
                        </span>

                        <textarea
                          value={research}
                          onChange={(event) =>
                            setResearch(event.target.value)
                          }
                          rows={3}
                          placeholder="Describe your research interests..."
                          className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--foreground)] outline-none focus:border-[var(--primary)]"
                        />
                      </label>
                    </div>

                    {/* Academic information */}
                    <div className="mt-9 border-t border-[var(--border)] pt-7">
                      <SectionHeading
                        title="Academic information"
                        description="Update your education and academic details."
                      />

                      <div className="grid gap-5 sm:grid-cols-2">
                        <Field
                          label="Academic status"
                          value={academicStatus}
                          onChange={setAcademicStatus}
                          placeholder="e.g. Undergraduate"
                        />

                        <Field
                          label="University"
                          value={university}
                          onChange={setUniversity}
                          placeholder="Enter university name"
                        />

                        <Field
                          label="Degree / Program"
                          value={degreeProgram}
                          onChange={setDegreeProgram}
                          placeholder="e.g. B.Tech Computer Science"
                        />

                        <Field
                          label="Domain"
                          value={domain}
                          onChange={setDomain}
                          placeholder="e.g. Computer Science"
                        />

                        <Field
                          label="Current year"
                          value={currentYear}
                          onChange={setCurrentYear}
                          placeholder="e.g. 3rd Year"
                        />

                        <Field
                          label="Graduation year"
                          type="number"
                          value={graduationYear}
                          onChange={setGraduationYear}
                          placeholder="e.g. 2028"
                        />

                        <Field
                          label="Subjects"
                          value={subjects}
                          onChange={setSubjects}
                          placeholder="DBMS, OS, DSA, CN"
                        />
                      </div>

                      <p className="mt-2 text-xs text-[var(--muted-foreground)]">
                        Separate multiple subjects with commas.
                      </p>
                    </div>

                    {/* Learning preferences */}
                    <div className="mt-9 border-t border-[var(--border)] pt-7">
                      <SectionHeading
                        title="Learning preferences"
                        description="Customize your preferred learning routine."
                      />

                      <div className="grid gap-5 sm:grid-cols-2">
                        <Field
                          label="Daily study hours"
                          value={dailyStudyHours}
                          onChange={setDailyStudyHours}
                          placeholder="e.g. 3 hours"
                        />

                        <Field
                          label="Learning depth"
                          value={learningDepth}
                          onChange={setLearningDepth}
                          placeholder="e.g. Detailed"
                        />
                      </div>
                    </div>

                    {/* Save all profile sections */}
                    <div className="mt-8 border-t border-[var(--border)] pt-6">
                      <button
                        type="submit"
                        disabled={updateProfile.isPending}
                        className="rounded-xl bg-[var(--primary)] px-6 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
                      >
                        {updateProfile.isPending
                          ? 'Saving changes...'
                          : 'Save all changes'}
                      </button>

                      {updateProfile.isSuccess && (
                        <p className="mt-3 text-sm text-green-600">
                          Profile updated successfully.
                        </p>
                      )}

                      {updateProfile.isError && (
                        <p className="mt-3 text-sm text-red-500">
                          Unable to update profile. Please try again.
                        </p>
                      )}
                    </div>
                  </form>

                  <div className="mt-8 border-t border-[var(--border)] pt-7">
                    <InfoRow
                      label="Onboarding status"
                      value={profile.learner.onboardingStatus}
                    />

                    <InfoRow
                      label="Registration date"
                      value={formatDate(
                        profile.account.registrationDate
                      )}
                    />

                    <InfoRow
                      label="Last login"
                      value={formatDate(profile.account.lastLogin)}
                    />
                  </div>
                </>
              ) : null}
            </div>
          )}

          {activeTab === 'context' && (
            <div>
              <SectionHeading
                title="AI Context"
                description="Information available to personalize your learning experience."
              />

              {contextQuery.isError ? (
                <p className="text-sm text-red-500">
                  Unable to load AI context.
                </p>
              ) : contextQuery.data ? (
                <div className="space-y-5">
                  <div className="rounded-xl border border-[var(--border)] p-4">
                    <InfoRow
                      label="Current plan"
                      value={contextQuery.data.planTier}
                    />

                    <InfoRow
                      label="AI personalization"
                      value={
                        contextQuery.data.aiPersonalizationEnabled
                          ? 'Enabled'
                          : 'Disabled'
                      }
                    />
                  </div>

                  {contextQuery.data.aiPersonalizationEnabled ? (
                    <div className="space-y-5">
                      <ContextCard title="Active Syllabus">
                        <ActiveSyllabusCard
                          value={contextQuery.data.activeSyllabus}
                        />
                      </ContextCard>

                      <ContextCard title="Active Roadmap">
                        {contextQuery.data.activeRoadmap ? (
                          <ContextValue
                            value={contextQuery.data.activeRoadmap}
                          />
                        ) : (
                          <p className="text-sm text-[var(--muted-foreground)]">
                            No active roadmap available.
                          </p>
                        )}
                      </ContextCard>

                      <ContextCard title="Memory Summary">
                        {contextQuery.data.memorySummary ? (
                          <ContextValue
                            value={contextQuery.data.memorySummary}
                          />
                        ) : (
                          <p className="text-sm text-[var(--muted-foreground)]">
                            No memory summary available.
                          </p>
                        )}
                      </ContextCard>
                    </div>
                  ) : (
                    <p className="rounded-xl bg-[var(--background)] p-4 text-sm text-[var(--muted-foreground)]">
                      AI personalization is disabled. Your AI context summary is not currently available.
                    </p>
                  )}
                </div>
              ) : null}
            </div>
          )}

          {activeTab === 'files' && (
            <div>
              <SectionHeading
                title="My Files"
                description="Access your uploaded documents and generated files."
              />

              <div className="mb-5 flex flex-wrap gap-2">
                {(
                  [
                    'ALL',
                    'SYLLABUS',
                    'BUILD_ARTIFACT',
                    'RESUME',
                    'ATS',
                  ] as FileCategory[]
                ).map((category) => (
                  <button
                    key={category}
                    type="button"
                    onClick={() => setFileCategory(category)}
                    className={`rounded-lg border px-3 py-2 text-xs font-medium transition ${
                      fileCategory === category
                        ? 'border-[var(--primary)] bg-[var(--primary)] text-white'
                        : 'border-[var(--border)] text-[var(--muted-foreground)] hover:bg-[var(--background)]'
                    }`}
                  >
                    {category.replace('_', ' ')}
                  </button>
                ))}
              </div>

              {filesQuery.isLoading ? (
                <p className="text-sm text-[var(--muted-foreground)]">
                  Loading files...
                </p>
              ) : filesQuery.isError ? (
                <p className="text-sm text-red-500">
                  Unable to load files.
                </p>
              ) : filesQuery.data?.files.length ? (
                <div className="space-y-3">
                  {filesQuery.data.files.map((file) => (
                    <div
                      key={file.id}
                      className="flex flex-col gap-3 rounded-xl border border-[var(--border)] p-4 sm:flex-row sm:items-center sm:justify-between"
                    >
                      <div className="min-w-0">
                        <p className="break-words font-medium text-[var(--foreground)]">
                          {file.fileName}
                        </p>

                        <p className="mt-1 text-xs text-[var(--muted-foreground)]">
                          {file.category.replace('_', ' ')}
                          {' · '}
                          {formatFileSize(file.fileSize)}
                          {' · '}
                          {formatDate(file.createdAt)}
                        </p>

                        {file.status && (
                          <p className="mt-1 text-xs text-[var(--muted-foreground)]">
                            Status: {file.status}
                          </p>
                        )}

                        {file.overallScore != null && (
                          <p className="mt-1 text-xs text-[var(--muted-foreground)]">
                            Score: {file.overallScore}
                          </p>
                        )}
                      </div>

                      {file.category !== 'ATS' && (
                        <button
                          type="button"
                          onClick={() =>
                            handleFileDownload(
                              file.category,
                              file.id
                            )
                          }
                          className="shrink-0 rounded-lg border border-[var(--border)] px-4 py-2 text-sm font-medium text-[var(--foreground)] hover:bg-[var(--background)]"
                        >
                          Download
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="rounded-xl border border-dashed border-[var(--border)] p-10 text-center">
                  <p className="font-medium text-[var(--foreground)]">
                    No files found
                  </p>

                  <p className="mt-1 text-sm text-[var(--muted-foreground)]">
                    Files in this category will appear here.
                  </p>
                </div>
              )}

              {filesQuery.data && (
                <p className="mt-4 text-xs text-[var(--muted-foreground)]">
                  {filesQuery.data.total} file(s) found
                </p>
              )}
            </div>
          )}

          {activeTab === 'preferences' && (
            <div>
              <SectionHeading
                title="Preferences"
                description="Control notifications and AI personalization."
              />

              {preferencesQuery.isError ? (
                <p className="text-sm text-red-500">
                  Unable to load preferences.
                </p>
              ) : preferences ? (
                <div className="space-y-5">
                  {(
                    [
                      {
                        key: 'emailNotifications',
                        title: 'Email notifications',
                        description:
                          'Receive important account notifications by email.',
                      },
                      {
                        key: 'studyReminders',
                        title: 'Study reminders',
                        description:
                          'Receive reminders to stay consistent with learning.',
                      },
                      {
                        key: 'productUpdates',
                        title: 'Product updates',
                        description:
                          'Get updates about new features and improvements.',
                      },
                      {
                        key: 'aiPersonalizationEnabled',
                        title: 'AI personalization',
                        description:
                          'Allow AI features to use your learning context.',
                      },
                    ] as const
                  ).map((item) => (
                    <label
                      key={item.key}
                      className="flex cursor-pointer items-center justify-between gap-4 border-b border-[var(--border)] pb-5 last:border-0"
                    >
                      <span>
                        <span className="block text-sm font-medium text-[var(--foreground)]">
                          {item.title}
                        </span>

                        <span className="mt-1 block text-xs text-[var(--muted-foreground)]">
                          {item.description}
                        </span>
                      </span>

                      <input
                        type="checkbox"
                        checked={preferences[item.key]}
                        disabled={updatePreferences.isPending}
                        onChange={(event) =>
                          handlePreferenceChange(
                            item.key,
                            event.target.checked
                          )
                        }
                        className="h-5 w-5 shrink-0 accent-[var(--primary)]"
                      />
                    </label>
                  ))}

                  {updatePreferences.isError && (
                    <p className="text-sm text-red-500">
                      Unable to update this preference.
                    </p>
                  )}

                  {updatePreferences.isSuccess && (
                    <p className="text-sm text-green-600">
                      Preferences updated.
                    </p>
                  )}
                </div>
              ) : null}
            </div>
          )}

          {activeTab === 'account' && (
            <div>
              <SectionHeading
                title="Account & Security"
                description="Review your authentication and subscription details."
              />

              {accountQuery.isError ? (
                <p className="text-sm text-red-500">
                  Unable to load account information.
                </p>
              ) : account ? (
                <>
                  <div className="rounded-xl border border-[var(--border)] p-4">
                    <InfoRow
                      label="Email"
                      value={account.email}
                    />

                    <InfoRow
                      label="Email verified"
                      value={account.emailVerified ? 'Yes' : 'No'}
                    />

                    <InfoRow
                      label="Multi-factor authentication"
                      value={
                        account.mfaEnabled ? 'Enabled' : 'Disabled'
                      }
                    />

                    <InfoRow
                      label="Password authentication"
                      value={
                        account.hasPasswordAuth
                          ? 'Enabled'
                          : 'Not enabled'
                      }
                    />

                    <InfoRow
                      label="Authentication providers"
                      value={account.authProviders?.join(', ')}
                    />
                  </div>

                  <div className="mt-6 rounded-xl border border-[var(--border)] p-4">
                    <h3 className="mb-3 font-semibold text-[var(--foreground)]">
                      Subscription
                    </h3>

                    {account.activeSubscription ? (
                      <>
                        <InfoRow
                          label="Current plan"
                          value={
                            account.activeSubscription.currentPlan
                          }
                        />

                        <InfoRow
                          label="Billing cycle"
                          value={
                            account.activeSubscription.billingCycle
                          }
                        />

                        <InfoRow
                          label="Status"
                          value={account.activeSubscription.status}
                        />

                        <InfoRow
                          label="Current period ends"
                          value={formatDate(
                            account.activeSubscription.currentPeriodEnd
                          )}
                        />

                        <InfoRow
                          label="Days remaining"
                          value={
                            account.activeSubscription.daysRemaining
                          }
                        />
                      </>
                    ) : (
                      <p className="text-sm text-[var(--muted-foreground)]">
                        No active subscription information available.
                      </p>
                    )}
                  </div>

                  <div className="mt-8 rounded-xl border border-red-500/30 p-5">
                    <h3 className="font-semibold text-red-500">
                      Delete account
                    </h3>

                    <p className="mt-2 text-sm text-[var(--muted-foreground)]">
                      Permanently delete your account and associated data. This action cannot be undone.
                    </p>

                    <button
                      type="button"
                      onClick={() => setDeleteDialogOpen(true)}
                      className="mt-4 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-700"
                    >
                      Delete my account
                    </button>
                  </div>
                </>
              ) : null}
            </div>
          )}
        </section>
      </div>

      {deleteDialogOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-md rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-xl">
            <h2 className="text-xl font-bold text-red-500">
              Delete account permanently?
            </h2>

            <p className="mt-2 text-sm text-[var(--muted-foreground)]">
              This action is permanent. Type DELETE to confirm.
            </p>

            <form
              onSubmit={handleAccountDeletion}
              className="mt-5 space-y-4"
            >
              <Field
                label='Type "DELETE" to confirm'
                value={confirmationText}
                onChange={setConfirmationText}
                placeholder="DELETE"
              />

              {account?.hasPasswordAuth && (
                <Field
                  label="Current password"
                  type="password"
                  value={currentPassword}
                  onChange={setCurrentPassword}
                  placeholder="Enter your current password"
                />
              )}

              {account?.mfaEnabled && (
                <Field
                  label="Authenticator code"
                  value={totpCode}
                  onChange={setTotpCode}
                  placeholder="Enter your TOTP code"
                />
              )}

              {deleteAccount.isError && (
                <p className="text-sm text-red-500">
                  {deleteAccount.error instanceof Error
                    ? deleteAccount.error.message
                    : 'Account deletion failed.'}
                </p>
              )}

              <div className="flex flex-wrap justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setDeleteDialogOpen(false);
                    setConfirmationText('');
                    setCurrentPassword('');
                    setTotpCode('');
                  }}
                  className="rounded-lg border border-[var(--border)] px-4 py-2.5 text-sm font-medium text-[var(--foreground)]"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={
                    confirmationText !== 'DELETE' ||
                    (account?.hasPasswordAuth && !currentPassword) ||
                    (account?.mfaEnabled && !totpCode) ||
                    deleteAccount.isPending
                  }
                  className="rounded-lg bg-red-600 px-4 py-2.5 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {deleteAccount.isPending
                    ? 'Deleting...'
                    : 'Confirm deletion'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}
