import { useEffect, useState } from "react";
import { getUserNotices, getCallSummary } from "../services/api";

export default function Notices(){
  const [user, setUser] = useState("");
  const [callId, setCallId] = useState("");
  const [items, setItems] = useState([]);
  const [summary, setSummary] = useState(null);
  const [status, setStatus] = useState("");

  const load = async () => {
    setStatus("Cargando...");
    try{
      const [u, s] = await Promise.all([
        user ? getUserNotices(user, callId) : Promise.resolve({items:[]}),
        callId ? getCallSummary(callId) : Promise.resolve(null)
      ]);
      setItems(u.items || []);
      setSummary(s);
      setStatus("");
    }catch(e){
      setStatus(String(e));
    }
  };

  useEffect(()=>{ /* carga inicial vacía */ },[]);

  return (
    <div className="card">
      <h2>Notificaciones</h2>
      <div className="row">
        <label>Usuario</label>
        <input value={user} onChange={(e)=>setUser(e.target.value)} placeholder="ej: 5555" />
        <label>Convocatoria</label>
        <input value={callId} onChange={(e)=>setCallId(e.target.value)} placeholder="ej: Charlie" />
        <button onClick={load}>Buscar</button>
      </div>

      {status && <pre>{status}</pre>}

      {summary && (
        <section className="card" style={{marginTop:12}}>
          <h3>Resumen por convocatoria: {summary.call_id}</h3>
          <p><b>Seleccionado:</b> {summary.selected || "(pendiente)"}</p>
          <ul>
            {(summary.results||[]).map((r,i)=>(
              <li key={i}>
                submission_id: <code>{r.submission_id}</code> — decision: <b>{r.decision}</b> {r.bidder_identifier?`— bidder: ${r.bidder_identifier}`:""}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="card" style={{marginTop:12}}>
        <h3>Notificaciones del usuario {user || "(sin usuario)"}</h3>
        {items.length===0 ? <p className="muted">Sin notificaciones</p> : (
          <table className="table">
            <thead><tr>
              <th>call_id</th><th>submission_id</th><th>decision</th>
            </tr></thead>
            <tbody>
              {items.map((n,idx)=>(
                <tr key={idx}>
                  <td>{n.call_id}</td>
                  <td><code>{n.submission_id}</code></td>
                  <td><b>{n.decision}</b></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
