const API_BASE: string = import.meta.env.VITE_API_URL ?? "/api";

const TOKEN_KEY = "bditagui_token";
const USER_KEY = "bditagui_user";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setSession(token: string, user: unknown): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getStoredUser<T>(): T | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
}

function sesionExpirada(): void {
  clearSession();
  window.dispatchEvent(new Event("auth-expired"));
}

function cabecerasAutenticadas(): Record<string, string> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function mensajeDeError(response: Response): Promise<string> {
  let detail: unknown = response.statusText;
  try {
    const data = await response.json();
    detail = data.detail ?? data;
  } catch {
    /* cuerpo no JSON */
  }
  return Array.isArray(detail)
    ? detail.map((d) => (typeof d === "string" ? d : d.msg)).join("; ")
    : String(detail);
}

async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const { method = "GET", body } = opts;

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: cabecerasAutenticadas(),
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 401) sesionExpirada();

  if (!response.ok) {
    throw new ApiError(response.status, await mensajeDeError(response));
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export async function descargarCSV(
  path: string,
  nombreArchivo: string,
): Promise<void> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: cabecerasAutenticadas(),
  });

  if (response.status === 401) sesionExpirada();

  if (!response.ok) {
    throw new ApiError(response.status, await mensajeDeError(response));
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = nombreArchivo;
  enlace.click();
  URL.revokeObjectURL(url);
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PUT", body }),
  del: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
