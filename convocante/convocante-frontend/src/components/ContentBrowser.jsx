// src/components/ContentBrowser.jsx
import { useEffect, useState } from 'react'
import { api } from '../services/api.js'

export default function ContentBrowser({ callId, submissionId, onClose }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('')

  useEffect(() => {
    const run = async () => {
      setLoading(true); setError('')
      try {
        const list = await api.listContent(callId, submissionId)
        setItems(list)
      } catch (e) {
        setError(e?.message || 'Error cargando contenido')
      } finally {
        setLoading(false)
      }
    }
    run()
  }, [callId, submissionId])

  const filtered = items.filter(i => !filter || i.rel_path.toLowerCase().includes(filter.toLowerCase()))

  return (
    <div className="card" style={{ marginTop: 12 }}>
      <div className="row">
        <h3>Contenido descifrado · <span className="code">{callId}</span> · <span className="code">{submissionId}</span></h3>
        <button className="btn ghost" onClick={onClose}>Cerrar</button>
      </div>

      <div className="row" style={{ gap: 8, marginTop: 8 }}>
        <input type="text" placeholder="Filtrar por nombre..." value={filter} onChange={e=>setFilter(e.target.value)} />
        <div className="badge">{filtered.length} archivo(s)</div>
      </div>

      {loading && <p className="muted">Cargando…</p>}
      {error && <div className="alert error">{error}</div>}

      <table className="table">
        <thead>
          <tr>
            <th>ruta</th>
            <th style={{width:120}}>tamaño</th>
            <th style={{width:160}}>acciones</th>
          </tr>
        </thead>
        <tbody>
          {filtered.length === 0 && !loading && (
            <tr><td colSpan={3} className="muted">Sin archivos</td></tr>
          )}
          {filtered.map((f) => {
            const url = api.contentFileUrl(callId, submissionId, f.rel_path)
            const isText = /\.(json|txt|log|csv|xml)$/i.test(f.rel_path)
            const isImage = /\.(png|jpg|jpeg)$/i.test(f.rel_path)
            const target = (isText || isImage) ? '_blank' : '_self'
            return (
              <tr key={f.rel_path}>
                <td className="code">{f.rel_path}</td>
                <td>{f.size}</td>
                <td style={{display:'flex', gap:8}}>
                  <a className="btn" href={url} target={target} rel="noreferrer">
                    {(isText || isImage) ? 'Ver' : 'Descargar'}
                  </a>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
