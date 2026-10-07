export type SyllabusStatus =
  | 'PROCESSING'
  | 'WAITING_FOR_CONFIRMATION'
  | 'CONFIRMED'
  | 'FAILED';

export interface SyllabusUploadPayload {
  file: File;
}

export interface SyllabusUploadResponse {
  id: string;
  status: SyllabusStatus;
}

export interface SyllabusStatusResponse {
  id: string;
  status: SyllabusStatus;
}

export interface SyllabusSubject {
  name: string;
  topics: string[];
}

export interface ParsedSyllabusContent {
  subjects: SyllabusSubject[];
}

export interface Syllabus {
  id: string;
  status: SyllabusStatus;
  parsed_content?: ParsedSyllabusContent | null;
}

export interface SyllabusUpdatePayload {
  parsed_content: ParsedSyllabusContent;
}

export interface SyllabusMessageResponse {
  message: string;
  status?: SyllabusStatus;
}