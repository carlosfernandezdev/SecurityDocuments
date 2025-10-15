import { useEffect, useState } from 'react';
import { api } from './services/api';
import { loadAuth } from './services/auth';

import Auth from './components/Auth';
import Calls from './components/Calls';
import Submit from './components/Submit';
import Inbox from './components/Inbox';
import Notices from './components/Notices';

export default function App(){
  const [calls,setCalls]=useState([]);
  const [loading,setLoading]=useState(false);
  const [err,setErr]=useState('');
  const [session,setSession]=useState(loadAuth());

  const refreshCalls = async() => {
    setLoading(true); setErr('');
    try{
      setCalls(await api.listCalls());
    }catch(e){
      setErr(e?.message||'Error cargando convocatorias');
    }finally{
      setLoading(false);
    }
  };

  useEffect(()=>{ refreshCalls(); },[]);

  return (
    <div className="container">
      <h1>Licitante · Portal</h1>
      <p className="muted">Inicia sesión local para filtrar tus notificaciones y simular múltiples licitantes en esta máquina.</p>

      {/* Acceso (registro + login) */}
      <Auth onAuthChange={setSession} />

      <div className="card">
        <div className="row">
          <h2>Convocatorias</h2>
          <button className="btn ghost" onClick={refreshCalls} disabled={loading}>{loading?'Actualizando…':'Actualizar'}</button>
        </div>
        {err && <div className="alert error">{err}</div>}
        <Calls items={calls}/>
      </div>

      <div className="card">
        <h2>Enviar licitación</h2>
        <Submit/>
      </div>

      <div className="card">
        <h2>Envíos recientes</h2>
        <Inbox/>
      </div>

      <div className="card">
        <h2>Notificaciones</h2>
        <Notices/>
      </div>
    </div>
  );
}
