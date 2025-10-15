import { useState } from 'react'
import { api } from '../services/api.js'

export default function SubmissionTester() {
  const [files, setFiles] = useState({
    meta: null, payload: null, wrapped_key: null, nonce: null, tag: null
  })
  const [running, setRunning] = useState(false)
  const [res, setRes] = useState(null)
  const [err, setErr] = useState('')

  const onPick = (key) => (e) => {
    setFiles((prev) => ({ ...prev, [key]: e.target.files[0] || null }))
  }

  const canSend = ['meta', 'payload', 'wrapped_key', 'nonce', 'tag'].every(k => files[k])

  const submit = async () => {
    setRunning(true); setErr(''); setRes(null)
    try {
      const r = await api.submitProposalParts(files)
      setRes(r)
    } catch (e) {
      setErr(e?.message || 'Error enviando')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div>
      <div className="grid">
        <div>
          <label>meta.json</label>
          <input type="file" accept=".json,application/json" onChange={onPick('meta')} />
        </div>
        <div>
          <label>payload.enc</label>
          <input type="file" onChange={onPick('payload')} />
        </div>
        <div>
          <label>wrapped_key.bin</label>
          <input type="file" onChange={onPick('wrapped_key')} />
        </div>
        <div>
          <label>nonce.bin</label>
          <input type="file" onChange={onPick('nonce')} />
        </div>
        <div>
          <label>tag.bin</label>
          <input type="file" onChange={onPick('tag')} />
        </div>
      </div>

      <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
        <button className="btn" onClick={submit} disabled={!canSend || running}>
          {running ? 'Enviando…' : 'Enviar a /internal/receive-proposal'}
        </button>
        <span className="muted">Usa el secret configurado en <code>VITE_SHARED_SECRET</code>.</span>
      </div>

      {err && <div className="alert error" style={{ marginTop: 10 }}>{err}</div>}
      {res && (
        <div className="card" style={{ marginTop: 12 }}>
          <h3>Respuesta</h3>
          <pre className="code" style={{ whiteSpace: 'pre-wrap' }}>
            {JSON.stringify(res, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
