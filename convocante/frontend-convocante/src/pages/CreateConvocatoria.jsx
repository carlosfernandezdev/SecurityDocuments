import React, { useState } from 'react'
import { api } from '../api'
export default function CreateConvocatoria(){
  const [titulo, setTitulo] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [ok, setOk] = useState('')
  const [err, setErr] = useState('')
  const submit = async (e)=>{
    e.preventDefault(); setErr(''); setOk('')
    try{
      const c = await api('/api/convocatorias', { method:'POST', body: JSON.stringify({ titulo, descripcion }) })
      setOk(`Creada #${c.id}`); setTitulo(''); setDescripcion('')
    }catch(e){ setErr(e.message) }
  }
  return (
    <div className="container">
      <div className="card">
        <h2 style={{marginTop:0}}>Nueva convocatoria</h2>
        <form onSubmit={submit}>
          <label>Título</label><input value={titulo} onChange={e=>setTitulo(e.target.value)} required />
          <label>Descripción</label><textarea rows={4} value={descripcion} onChange={e=>setDescripcion(e.target.value)} required />
          <div className="sp" /><button className="primary">Crear</button>
        </form>
        {ok && <p style={{color:'#34d399'}}>{ok}</p>}
        {err && <p style={{color:'#fca5a5'}}>{err}</p>}
      </div>
    </div>
  )
}
