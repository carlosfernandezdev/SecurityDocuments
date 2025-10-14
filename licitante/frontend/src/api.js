// =======================================================
// api.js — Opción A: usar SOLO el backend del LICITANTE
// =======================================================

// Puedes dejarlo hardcodeado o usar .env; dejo ambos:
export const LICITANTE_BASE =
  (import.meta?.env?.VITE_LICITANTE_BASE ?? "http://127.0.0.1:8002").replace(/\/$/, "");
export const LICITANTE_API = `${LICITANTE_BASE}/api`;

// =======================================================
// Helpers de red
// =======================================================
async function fetchJSON(url, opts = {}, dbg = {}) {
  const r = await fetch(url, { ...opts });
  const text = await r.text().catch(() => "");
  if (!r.ok) {
    throw new Error(`[${dbg.label || "fetch"}] ${r.status} ${r.statusText}: ${text}`);
  }
  const ct = r.headers.get("content-type") || "";
  return ct.includes("application/json") ? JSON.parse(text || "null") : null;
}

function toFormData(obj = {}) {
  const fd = new FormData();
  Object.entries(obj).forEach(([k, v]) => {
    if (v === undefined || v === null) return;
    // Si viene un Blob/File lo añade tal cual, si no stringifica
    if (v instanceof Blob || v instanceof File) {
      fd.append(k, v, v.name || `${k}.bin`);
    } else {
      fd.append(k, String(v));
    }
  });
  return fd;
}

// =======================================================
// Normalizadores
// =======================================================
function normalizeCalls(raw) {
  const calls = Array.isArray(raw?.calls) ? raw.calls : [];
  return calls.map((c) => ({
    id: c.call_id ?? c.id,
    key_id: c.key_id ?? "default",
    created_at: c.created_at ?? null,
    // El push del convocante suele traer esta URL ABSOLUTA.
    // Si por alguna razón llega relativa, la dejamos pasar (la UI decide cómo abrirla).
    rsa_pub_pem_url: c.rsa_pub_pem_url ?? null,
    _raw: c,
  }));
}

// Para la UI: no transformamos (Opción A = solo licitante). Si la URL es absoluta, OK.
// Si viniera relativa por alguna razón, la UI puede mostrarla tal cual.
export function resolveRsaPubUrl(call) {
  return call?.rsa_pub_pem_url || null;
}

// =======================================================
// API del Licitante — Convocatorias y Submissions
// =======================================================

// Lista de convocatorias guardadas en el licitante (push del convocante)
export async function listCalls() {
  const data = await fetchJSON(`${LICITANTE_API}/calls`, {}, { label: "listCalls" });
  return normalizeCalls(data || {});
}

// Listar submissions del usuario (si el backend expone esta ruta)
export async function listSubmissions(user) {
  const u = encodeURIComponent(user);
  const data = await fetchJSON(`${LICITANTE_API}/submissions?user=${u}`, {}, { label: "listSubmissions" });
  return Array.isArray(data?.submissions) ? data.submissions : [];
}

// Enviar propuesta como sealed.zip (recomendado)
export async function submitSealedZip({ user, file /* File | Blob */ }) {
  if (!file) throw new Error("Falta sealed.zip");
  const fd = new FormData();
  fd.append("user", user);
  fd.append("sealed", file, file.name || "sealed.zip");
  const data = await fetchJSON(`${LICITANTE_API}/submit`, { method: "POST", body: fd }, { label: "submitSealedZip" });
  return data;
}

// Enviar propuesta en piezas (meta.json, payload.enc, wrapped_key.bin, nonce.bin, tag.bin)
export async function submitPieces({ user, meta, payload, wrapped_key, nonce, tag }) {
  const fd = new FormData();
  fd.append("user", user);
  if (!(meta && payload && wrapped_key && nonce && tag)) {
    throw new Error("Faltan archivos: meta, payload, wrapped_key, nonce, tag");
  }
  fd.append("meta", meta, meta.name || "meta.json");
  fd.append("payload", payload, payload.name || "payload.enc");
  fd.append("wrapped_key", wrapped_key, wrapped_key.name || "wrapped_key.bin");
  fd.append("nonce", nonce, nonce.name || "nonce.bin");
  fd.append("tag", tag, tag.name || "tag.bin");
  const data = await fetchJSON(`${LICITANTE_API}/submit`, { method: "POST", body: fd }, { label: "submitPieces" });
  return data;
}

// =======================================================
// Health / utilidades
// =======================================================
export async function getHealth() {
  return fetchJSON(`${LICITANTE_BASE}/health`, {}, { label: "health" });
}

// WebSocket del licitante para eventos (e.g., "submitted")
export function wsUrlFor(user) {
  const base = LICITANTE_BASE.replace(/^http/i, "ws");
  const u = encodeURIComponent(user);
  return `${base}/ws?user=${u}`;
}

// =======================================================
// (Opcional) helpers de UI / formato
// =======================================================
export function formatIso(ts) {
  if (!ts) return "-";
  try {
    const d = new Date(ts);
    if (isNaN(d.getTime())) return String(ts);
    return d.toLocaleString();
  } catch {
    return String(ts);
  }
}
