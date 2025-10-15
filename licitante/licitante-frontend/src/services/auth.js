const KEY = "licitante_auth_v1";

export function saveAuth({ bidder_id, password }) {
  localStorage.setItem(KEY, JSON.stringify({ bidder_id, password }));
}

export function loadAuth() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const obj = JSON.parse(raw);
    if (!obj?.bidder_id) return null;
    return obj;
  } catch {
    return null;
  }
}

export function clearAuth() {
  localStorage.removeItem(KEY);
}
