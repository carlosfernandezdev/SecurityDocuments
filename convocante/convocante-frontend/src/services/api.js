// src/services/api.js
const BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8001/convocante'
const SECRET = import.meta.env.VITE_SHARED_SECRET || 'SHARED_SECRET'

async function http(method, url, body, isJson = true) {
  const init = { method, headers: {} }
  if (body && !(body instanceof FormData)) {
    init.headers['Content-Type'] = 'application/json'
    init.body = JSON.stringify(body)
  } else if (body instanceof FormData) {
    init.body = body
  }
  const res = await fetch(`${BASE}${url}`, init)
  if (!res.ok) {
    let errText
    try { errText = await res.text() } catch { errText = `${res.status}` }
    throw new Error(errText)
  }
  return isJson ? res.json() : res.text()
}

export const api = {
  base: BASE,
  secret: SECRET,

  createCall: (call_id) => http('POST', '/api/calls', { call_id }),
  listCalls: () => http('GET', '/api/calls'),
  downloadPubKey: async (key_id) => {
    const res = await fetch(`${BASE}/api/keys/${encodeURIComponent(key_id)}/rsa_pub.pem`)
    if (!res.ok) throw new Error('No se pudo descargar la clave pública')
    return res.text()
  },

  // Recepción (solo para pruebas locales)
  submitProposalParts: (files) => {
    const form = new FormData()
    form.append('meta', files.meta)
    form.append('payload', files.payload)
    form.append('wrapped_key', files.wrapped_key)
    form.append('nonce', files.nonce)
    form.append('tag', files.tag)
    return http('POST', `/internal/receive-proposal?secret=${encodeURIComponent(SECRET)}`, form)
  },

  // Submissions
  listSubmissions: (call_id) => http('GET', `/api/calls/${encodeURIComponent(call_id)}/submissions`),
  downloadSubmissionFileUrl: (call_id, submission_id, filename) =>
    `${BASE}/api/calls/${encodeURIComponent(call_id)}/submissions/${encodeURIComponent(submission_id)}/files/${encodeURIComponent(filename)}`,

  // Contenido
  listContentFiles: (call_id, submission_id) =>
    http('GET', `/api/calls/${encodeURIComponent(call_id)}/submissions/${encodeURIComponent(submission_id)}/content`),

  downloadContentFileUrl: (call_id, submission_id, relPath) =>
    `${BASE}/api/calls/${encodeURIComponent(call_id)}/submissions/${encodeURIComponent(submission_id)}/content/${encodeURIComponent(relPath)}`,
}

/** Seleccionar ganador (aceptado) y rechazar el resto */
export const selectWinner = async (callId, submissionId, notes = '') => {
  // Reutilizamos api.base (ya incluye /convocante)
  const params = new URLSearchParams({ call_id: callId, submission_id: submissionId, notes })
  const r = await fetch(`${api.base}/api/decisions/select`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString(),
  })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}
