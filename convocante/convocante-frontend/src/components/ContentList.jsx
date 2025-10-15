// src/components/ContentList.jsx
import { useEffect, useState } from 'react'
import { api } from '../services/api.js'

export default function ContentList({ callId, submissionId }) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const run = async () => {
      setLoading(true); setError('')
      try {
        const list = await api.listContentFiles(callId, submissionId)
        setItems(list)
      } catch (e) {
        setError(e?.message || 'Error cargando contenido')
      } finally {
        setLoading(false)
      }
    }
    run()
  }, [callId, submissionId])

  return (
    <div className="card" style={{ marginTop: 10 }}>
      <h4>Contenido desencriptado</h4>
      {loading && <p className="muted">Cargando…</p>}
      {error && <div className="alert error">{error}</div>}
      {!loading && items.length === 0 && <p className="muted">No hay archivos.</p>}
      {items.length > 0 && (
        <table className="table">
          <thead>
            <tr>
              <th>ruta</th>
              <th>tamaño</th>
              <th>descargar</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.path}>
                <td className="code">{it.path}</td>
                <td>{it.size.toLocaleString()} B</td>
                <td>
                  <a className="btn" href={api.downloadContentFileUrl(callId, submissionId, it.path)}>
                    Descargar
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
