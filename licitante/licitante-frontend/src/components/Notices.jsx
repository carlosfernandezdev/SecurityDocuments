import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { loadAuth } from '../services/auth';

export default function Notices(){
  const [items,setItems]=useState([]);
  const [loading,setLoading]=useState(false);
  const [err,setErr]=useState('');
  const auth = loadAuth();
  const bidderId = auth?.bidder_id || '';

  const refresh = async() => {
    setLoading(true); setErr('');
    try{
      const list = await api.listNotifications(bidderId || undefined);
      setItems(list);
    }catch(e){
      setErr(e?.message||'Error');
    }finally{
      setLoading(false);
    }
  };

  useEffect(()=>{ refresh(); /* refresh when bidder changes */ }, [bidderId]);

  return (
    <div>
      <div className="row">
        <h3>Notificaciones {bidderId ? <span className="muted">({bidderId})</span> : null}</h3>
        <button className="btn ghost" onClick={refresh} disabled={loading}>{loading?'Actualizando…':'Actualizar'}</button>
      </div>
      {err && <div className="alert error">{err}</div>}
      <table className="table">
        <thead><tr><th>call_id</th><th>licitante</th><th>decisión</th><th>notas</th></tr></thead>
        <tbody>
          {items.length===0 && <tr><td colSpan={4} className="muted">Sin notificaciones</td></tr>}
          {items.map((n,i)=>(
            <tr key={i}>
              <td className="code">{n.call_id}</td>
              <td className="code">{n.bidder_identifier}</td>
              <td>{n.decision}</td>
              <td>{n.notes||'-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {!bidderId && <div className="muted" style={{marginTop:6}}>Sugerencia: inicia sesión para ver sólo las tuyas.</div>}
    </div>
  );
}
