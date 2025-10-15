// src/components/CallsTable.jsx
import { useState } from 'react'
import { api } from '../services/api.js'
import SubmissionsByCall from './SubmissionsByCall.jsx'

export default function CallsTable({ items }) {
  const [downloading, setDownloading] = useState('')
  const [pem, setPem] = useState('')
  const [err, setErr] = useState('')
  const [openCall, setOpenCall] = useState('')

  const download = async (key_id) => {
    setErr('')
    setPem('')
    setDownloading(key_id)
    try {
      const text = await api.downloadPubKey(key_id)
      setPem(text)
    } catch (e) {
      setErr(e?.message || 'Error descargando')
    } finally {
      setDownloading('')
    }
  }

  return (
    <>
      <table className="table">
        <thead>
          <tr>
            <th>call_id</th>
            <th>key_id</th>
            <th style={{width: 280}}>acciones</th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 && (
            <tr><td colSpan={3} className="muted">Sin convocatorias</td></tr>
          )}
          {items.map((c) => (
            <tr key={`${c.call_id}-${c.key_id}`}>
              <td className="code">{c.call_id}</td>
              <td className="code">{c.key_id}</td>
              <td style={{ display: 'flex', gap: 8 }}>
                <button
                  className="btn"
                  onClick={() => download(c.key_id)}
                  disabled={downloading === c.key_id}
                >
                  {downloading === c.key_id ? 'Descargando…' : 'Descargar pública'}
                </button>
                <button
                  className="btn ghost"
                  onClick={() => setOpenCall(c.call_id)}
                >
                  Ver submissions
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {err && <div className="alert error" style={{ marginTop: 10 }}>{err}</div>}
      {pem && (
        <div className="card" style={{ marginTop: 12 }}>
          <h3>Clave pública</h3>
          <pre className="code" style={{ whiteSpace: 'pre-wrap' }}>{pem}</pre>
        </div>
      )}

      {openCall && (
        <SubmissionsByCall callId={openCall} onClose={() => setOpenCall('')} />
      )}
    </>
  )
}
