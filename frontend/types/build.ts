
export type ProjectType =
  | 'CODING'
  | 'RESEARCH'
  | 'BUSINESS'
  | 'ANALYSIS'
  | 'DESIGN'
  | 'OTHER';

export type ProjectStatus =
  | 'DRAFT'
  | 'ACTIVE'
  | 'COMPLETED'
  | 'ARCHIVED';

export type MilestoneStatus =
  | 'PENDING'
  | 'IN_PROGRESS'
  | 'COMPLETED';

export type TaskStatus =
  | 'PENDING'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'BLOCKED';

export type ArtifactType =
  | 'DOCUMENT'
  | 'UPLOAD'
  | 'DELIVERABLE'
  | 'PRESENTATION'
  | 'EVIDENCE';

export interface Project {
  id: string;
  learnerId?: string;
  title: string;
  description?: string | null;
  type: ProjectType;
  domain?: string | null;
  goal?: string | null;
  skills: string[];
  status: ProjectStatus;
  createdAt: string;
  updatedAt: string;
}

export interface Milestone {
  id: string;
  projectId: string;
  title: string;
  description?: string | null;
  status: MilestoneStatus;
  orderIdx: number;
  createdAt: string;
}

export interface Task {
  id: string;
  projectId: string;
  milestoneId?: string | null;
  title: string;
  description?: string | null;
  status: TaskStatus;
  orderIdx: number;
  createdAt: string;
  updatedAt: string;
}

export interface ArtifactVersion {
  id: string;
  artifactId: string;
  version: number;
  fileName?: string | null;
  fileSize?: number | null;
  storageKey?: string | null;
  createdAt: string;
}

export interface Artifact {
  id: string;
  projectId: string;
  title: string;
  description?: string | null;
  type: ArtifactType;
  createdAt: string;
  updatedAt: string;
  versions?: ArtifactVersion[] | null;
}

export interface Evidence {
  id: string;
  projectId: string;
  artifactId?: string | null;
  title: string;
  description?: string | null;
  skills: string[];
  createdAt: string;
}

export interface RecommendedProject {
  title: string;
  description: string;
  type: ProjectType;
  skills: string[];
}

export interface BuildCoachRequest {
  intent: string;
  message: string;
  context?: Record<string, unknown>;
}

export interface BuildCoachResponse {
  reply: string;
  suggestions?: string[] | null;
  actionItems?: Record<string, unknown>[] | null;
}

export interface BuildState {
  projects: Project[];
  milestones: Milestone[];
  tasks: Task[];
  artifacts: Artifact[];
  evidence: Evidence[];
}

export interface CreateProjectInput {
  title: string;
  description?: string;
  type: ProjectType;
  domain?: string;
  goal?: string;
  skills: string[];
}

export type UpdateProjectInput = Partial<CreateProjectInput> & {
  status?: ProjectStatus;
};

export interface CreateMilestoneInput {
  projectId: string;
  title: string;
  description?: string;
  status?: MilestoneStatus;
  orderIdx?: number;
}

export type UpdateMilestoneInput = Partial<
  Pick<Milestone, 'title' | 'description' | 'status' | 'orderIdx'>
>;

export interface CreateTaskInput {
  projectId: string;
  milestoneId?: string;
  title: string;
  description?: string;
  status?: TaskStatus;
  orderIdx?: number;
}

export interface UpdateTaskInput {
  milestoneId?: string | null;
  title?: string;
  description?: string;
  status?: TaskStatus;
  orderIdx?: number;
}

export interface CreateArtifactInput {
  projectId: string;
  title: string;
  description?: string;
  type: ArtifactType;
  fileName?: string;
  fileSize?: number;
  storageKey?: string;
}

export interface CreateArtifactVersionInput {
  fileName?: string;
  fileSize?: number;
  storageKey?: string;
}

export interface CreateEvidenceInput {
  projectId: string;
  artifactId?: string;
  title: string;
  description?: string;
  skills: string[];
}
