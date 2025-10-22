import React, { useState } from 'react'
import { api } from '../api'
export default function AuthBox({ onAuth }) {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [role, setRole] = useState('LICITANTE')
  const [err, setErr] = useState('')
  const submit = async (e) => {
    e.preventDefault()
    setErr('')
    try {
      if (mode === 'register') {
        await api('/api/auth/register', { method: 'POST', body: JSON.stringify({ email, password, name, role }) })
      }
      const user = await api('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
      onAuth(user)
    } catch (e) { setErr(e.message || 'Error') }
  }
  return (
    <div className="card" style={{maxWidth:480, margin:'40px auto'}}>
      <h2 style={{marginTop:0}}>{mode === 'login' ? 'Iniciar sesión' : 'Crear cuenta'}</h2>
      <form onSubmit={submit}>
        {mode === 'register' && (<>
          <label>Nombre</label>
          <input value={name} onChange={e=>setName(e.target.value)} required />
          <label>Rol</label>
          <select value={role} onChange={e=>setRole(e.target.value)}>
            <option value="CONVOCANTE">CONVOCANTE</option>
            <option value="LICITANTE">LICITANTE</option>
          </select>
        </>)}
        <label>Email</label><input type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
        <label>Contraseña</label><input type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
        <div className="sp" />
        <div className="row">
          <button type="submit" className="primary">{mode === 'login' ? 'Entrar' : 'Registrar'}</button>
          <button type="button" onClick={()=>setMode(mode==='login'?'register':'login')}>{mode==='login'?'Crear cuenta':'Ya tengo cuenta'}</button>
        </div>
      </form>
      {err && <p className="muted" style={{color:'#fca5a5'}}>{err}</p>}
    </div>
  )
}
