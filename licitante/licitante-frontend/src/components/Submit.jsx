import { useState } from 'react'
import { api } from '../services/api.js'
export default function Submit(){
  const [sealed,setSealed]=useState(null)
  const [parts,setParts]=useState({meta:null,payload:null,wrapped_key:null,nonce:null,tag:null})
  const [res,setRes]=useState(null); const [err,setErr]=useState(''); const [sending,setSending]=useState(false)
  const canParts = ['meta','payload','wrapped_key','nonce','tag'].every(k=>parts[k])
  const sendSealed=async()=>{ if(!sealed) return; setSending(true); setErr(''); setRes(null); try{setRes(await api.submitSealed(sealed))}catch(e){setErr(e?.message||'Error')}finally{setSending(false)}}
  const sendParts=async()=>{ if(!canParts) return; setSending(true); setErr(''); setRes(null); try{setRes(await api.submitParts(parts))}catch(e){setErr(e?.message||'Error')}finally{setSending(false)}}
  return (<div>
    <h3>Subir sealed.zip</h3>
    <input type="file" accept=".zip,application/zip" onChange={e=>setSealed(e.target.files[0]||null)}/>
    <div style={{marginTop:8}}><button className="btn" onClick={sendSealed} disabled={!sealed||sending}>{sending?'Enviando…':'Enviar sealed.zip'}</button></div>
    <h3 style={{marginTop:18}}>O subir partes</h3>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit, minmax(240px,1fr))',gap:12}}>
      <div><label>meta.json</label><input type="file" accept=".json" onChange={e=>setParts(p=>({...p,meta:e.target.files[0]||null}))}/></div>
      <div><label>payload.enc</label><input type="file" onChange={e=>setParts(p=>({...p,payload:e.target.files[0]||null}))}/></div>
      <div><label>wrapped_key.bin</label><input type="file" onChange={e=>setParts(p=>({...p,wrapped_key:e.target.files[0]||null}))}/></div>
      <div><label>nonce.bin</label><input type="file" onChange={e=>setParts(p=>({...p,nonce:e.target.files[0]||null}))}/></div>
      <div><label>tag.bin</label><input type="file" onChange={e=>setParts(p=>({...p,tag:e.target.files[0]||null}))}/></div>
    </div>
    <div style={{marginTop:8}}><button className="btn" onClick={sendParts} disabled={!canParts||sending}>{sending?'Enviando…':'Enviar partes'}</button></div>
    {err && <div className="alert error" style={{marginTop:10}}>{err}</div>}
    {res && <div className="card" style={{marginTop:10}}><h4>Respuesta</h4><pre className="code" style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(res,null,2)}</pre></div>}
  </div>)
}