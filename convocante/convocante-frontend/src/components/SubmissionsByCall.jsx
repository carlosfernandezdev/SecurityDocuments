// src/components/SubmissionsByCall.jsx
import { useEffect, useState } from 'react'
import { api, selectWinner} from '../services/api.js'
import ContentList from './ContentList.jsx'

export default function SubmissionsByCall({ callId, onClose }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [openSubmission, setOpenSubmission] = useState('')

  useEffect(() => {
    const run = async () => {
      setLoading(true); setError(''); setOpenSubmission('')
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
            <th>contenido</th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 && !loading && (
            <tr><td colSpan={4} className="muted">Sin submissions aún</td></tr>
          )}
          {items.map((s) => (
            <tr key={s.submission_id}>
              <td className="code">{s.submission_id}</td>
              <td>{s.created_at}</td>
              <td>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                  {['result.json','manifest.json','signature.bin','sealed_base.zip','content.zip'].map((fname) => {
                    const has = s.files.find(f => f.name === fname)
                    if (!has) return null
                    const href = has.download_url.startsWith('/convocante')
                      ? `${api.base}${has.download_url.replace('/convocante','')}`
                      : `${api.base}${has.download_url}`
                    const label = fname === 'result.json' ? 'Ver result.json' : fname
                    const target = fname === 'result.json' ? '_blank' : '_self'
                    return (
                      <a key={fname} className="btn ghost" href={href} target={target} rel="noreferrer">
                        {label}
                      </a>
                    )
                  })}
                </div>
              </td>
              <td>
                <button className="btn" onClick={() => setOpenSubmission(
                  openSubmission === s.submission_id ? '' : s.submission_id
                )}>
                  {openSubmission === s.submission_id ? 'Ocultar contenido' : `Ver contenido (${s?.content?.count ?? 0})`}
                </button>

                {/* Botón Seleccionar ganador */}
                <button
                  className="btn ghost"
                  style={{ marginLeft: 8 }}
                  onClick={async () => {
                    try {
                      const res = await selectWinner(callId, s.submission_id, 'selección desde panel')
                      alert('Notificado:\n' + JSON.stringify(res, null, 2))
                    } catch (e) {
                      alert('Error al notificar: ' + e)
                    }
                  }}
                >
                  Seleccionar ganador
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {openSubmission && (
        <ContentList callId={callId} submissionId={openSubmission} />
      )}
    </div>
  )
}
