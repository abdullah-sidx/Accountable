/**
 * apiClient — fetch-based configuration targeting the Python (FastAPI) backend.
 * Base URL: http://localhost:8000
 */

export const API_BASE_URL =
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_API_BASE_URL) ||
  "http://localhost:8000";

const TOKEN_KEY = "accountable.token";

export function getAuthToken() {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setAuthToken(token) {
  if (typeof window === "undefined") return;
  try {
    if (token) window.localStorage.setItem(TOKEN_KEY, token);
    else window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage unavailable */
  }
}

export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

async function request(path, { method = "GET", body, headers = {}, signal } = {}) {
  const isFormData = typeof FormData !== "undefined" && body instanceof FormData;
  const token = getAuthToken();

  const res = await fetch(`${API_BASE_URL}${path}`, {
    method,
    signal,
    headers: {
      Accept: "application/json",
      ...(isFormData || body == null ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: isFormData ? body : body == null ? undefined : JSON.stringify(body),
  });

  const text = await res.text();
  let payload = null;
  try {
    payload = text ? JSON.parse(text) : null;
  } catch {
    payload = text;
  }

  if (!res.ok) {
    throw new ApiError(payload?.detail || `Request failed (${res.status})`, res.status, payload);
  }
  return payload;
}

export const apiClient = {
  get: (path, options) => request(path, { ...options, method: "GET" }),
  post: (path, body, options) => request(path, { ...options, method: "POST", body }),
  patch: (path, body, options) => request(path, { ...options, method: "PATCH", body }),
  delete: (path, options) => request(path, { ...options, method: "DELETE" }),
};

/* ---------- Domain endpoints ---------- */

export const issuesApi = {
  list: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiClient.get(`/api/issues${qs ? `?${qs}` : ""}`);
  },
  heatmap: () => apiClient.get("/api/issues/heatmap"),
  createSnapTag: (formData) => apiClient.post("/api/issues/snaptag", formData),
};

export const fundsApi = {
  trail: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiClient.get(`/api/funds/trail${qs ? `?${qs}` : ""}`);
  },
};

export const gamificationApi = {
  profile: (userId = "me") => apiClient.get(`/api/gamification/${userId}`),
  certificateUrl: (userId = "me") => `${API_BASE_URL}/api/gamification/${userId}/certificate`,
};

export default apiClient;
