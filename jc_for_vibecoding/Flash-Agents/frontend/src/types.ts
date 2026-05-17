export type Domain = 'RD' | 'MEC' | 'IT' | string;

export interface User {
  id: number;
  external_id: string;
  email: string;
  display_name: string;
  domain: Domain;
  employee_no?: number | null;
  roles: { roles?: string[] };
  is_admin: boolean;
}

export interface TokenOut {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
  user: User;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  category: string;
  domains: string[];
  skills: string[];
  icon: string;
  system_prompt: string;
}

export interface Conversation {
  id: string;
  user_id: number;
  domain: string;
  agent_id: string;
  title: string;
  opencode_session_id?: string | null;
  workspace_path: string;
  status: 'idle' | 'running' | 'error' | string;
  last_error?: string | null;
  meta: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface TodoItem {
  id: string;
  text: string;
  status: 'todo' | 'running' | 'done' | 'error' | string;
}

export interface ToolCall {
  id: string;
  name: string;
  status: 'running' | 'done' | 'error';
  input?: unknown;
  output?: unknown;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: number;
  status?: 'streaming' | 'done' | 'error';
  reasoning?: string[];
  tools?: ToolCall[];
  questions?: Array<{ id: string; text: string; options?: string[] }>;
}

export interface SseEvent<T = any> {
  event: string;
  data: T;
}

export interface WorkspaceFile {
  path: string;
  name: string;
  type: 'file' | 'dir';
  size: number;
  updated_at?: string | null;
}

export interface Skill {
  id: number | string;
  name: string;
  version: string;
  source: string;
  domain: string;
  entrypoint: string;
  enabled: boolean;
  manifest: Record<string, unknown>;
}
