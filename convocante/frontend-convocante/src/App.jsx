import React, { useState } from 'react'
import Header from './components/Header.jsx'
import AuthBox from './components/AuthBox.jsx'
import Convocatorias from './pages/Convocatorias.jsx'
import CreateConvocatoria from './pages/CreateConvocatoria.jsx'
export default function App(){
  const [user, setUser] = useState(null)
  const [tab, setTab] = useState('convocatorias')
  if(!user) return <AuthBox onAuth={setUser} />
  return (<>
    <Header title="Convocante" user={user} onLogout={()=>setUser(null)} />
    <div className="container">
      <div className="card" style={{display:'flex', gap:8}}>
        <button className={tab==='convocatorias'?'primary':''} onClick={()=>setTab('convocatorias')}>Convocatorias</button>
        <button className={tab==='create'?'primary':''} onClick={()=>setTab('create')}>Crear convocatoria</button>
      </div>
    </div>
    {tab==='convocatorias' && <Convocatorias />}
    {tab==='create' && <CreateConvocatoria />}
  </>)
}
