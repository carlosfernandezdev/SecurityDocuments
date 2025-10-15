import { useEffect, useState } from 'react'
import CreateCallForm from './components/CreateCallForm.jsx'
import CallsTable from './components/CallsTable.jsx'
import SubmissionTester from './components/SubmissionTester.jsx'
import { api } from './services/api.js'

export default function App() {
  const [calls, setCalls] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const refresh = async () => {
    setLoading(true)
    setError('')
    try {
      const list = await api.listCalls()
      setCalls(list)
    } catch (e) {
      setError(e?.message || 'Error cargando convocatorias')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  return (
    <div className="container">
      <header>
        <h1>Convocante · Administración</h1>
        <p className="muted">
          Crea convocatorias, lista `call_id` y `key_id`, y descarga la clave pública por convocatoria.
        </p>
      </header>

      <section className="card">
        <h2>Crear convocatoria</h2>
        <CreateCallForm onCreated={refresh} />
      </section>

      <section className="card">
        <div className="row">
          <h2>Convocatorias</h2>
          <button className="btn ghost" onClick={refresh} disabled={loading}>
            {loading ? 'Actualizando…' : 'Actualizar'}
          </button>
        </div>
        {error && <div className="alert error">{error}</div>}
        <CallsTable items={calls} />
      </section>

      <section className="card">
        <details>
          <summary>Herramienta de prueba de recepción (opcional)</summary>
          <p className="muted">
            Solo para pruebas locales: sube <code>meta.json</code>, <code>payload.enc</code>,
            <code>wrapped_key.bin</code>, <code>nonce.bin</code> y <code>tag.bin</code> para simular
            una recepción en <code>/internal/receive-proposal</code>.
          </p>
          <SubmissionTester />
        </details>
      </section>

      <footer>
        <small>API base: <code>{api.base}</code></small>
      </footer>
    </div>
  )
}
