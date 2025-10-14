import { useEffect, useMemo, useState } from "react";
import { Routes, Route, Link, NavLink } from "react-router-dom";
import { listCalls, createCall, getCall, getActiveCall, getPublicCall, getSubmission } from "./api.js";

/* ---------------- UI Shell ---------------- */
function Header() {
  return (
    <header className="app-header">
      <Link to="/" className="button secondary">🏛️ Convocante</Link>
      <nav className="nav">
        <NavLink to="/" end className={({ isActive }) => `button secondary ${isActive ? "active" : ""}`}>Convocatorias</NavLink>
        <NavLink to="/nueva" className={({ isActive }) => `button secondary ${isActive ? "active" : ""}`}>Nueva</NavLink>
        <NavLink to="/ofertas" className={({ isActive }) => `button secondary ${isActive ? "active" : ""}`}>Ofertas</NavLink>
      </nav>
    </header>
  );
}

/* ---------------- Pages ---------------- */
function CallsList() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data = await listCalls();
      const list = Array.isArray(data?.calls) ? data.calls : [];
      setRows(list);
    } catch (e) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="card">
      <div className="card-head">
        <h2>Convocatorias</h2>
        <div className="toolbar">
          <Link to="/nueva" className="button">+ Nueva</Link>
        </div>
      </div>

      {loading ? <p>Cargando…</p> : rows.length === 0 ? (
        <p className="muted">No hay convocatorias.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>call_id</th>
              <th>key_id</th>
              <th>Creada</th>
              <th>Clave pública</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.call_id}>
                <td>{c.call_id}</td>
                <td>{c.key_id}</td>
                <td>{formatDate(c.created_at)}</td>
                <td>
                  <a className="button secondary" href={`${c.rsa_pub_pem_url}`} target="_blank" rel="noreferrer">
                    Ver PEM
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function NewCall() {
  const [callId, setCallId] = useState(defaultCallId());
  const [keyId, setKeyId] = useState("default");
  const [creating, setCreating] = useState(false);
  const [result, setResult] = useState(null);

  async function onSubmit(e) {
    e.preventDefault();
    setCreating(true);
    try {
      const res = await createCall({ call_id: callId.trim(), key_id: keyId.trim() || "default" });
      setResult(res);
    } catch (e) {
      alert(e.message);
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="card">
      <h2>Nueva Convocatoria</h2>
      <form onSubmit={onSubmit} className="row" style={{ marginTop: 12 }}>
        <div>
          <label>call_id</label>
          <input className="input" value={callId} onChange={e => setCallId(e.target.value)} required />
        </div>
        <div>
          <label>key_id</label>
          <input className="input" value={keyId} onChange={e => setKeyId(e.target.value)} />
        </div>
        <div style={{ gridColumn: "1 / -1" }}>
          <button className="button" disabled={creating}>
            {creating ? "Creando…" : "Crear"}
          </button>
        </div>
      </form>

      {result && (
        <div style={{ marginTop: 16 }} className="card">
          <h3>Respuesta del backend</h3>
          <pre className="pre">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}

      <div className="card" style={{ marginTop: 16 }}>
        <h3>Convocatoria activa (atajo)</h3>
        <ActiveCallPeek />
      </div>
    </div>
  );
}

function ActiveCallPeek() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      setData(await getActiveCall());
    } catch (e) {
      setData(null);
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) return <p>Cargando…</p>;
  if (!data) return <p className="muted">No hay activa o error.</p>;
  return (
    <>
      <p><b>call_id:</b> {data.call_id}</p>
      <p><b>key_id:</b> {data.key_id}</p>
      <pre className="pre">{data.rsa_pub_pem}</pre>
    </>
  );
}

function Offers() {
  const [callId, setCallId] = useState("");
  const [call, setCall] = useState(null);
  const [loadingCall, setLoadingCall] = useState(false);

  const [submissionId, setSubmissionId] = useState("");
  const [submission, setSubmission] = useState(null);
  const [loadingSub, setLoadingSub] = useState(false);

  // Carga de detalle de convocatoria
  const loadCall = async () => {
    if (!callId) return;
    setLoadingCall(true);
    try {
      const res = await getCall(callId);
      setCall(res?.call ?? null);
    } catch (e) {
      setCall(null);
      alert(e.message);
    } finally {
      setLoadingCall(false);
    }
  };

  // Carga de clave pública desde public_api
  const [pubInfo, setPubInfo] = useState(null);
  const loadPublic = async () => {
    if (!callId) return;
    try {
      const res = await getPublicCall(callId);
      setPubInfo(res);
    } catch (e) {
      setPubInfo(null);
    }
  };

  // Carga de submission individual
  const loadSubmission = async () => {
    if (!callId || !submissionId) return;
    setLoadingSub(true);
    try {
      const res = await getSubmission(callId, submissionId);
      setSubmission(res);
    } catch (e) {
      setSubmission(null);
      alert(e.message);
    } finally {
      setLoadingSub(false);
    }
  };

  useEffect(() => { if (callId) { loadCall(); loadPublic(); } }, [callId]);

  return (
    <div className="card">
      <h2>Ofertas / Detalles</h2>

      <div className="row" style={{ marginTop: 12 }}>
        <div>
          <label>ID Convocatoria (call_id)</label>
          <input className="input" value={callId} onChange={e => setCallId(e.target.value)} placeholder="p.ej. 2025-10-08-001" />
        </div>
        <div style={{ display: "flex", alignItems: "flex-end" }}>
          <button className="button" onClick={loadCall} disabled={!callId || loadingCall}>
            {loadingCall ? "Cargando…" : "Buscar"}
          </button>
        </div>
      </div>

      {call && (
        <div className="call-summary" style={{ marginTop: 12 }}>
          <p><b>key_id:</b> {call.key_id}</p>
          <p><b>PEM público:</b> <a className="button secondary" href={call.rsa_pub_pem_url} target="_blank" rel="noreferrer">Abrir</a></p>
          {pubInfo?.rsa_pub_pem && <pre className="pre">{pubInfo.rsa_pub_pem}</pre>}
        </div>
      )}

      <hr style={{ border: 0, borderTop: "1px solid #263142", margin: "16px 0" }} />

      <h3>Ver una submission (individual)</h3>
      <div className="row" style={{ marginTop: 12 }}>
        <div>
          <label>submission_id</label>
          <input className="input" value={submissionId} onChange={e => setSubmissionId(e.target.value)} placeholder="hash de 12 chars" />
        </div>
        <div style={{ display: "flex", alignItems: "flex-end" }}>
          <button className="button" onClick={loadSubmission} disabled={!callId || !submissionId || loadingSub}>
            {loadingSub ? "Cargando…" : "Consultar"}
          </button>
        </div>
      </div>

      {submission && (
        <div className="card" style={{ marginTop: 16 }}>
          <h4>Submission</h4>
          <pre className="pre">{JSON.stringify(submission, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

/* ---------------- App ---------------- */
export default function App() {
  return (
    <>
      <Header />
      <div className="container">
        <Routes>
          <Route path="/" element={<CallsList />} />
          <Route path="/nueva" element={<NewCall />} />
          <Route path="/ofertas" element={<Offers />} />
        </Routes>
      </div>
    </>
  );
}

/* ---------------- Utils ---------------- */
function defaultCallId() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
}
function formatDate(v) {
  if (!v) return "-";
  const d = new Date(v);
  if (Number.isNaN(d.getTime())) return String(v);
  return d.toLocaleString();
}
