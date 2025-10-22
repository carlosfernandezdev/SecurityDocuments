import React, { useEffect, useState } from 'react'
import { api, API } from '../api'
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8001/ws/licitante'
export default function Convocatorias() {
  const [items, setItems] = useState([])
  const [log, setLog] = useState([])
  const [sel, setSel] = useState(null)
  useEffect(()=>{ (async()=> setItems(await api('/api/convocatorias')))() },[])
  useEffect(()=>{
    const ws = new WebSocket(WS_URL)
    ws.onopen = () => setLog(x=>[...x, 'WS conectado'])
    ws.onmessage = (ev)=>{
      try{
        const data = JSON.parse(ev.data)
        if(data.type === 'new_convocatoria'){
          setItems(curr=>[{ id:data.id, titulo:data.titulo, descripcion:'(nueva)' }, ...curr])
          setLog(x=>[...x, `Nueva convocatoria #${data.id}: ${data.titulo}`])
        }
      }catch{}
    }
    ws.onclose = ()=> setLog(x=>[...x, 'WS desconectado'])
    return ()=> ws.close()
  }, [])
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
      <div className="card">
        <strong>Eventos</strong>
        <ul className="muted" style={{marginTop:8}}>
          {log.map((l,i)=><li key={i}>{l}</li>)}
        </ul>
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
      <SubmissionForm convId={item.id} />
    </div>
  )
}
function SubmissionForm({ convId }){
  const [payload_sha256, setP] = React.useState('')
  const [content_zip_sha256, setC] = React.useState('')
  const [sealed_zip_sha256, setS] = React.useState('')
  const [wrapped_key_b64, setWK] = React.useState('')
  const [nonce_b64, setN] = React.useState('')
  const [tag_b64, setT] = React.useState('')
  const [ciphertext_b64, setCT] = React.useState('')
  const [signer_pk_hex, setPK] = React.useState('')
  const [signature_b64, setSIG] = React.useState('')
  const [ok, setOk] = React.useState('')
  const [err, setErr] = React.useState('')
  const submit = async (e)=>{
    e.preventDefault(); setErr(''); setOk('')
    try{
      const body = { payload_sha256, content_zip_sha256, sealed_zip_sha256,
        wrapped_key_b64, nonce_b64, tag_b64, ciphertext_b64,
        signer_pk_hex: signer_pk_hex || null, signature_b64: signature_b64 || null }
      const r = await fetch(`${API}/api/submissions/${convId}`, { method:'POST', credentials:'include', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body) })
      if(!r.ok) throw new Error(await r.text())
      const data = await r.json()
      setOk(`Enviado #${data.id}`); setWK(''); setN(''); setT(''); setCT(''); setPK(''); setSIG('')
    }catch(e){ setErr(e.message) }
  }
  return (
    <div className="card" style={{marginTop:16}}>
      <h4 style={{marginTop:0}}>Enviar propuesta cifrada</h4>
      <form onSubmit={submit}>
        <div className="row">
          <div><label>wrapped_key (b64)</label><textarea rows={3} value={wrapped_key_b64} onChange={e=>setWK(e.target.value)} required /></div>
          <div><label>nonce (b64)</label><input value={nonce_b64} onChange={e=>setN(e.target.value)} required /><label>tag (b64)</label><input value={tag_b64} onChange={e=>setT(e.target.value)} required /></div>
        </div>
        <label>ciphertext (b64)</label><textarea rows={4} value={ciphertext_b64} onChange={e=>setCT(e.target.value)} required />
        <div className="row">
          <div><label>signer_pk_hex (opcional)</label><input value={signer_pk_hex} onChange={e=>setPK(e.target.value)} /></div>
          <div><label>signature (b64, opcional)</label><input value={signature_b64} onChange={e=>setSIG(e.target.value)} /></div>
        </div>
        <div className="row">
          <div><label>payload_sha256 (opcional)</label><input value={payload_sha256} onChange={e=>setP(e.target.value)} /></div>
          <div><label>content_zip_sha256 (opcional)</label><input value={content_zip_sha256} onChange={e=>setC(e.target.value)} /></div>
          <div><label>sealed_zip_sha256 (opcional)</label><input value={sealed_zip_sha256} onChange={e=>setS(e.target.value)} /></div>
        </div>
        <div className="sp" /><button className="primary">Enviar</button>
      </form>
      {ok && <p style={{color:'#34d399'}}>{ok}</p>}
      {err && <p style={{color:'#fca5a5'}}>{err}</p>}
    </div>
  )
}
