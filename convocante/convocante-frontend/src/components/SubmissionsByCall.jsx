import { useEffect, useState } from 'react'
import { api } from '../services/api.js'

export default function SubmissionsByCall({ callId, onClose }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const run = async () => {
      setLoading(true); setError('')
      try {
        const list = await api.listSubmissions(callId)
        setItems(list)
      } catch (e) {
        setError(e?.message || 'Error cargando submissions')
      } finally {
        setLoading(false)
      }
    }
    run()
  }, [callId])

  return (
    <div className="card" style={{ marginTop: 12 }}>
      <div className="row">
        <h3>Submissions · <span className="code">{callId}</span></h3>
        <button className="btn ghost" onClick={onClose}>Cerrar</button>
      </div>
      {loading && <p className="muted">Cargando…</p>}
      {error && <div className="alert error">{error}</div>}
      <table className="table">
        <thead>
          <tr>
            <th>submission_id</th>
            <th>creado</th>
            <th>archivos</th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 && !loading && (
            <tr><td colSpan={3} className="muted">Sin submissions aún</td></tr>
          )}
          {items.map((s) => (
            <tr key={s.submission_id}>
              <td className="code">{s.submission_id}</td>
              <td>{s.created_at}</td>
              <td>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {['content.zip','result.json','manifest.json','signature.bin','sealed_base.zip'].map((fname) => {
                    const has = s.files.find(f => f.name === fname)
                    if (!has) return null
                    const href = api.downloadSubmissionFileUrl(callId, s.submission_id, fname)
                    const label = fname === 'content.zip' ? 'Descargar content.zip' :
                                  fname === 'result.json' ? 'Ver result.json' : fname
                    const target = fname === 'result.json' ? '_blank' : '_self'
                    return (
                      <a key={fname} className="btn" href={href} target={target} rel="noreferrer">
                        {label}
                      </a>
                    )
                  })}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
