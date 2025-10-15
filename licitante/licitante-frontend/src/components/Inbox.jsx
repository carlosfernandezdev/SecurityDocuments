import { useEffect, useState } from 'react'
import { api } from '../services/api.js'
export default function Inbox(){
  const [items,setItems]=useState([]); const [callId,setCallId]=useState(''); const [loading,setLoading]=useState(false); const [err,setErr]=useState('')
  const refresh=async()=>{ setLoading(true); setErr(''); try{setItems(await api.listSubmissions(callId||undefined))}catch(e){setErr(e?.message||'Error')}finally{setLoading(false)} }
  useEffect(()=>{refresh()},[])
  return (<div>
    <div className="row" style={{gap:8}}>
      <input type="text" placeholder="Filtrar por call_id (opcional)" value={callId} onChange={e=>setCallId(e.target.value)}/>
      <button className="btn ghost" onClick={refresh} disabled={loading}>{loading?'Actualizando…':'Actualizar'}</button>
    </div>
    {err && <div className="alert error">{err}</div>}
    <table className="table"><thead><tr><th>id</th><th>call_id</th><th>licitante</th><th>status</th><th>creado</th></tr></thead>
    <tbody>{items.length===0 && <tr><td colSpan={5} className="muted">Sin envíos</td></tr>}{items.map(it=>(
      <tr key={`${it.call_id}-${it.id}`}><td className="code">{it.id}</td><td className="code">{it.call_id}</td><td className="code">{it.bidder_identifier||'-'}</td><td>{it.status}</td><td>{it.created_at}</td></tr>
    ))}</tbody></table>
  </div>)
}