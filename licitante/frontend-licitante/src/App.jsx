import React, { useState } from 'react'
import Header from './components/Header.jsx'
import AuthBox from './components/AuthBox.jsx'
import Convocatorias from './pages/Convocatorias.jsx'
export default function App(){
  const [user, setUser] = useState(null)
  if(!user) return <AuthBox onAuth={setUser} />
  return (<>
    <Header title="Licitante" user={user} onLogout={()=>setUser(null)} />
    <Convocatorias />
  </>)
}
