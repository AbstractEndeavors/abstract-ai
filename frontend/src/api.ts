import type { AppState, Progress } from './types';

const BASE = '/api';

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}

async function del<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`DELETE ${path} failed: ${res.status}`);
  return res.json() as Promise<T>;
}

export function fetchState(): Promise<AppState> {
  return get<AppState>('/state');
}

export function patchState(fields: Partial<AppState>): Promise<AppState> {
  return post<AppState>('/state', fields);
}

export function fetchModels(): Promise<{ models: string[] }> {
  return get<{ models: string[] }>('/models');
}

export function selectModel(model_name: string): Promise<unknown> {
  return post('/model/select', { model_name });
}

export function submitQuery(): Promise<unknown> {
  return post('/submit');
}

export function fetchProgress(): Promise<Progress> {
  return get<Progress>('/progress');
}

export function clearRequests(): Promise<unknown> {
  return post('/clear/requests');
}

export function clearChunks(): Promise<unknown> {
  return post('/clear/chunks');
}

export function addUrl(url: string): Promise<unknown> {
  return post('/urls/add', { url });
}

export function deleteUrl(url: string): Promise<unknown> {
  return del('/urls', { url });
}

export function fetchUrl(url: string, type: 'soup' | 'source'): Promise<{ content: string }> {
  return post<{ content: string }>('/urls/fetch', { url, type });
}

export function navTracker(key: string, value: number): Promise<unknown> {
  return post('/nav/tracker', { key, value });
}

export function generateReadme(): Promise<unknown> {
  return post('/generate/readme');
}
