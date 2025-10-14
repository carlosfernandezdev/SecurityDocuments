// Base del backend (por ejemplo: http://127.0.0.1:8001)
export const BASE = import.meta.env.VITE_CONVOCANTE_BASE ?? "http://127.0.0.1:8001";

// Prefijo real en tu backend: /convocante/api/...
export const API = `${BASE}/convocante/api`;

// Helpers
function j(path) {
  return `${API}${path.startsWith("/") ? "" : "/"}${path}`;
}
function withIds(path, ...segments) {
  const base = j(path);
  const rest = segments.map(s => encodeURIComponent(String(s))).join("/");
  return base.endsWith("/") ? `${base}${rest}` : `${base}/${rest}`;
}

/* ---------------- Calls ---------------- */
// Lista todas las convocatorias: GET /convocante/api/calls  -> { ok, calls: [...] }
export async function listCalls() {
  const r = await fetch(j("/calls"));
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

// Crea convocatoria: POST /convocante/api/calls/create?call_id=...&key_id=...
// OJO: El backend espera parámetros por QUERY, no JSON/body.
export async function createCall({ call_id, key_id = "default" }) {
  const url = `${j("/calls/create")}?call_id=${encodeURIComponent(call_id)}&key_id=${encodeURIComponent(key_id)}`;
  const r = await fetch(url, { method: "POST" });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

// Detalle de una convocatoria: GET /convocante/api/calls/{call_id} -> { ok, call: {...} }
export async function getCall(call_id) {
  const r = await fetch(withIds("/calls", call_id));
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

/* ---------------- Public key helpers ---------------- */
// Convocatoria activa (última): GET /convocante/api/active-call
export async function getActiveCall() {
  const r = await fetch(j("/active-call"));
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

// Llave pública de un call específico: GET /convocante/api/call/{call_id}
export async function getPublicCall(call_id) {
  const r = await fetch(withIds("/call", call_id));
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

/* ---------------- Submissions ---------------- */
// Nota: No hay endpoint para LISTAR submissions en el backend; sólo lectura individual.
export async function getSubmission(call_id, submission_id) {
  const r = await fetch(withIds("/calls", call_id, "submission", submission_id));
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
