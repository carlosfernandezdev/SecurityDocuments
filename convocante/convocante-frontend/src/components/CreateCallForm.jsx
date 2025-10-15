import { useState } from 'react'
import { api } from '../services/api.js'

export default function CreateCallForm({ onCreated }) {
  const [callId, setCallId] = useState('')
  const [creating, setCreating] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    if (!callId.trim()) return
    setCreating(true); setError(''); setResult(null)
    try {
      const r = await api.createCall(callId.trim())
      setResult(r)
      setCallId('')
      onCreated?.()
    } catch (e) {
      setError(e?.message || 'Error creando la convocatoria')
    } finally {
      setCreating(false)
    }
  }

  return (
    <form onSubmit={submit}>
      <label htmlFor="callId">ID de convocatoria (call_id)</label>
      <input
        id="callId"
        type="text"
        placeholder="OBRA-001"
        value={callId}
        onChange={(e)=>setCallId(e.target.value)}
      />
      <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
        <button className="btn" type="submit" disabled={creating}>
          {creating ? 'Creando…' : 'Crear'}
        </button>
        {error && <span className="alert error" style={{ margin: 0 }}>{error}</span>}
      </div>
      {result && (
        <div style={{ marginTop: 12 }}>
          <div className="badge">Creada</div>
          <div className="code" style={{ marginTop: 6 }}>
            call_id: <b>{result.call_id}</b><br/>
            key_id:&nbsp; <b>{result.key_id}</b><br/>
            pública:&nbsp; <code>{result.rsa_pub_endpoint}</code>
          </div>
        </div>
      )}
    </form>
  )
}
