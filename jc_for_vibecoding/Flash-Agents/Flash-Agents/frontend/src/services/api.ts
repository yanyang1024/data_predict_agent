import { persist } from '../utils/persist';
import type { SseEvent } from '../types';

export const API_BASE = import.meta.env.VITE_API_BASE || '/api';

export class ApiError extends Error {
  status: number;
  payload: unknown;
  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.status = status;
    this.payload = payload;
  }
}

export function getToken() {
  return persist.get<string | null>('jwt', null);
}

export function setToken(token: string | null) {
  if (token) persist.set('jwt', token);
  else persist.remove('jwt');
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers || {});
  const token = getToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (!(init.body instanceof FormData) && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');

  const resp = await fetch(`${API_BASE}${path}`, { ...init, headers });
  const text = await resp.text();
  const payload = text ? safeJson(text) : null;
  if (!resp.ok) {
    const message = typeof payload === 'object' && payload && 'detail' in payload ? String((payload as any).detail) : `HTTP ${resp.status}`;
    if (resp.status === 403) throw new ApiError(`没有权限访问当前资源：${message}`, resp.status, payload);
    throw new ApiError(message, resp.status, payload);
  }
  return payload as T;
}

function safeJson(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function parseSseFrame(frame: string): SseEvent | null {
  let event = 'message';
  const data: string[] = [];
  for (const line of frame.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim();
    if (line.startsWith('data:')) data.push(line.slice(5).trimStart());
  }
  if (data.length === 0) return null;
  const raw = data.join('\n');
  return { event, data: safeJson(raw) };
}

export async function streamSse(
  path: string,
  body: unknown,
  onEvent: (event: SseEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const token = getToken();
  const resp = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    signal
  });
  if (!resp.ok || !resp.body) throw new ApiError(`SSE failed: ${resp.status}`, resp.status, await resp.text());
  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    buffer = buffer.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    const frames = buffer.split('\n\n');
    buffer = frames.pop() || '';
    for (const frame of frames) {
      const parsed = parseSseFrame(frame.trim());
      if (parsed) onEvent(parsed);
    }
  }
  buffer += decoder.decode();
  const parsed = parseSseFrame(buffer.trim());
  if (parsed) onEvent(parsed);
}

export function createEventSource(path: string, onEvent: (event: SseEvent) => void): EventSource {
  const token = getToken();
  const source = new EventSource(`${API_BASE}${path}${path.includes('?') ? '&' : '?'}token=${encodeURIComponent(token || '')}`);
  const events = ['conversation.bound', 'assistant.delta', 'reasoning', 'todo.update', 'tool.start', 'tool.end', 'question', 'done', 'error', 'aborted'];
  for (const name of events) {
    source.addEventListener(name, (evt) => onEvent({ event: name, data: safeJson((evt as MessageEvent).data) }));
  }
  return source;
}
