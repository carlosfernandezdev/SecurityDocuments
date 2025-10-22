import React from 'react'
import { api } from '../api'
export default function Header({ title, user, onLogout }) {
  const logout = async ()=>{ await api('/api/auth/logout', { method:'POST' }); onLogout() }
  return (
    <header>
      <div className="container" style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <strong>{title}</strong>
        <div style={{display:'flex', alignItems:'center', gap:10}}>
          {user && <span className="badge">{user.role}</span>}
          {user && <span className="muted">{user.email}</span>}
          {user && <button onClick={logout}>Salir</button>}
        </div>
      </div>
    </header>
  )
}
