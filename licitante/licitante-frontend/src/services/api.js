const BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8002/licitante';

async function http(method, url, body, isJson = true) {
  const init = { method, headers: {} };
  if (body && !(body instanceof FormData)) {
    init.headers['Content-Type'] = 'application/json';
    init.body = JSON.stringify(body);
  } else if (body instanceof FormData) {
    init.body = body;
  }
  const res = await fetch(`${BASE}${url}`, init);
  if (!res.ok) {
    let t;
    try { t = await res.text(); } catch { t = `${res.status}`; }
    throw new Error(t);
  }
  return isJson ? res.json() : res.text();
}

export const getUserNotices = async (user, callId = "") => {
  const r = await fetch(`${BASE}/${encodeURIComponent(user)}/api/notifications${callId ? `?call_id=${encodeURIComponent(callId)}` : ""}`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
};

export const getCallSummary = async (callId) => {
  const r = await fetch(`${BASE}/api/notifications/by-call/${encodeURIComponent(callId)}`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
};
export const getAccounts = async () => {
  const r = await fetch(`${BASE}/api/accounts`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
};

export const setActiveAccount = async (user) => {
  const r = await fetch(`${BASE}/api/accounts/active`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
};
export const api = {
  base: BASE,
  // Convocatorias
  listCalls: () => http('GET', '/api/calls'),
  // Envío de propuestas
  submitSealed: (file) => { const f=new FormData(); f.append('sealed', file); return http('POST','/api/submit',f); },
  submitParts: (files) => { const f=new FormData(); for (const k of ['meta','payload','wrapped_key','nonce','tag']) f.append(k, files[k]); return http('POST','/api/submit',f); },
  listSubmissions: (call_id) => http('GET', `/api/submissions${call_id?`?call_id=${encodeURIComponent(call_id)}`:''}`),

  // Notificaciones (filtradas por licitante si se indica)
  listNotifications: (bidder_id) => (
    bidder_id
      ? http('GET', `/api/notifications/selection?bidder_id=${encodeURIComponent(bidder_id)}`)
      : http('GET', '/api/notifications/selection')
  ),

  // Cuentas (registro y listado)
  createAccount: (bidder_id, password) => http('POST', '/api/accounts', { bidder_id, password }),
  listAccounts: () => http('GET', '/api/accounts'),
};
