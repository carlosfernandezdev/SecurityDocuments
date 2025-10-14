import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  listCalls,
  listSubmissions,
  submitSealedZip,
  submitPieces,
  resolveRsaPubUrl,
  getHealth,
  wsUrlFor,
  formatIso,
} from "./api";

export default function App() {
  // estado principal
  const [calls, setCalls] = useState([]);
  const [selectedCall, setSelectedCall] = useState(null);
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);

  // usuario (para submissions)
  const [user, setUser] = useState("carlos");
  const [subs, setSubs] = useState([]);

  // health
  const [health, setHealth] = useState(null);

  // WebSocket
  const [wsStatus, setWsStatus] = useState("DISCONNECTED");
  const wsRef = useRef(null);
  const retryRef = useRef(null);

  // formularios
  const [sealedFile, setSealedFile] = useState(null);
  const [sendingZip, setSendingZip] = useState(false);

  const [fileMeta, setFileMeta] = useState(null);
  const [filePayload, setFilePayload] = useState(null);
  const [fileWrapped, setFileWrapped] = useState(null);
  const [fileNonce, setFileNonce] = useState(null);
  const [fileTag, setFileTag] = useState(null);
  const [sendingPieces, setSendingPieces] = useState(false);

  // ----- carga -----
  async function refreshCalls() {
    setLoading(true);
    setMsg("");
    try {
      const c = await listCalls(); // ← backend del licitante
      setCalls(c);
      if (!selectedCall && c.length) setSelectedCall(c[0].id);
      if (!c.length) setMsg("No hay convocatorias en el backend del licitante (aún).");
    } catch (e) {
      setCalls([]);
      setMsg("No pude cargar convocatorias: " + (e?.message || e));
    } finally {
      setLoading(false);
    }
  }

  async function refreshSubs() {
    try {
      const s = await listSubmissions(user);
      setSubs(s);
    } catch {
      // no bloquea UI
    }
  }

  async function refreshHealth() {
    try {
      const h = await getHealth();
      setHealth(h);
    } catch {
      setHealth(null);
    }
  }

  useEffect(() => {
    refreshCalls();
    refreshSubs();
    refreshHealth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selected = useMemo(
    () => calls.find((c) => c.id === selectedCall) || null,
    [calls, selectedCall]
  );

  // ----- WS con reconexión -----
  useEffect(() => {
    const url = wsUrlFor(user);
    let closed = false;

    function connect(delayMs = 0) {
      if (closed) return;
      setWsStatus("CONNECTING");
      clearTimeout(retryRef.current);
      retryRef.current = setTimeout(() => {
        try {
          const ws = new WebSocket(url);
          wsRef.current = ws;
          ws.onopen = () => setWsStatus("CONNECTED");
          ws.onclose = () => {
            setWsStatus("DISCONNECTED");
            if (!closed) connect(1200);
          };
          ws.onerror = () => { /* reconecta en onclose */ };
          ws.onmessage = (ev) => {
            try {
              const m = JSON.parse(ev.data);
              if (m?.type === "submitted") {
                refreshSubs();
              }
            } catch {}
          };
        } catch {
          setWsStatus("DISCONNECTED");
          connect(1200);
        }
      }, delayMs);
    }

    connect(0);
    return () => {
      closed = true;
      clearTimeout(retryRef.current);
      try { wsRef.current?.close(); } catch {}
    };
  }, [user]);

  // ----- envíos -----
  async function onSendSealed(e) {
    e.preventDefault();
    setMsg("");
    if (!sealedFile) { setMsg("Selecciona un sealed.zip"); return; }
    try {
      setSendingZip(true);
      const res = await submitSealedZip({ user, file: sealedFile });
      setMsg(`Envío sealed.zip: ${JSON.stringify(res)}`);
      refreshSubs();
    } catch (e2) {
      setMsg("Falló el envío sealed.zip: " + (e2?.message || e2));
    } finally {
      setSendingZip(false);
    }
  }

  async function onSendPieces(e) {
    e.preventDefault();
    setMsg("");
    if (!(fileMeta && filePayload && fileWrapped && fileNonce && fileTag)) {
      setMsg("Faltan archivos: meta, payload, wrapped_key, nonce, tag");
      return;
    }
    try {
      setSendingPieces(true);
      const res = await submitPieces({
        user,
        meta: fileMeta,
        payload: filePayload,
        wrapped_key: fileWrapped,
        nonce: fileNonce,
        tag: fileTag,
      });
      setMsg(`Envío piezas: ${JSON.stringify(res)}`);
      refreshSubs();
    } catch (e2) {
      setMsg("Falló el envío de piezas: " + (e2?.message || e2));
    } finally {
      setSendingPieces(false);
    }
  }

  return (
    <div className="container">
      <h1>Licitante — Panel</h1>
      <p>WS: <span className="badge">{wsStatus}</span> &nbsp;|&nbsp; Health: {health?.ok ? <span className="badge ok">OK</span> : <span className="badge warn">—</span>} {health?.time ? ` • ${formatIso(health.time)}` : ""}</p>

      <div className="card">
        <label>Usuario</label>
        <input value={user} onChange={(e) => setUser(e.target.value)} placeholder="usuario" />
        &nbsp;
        <button onClick={() => refreshCalls()} disabled={loading}>
          {loading ? "Actualizando..." : "Actualizar"}
        </button>
      </div>

      {msg && <div className="toast">{msg}</div>}

      {/* Convocatorias + Detalle */}
      <div className="grid2">
        <section className="card">
          <h2 style={{ marginTop: 0 }}>Convocatorias</h2>
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Key</th>
                <th>Creada</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {calls.length === 0 && (
                <tr>
                  <td colSpan={4} style={{ textAlign: "center", color: "var(--muted)" }}>
                    {loading ? "Cargando..." : "No hay convocatorias"}
                  </td>
                </tr>
              )}
              {calls.map((c) => (
                <tr key={c.id}>
                  <td className="mono">{c.id}</td>
                  <td>{c.key_id}</td>
                  <td>{formatIso(c.created_at)}</td>
                  <td>
                    <button className="small" onClick={() => setSelectedCall(c.id)}>Ver</button>
                    &nbsp;
                    {c.rsa_pub_pem_url && (
                      <a href={resolveRsaPubUrl(c)} target="_blank" rel="noreferrer" style={{ color: "var(--pri)", textDecoration: "none" }}>
                        PEM
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="card">
          <h2 style={{ marginTop: 0 }}>Detalle</h2>
          {!selected ? (
            <p className="small" style={{ color: "var(--muted)" }}>Selecciona una convocatoria.</p>
          ) : (
            <>
              <p><b>ID:</b> <span className="mono">{selected.id}</span></p>
              <p><b>Key ID:</b> {selected.key_id}</p>
              <p><b>Creada:</b> {formatIso(selected.created_at)}</p>
              <p>
                <b>PEM:</b>{" "}
                {selected.rsa_pub_pem_url ? (
                  <a href={resolveRsaPubUrl(selected)} target="_blank" rel="noreferrer" style={{ color: "var(--pri)", textDecoration: "none" }}>
                    Abrir rsa_pub.pem
                  </a>
                ) : (
                  <span className="small" style={{ color: "var(--muted)" }}>No disponible</span>
                )}
              </p>
              <details>
                <summary>Ver JSON</summary>
                <pre className="small mono" style={{ whiteSpace: "pre-wrap" }}>
                  {JSON.stringify(selected._raw, null, 2)}
                </pre>
              </details>
            </>
          )}
        </section>
      </div>

      {/* Envío de propuestas */}
      <div className="grid2">
        <section className="card">
          <h2 style={{ marginTop: 0 }}>Enviar sealed.zip</h2>
          <form onSubmit={onSendSealed}>
            <label>Archivo</label>
            <input
              type="file"
              accept=".zip,application/zip"
              onChange={(e) => setSealedFile(e.target.files?.[0] || null)}
            />
            <div style={{ marginTop: 8 }}>
              <button disabled={sendingZip}>
                {sendingZip ? "Enviando..." : "Enviar"}
              </button>
            </div>
          </form>
        </section>

        <section className="card">
          <h2 style={{ marginTop: 0 }}>Enviar piezas</h2>
          <form onSubmit={onSendPieces}>
            <label>meta.json</label>
            <input type="file" accept="application/json,.json" onChange={(e) => setFileMeta(e.target.files?.[0] || null)} />
            <label>payload.enc</label>
            <input type="file" onChange={(e) => setFilePayload(e.target.files?.[0] || null)} />
            <label>wrapped_key.bin</label>
            <input type="file" onChange={(e) => setFileWrapped(e.target.files?.[0] || null)} />
            <label>nonce.bin</label>
            <input type="file" onChange={(e) => setFileNonce(e.target.files?.[0] || null)} />
            <label>tag.bin</label>
            <input type="file" onChange={(e) => setFileTag(e.target.files?.[0] || null)} />

            <div style={{ marginTop: 8 }}>
              <button disabled={sendingPieces}>
                {sendingPieces ? "Enviando..." : "Enviar"}
              </button>
            </div>
          </form>
        </section>
      </div>

      {/* Mis envíos */}
      <section className="card">
        <h2 style={{ marginTop: 0 }}>Mis envíos</h2>
        {subs.length === 0 ? (
          <p className="small" style={{ color: "var(--muted)" }}>No hay envíos.</p>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Estado</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              {subs.map((s) => (
                <tr key={s.id}>
                  <td className="mono">{s.id}</td>
                  <td>
                    <span className={`badge ${s.state === "PENDING" ? "warn" : s.state === "OK" ? "ok" : "bad"}`}>
                      {s.state}
                    </span>
                  </td>
                  <td>{formatIso(s.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
