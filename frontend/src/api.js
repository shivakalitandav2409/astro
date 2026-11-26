const TOKEN_KEY = "astro_unified_token";
const API_BASE = (import.meta.env.VITE_API_BASE || "").replace(/\/$/, "");

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

export function setStoredToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  constructor(status, detail) {
    const msg =
      typeof detail === "string"
        ? detail
        : detail?.message || JSON.stringify(detail || "Request failed");
    super(msg);
    this.status = status;
    this.detail = detail;
  }
}

export async function apiFetch(path, options = {}) {
  const token = getStoredToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (token && !headers.Authorization) {
    headers.Authorization = `Bearer ${token}`;
  }
  const resp = await fetch(`${API_BASE}/api${path}`, {
    ...options,
    headers,
  });
  const contentType = resp.headers.get("content-type") || "";
  if (contentType.includes("application/pdf")) {
    if (!resp.ok) throw new ApiError(resp.status, "Failed to download PDF");
    return await resp.blob();
  }
  let data = null;
  if (contentType.includes("application/json")) {
    data = await resp.json();
  } else {
    data = await resp.text();
  }
  if (!resp.ok) {
    throw new ApiError(resp.status, data?.detail ?? data);
  }
  return data;
}
