import React, { useEffect, useState } from 'react'
import { api } from '../api'
export default function Convocatorias() {
  const [items, setItems] = useState([])
  const [sel, setSel] = useState(null)
  useEffect(()=>{ (async()=> setItems(await api('/api/convocatorias')))() },[])
  const open = async (id)=>{ setSel(await api('/api/convocatorias/'+id)) }
  return (
    <div className="container">
      <div className="card">
        <h2 style={{marginTop:0}}>Convocatorias</h2>
        <div className="list">
          {items.map(x=> (
            <div key={x.id} className="card" style={{margin:0}}>
              <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                <div><strong>{x.titulo}</strong><div className="muted">#{x.id}</div></div>
                <button onClick={()=>open(x.id)}>Abrir</button>
              </div>
            </div>
          ))}
        </div>
      </div>
      {sel && <ConvocatoriaDetail item={sel} />}
    </div>
  )
}
function ConvocatoriaDetail({ item }){
  return (
    <div className="card">
      <h3 style={{marginTop:0}}>#{item.id} — {item.titulo}</h3>
      <p className="muted">{item.descripcion}</p>
      <DecryptBox convId={item.id} />
    </div>
  )
}
function DecryptBox({ convId }){
  const [subId, setSubId] = React.useState('')
  const [privB64, setPrivB64] = React.useState('')
  const [out, setOut] = React.useState('')
  const [err, setErr] = React.useState('')
  const run = async ()=>{
    setErr(''); setOut('')
    try{
      const url = `${import.meta.env.VITE_API_BASE || 'http://localhost:8001'}/api/submissions/${convId}/${subId}/decrypt`
      const res = await fetch(url, { method:'POST', credentials:'include', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ private_key_pem_b64: privB64 }) })
      if(!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setOut(data.plaintext_b64 || '')
    }catch(e){ setErr(e.message) }
  }
  return (
    <div className="card" style={{marginTop:16}}>
      <h4 style={{marginTop:0}}>Descifrar propuesta</h4>
      <div className="row">
        <div><label>ID de Submission</label><input value={subId} onChange={e=>setSubId(e.target.value)} placeholder="p.ej. 12" /></div>
        <div><label>Clave privada (PEM en base64)</label><textarea rows={4} value={privB64} onChange={e=>setPrivB64(e.target.value)} placeholder="LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tL..." /></div>
      </div>
      <div className="sp" /><button className="primary" onClick={run}>Descifrar</button>
      {err && <p style={{color:'#fca5a5'}}>{err}</p>}
      {out && (<div className="card" style={{marginTop:12}}><div className="muted">Resultado (base64):</div><textarea readOnly rows={5} value={out} /></div>)}
    </div>
  )
}
