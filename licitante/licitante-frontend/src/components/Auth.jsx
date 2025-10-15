import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { saveAuth, loadAuth, clearAuth } from '../services/auth';

export default function Auth({ onAuthChange }) {
  const [registered, setRegistered] = useState([]);
  const [rBidder, setRBidder] = useState('');
  const [rPass, setRPass] = useState('');
  const [lBidder, setLBidder] = useState('');
  const [lPass, setLPass] = useState('');
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');
  const [loading, setLoading] = useState(false);

  const refreshAccounts = async () => {
    setErr(''); setLoading(true);
    try {
      const list = await api.listAccounts();
      setRegistered(list || []);
    } catch (e) {
      setErr(e?.message || 'Error listando cuentas');
    } finally { setLoading(false); }
  };

  useEffect(() => { refreshAccounts(); }, []);

  const doRegister = async () => {
    setMsg(''); setErr('');
    if (!rBidder || !rPass) { setErr('Completa bidder_id y password'); return; }
    try {
      await api.createAccount(rBidder.trim(), rPass);
      setMsg(`Cuenta creada: ${rBidder.trim()}`);
      setRBidder(''); setRPass('');
      refreshAccounts();
    } catch (e) {
      setErr(e?.message || 'Error creando cuenta');
    }
  };

  const doLogin = () => {
    setMsg(''); setErr('');
    if (!lBidder || !lPass) { setErr('Completa usuario y contraseña'); return; }
    saveAuth({ bidder_id: lBidder.trim(), password: lPass });
    onAuthChange(loadAuth());
    setMsg(`Sesión iniciada como ${lBidder.trim()}`);
    setLBidder(''); setLPass('');
  };

  const doLogout = () => {
    clearAuth();
    onAuthChange(null);
    setMsg('Sesión cerrada');
  };

  const current = loadAuth();

  return (
    <div className="card">
      <div className="row">
        <h2>Acceso</h2>
        <button className="btn ghost" onClick={refreshAccounts} disabled={loading}>
          {loading ? 'Actualizando…' : 'Actualizar'}
        </button>
      </div>

      {err && <div className="alert error">{err}</div>}
      {msg && <div className="alert" style={{background:'rgba(110,168,254,.12)',border:'1px solid rgba(110,168,254,.35)',padding:10,borderRadius:10}}>{msg}</div>}

      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(280px,1fr))',gap:16}}>
        <div className="card" style={{margin:0}}>
          <h3>Registro</h3>
          <p className="muted">Crea una cuenta simple (local) para tu licitante.</p>
          <div style={{display:'grid', gap:8}}>
            <input placeholder="bidder_id (p.ej. LIC-001)" value={rBidder} onChange={e=>setRBidder(e.target.value)} />
            <input placeholder="password" type="password" value={rPass} onChange={e=>setRPass(e.target.value)} />
            <button className="btn" onClick={doRegister}>Crear cuenta</button>
          </div>
          <div style={{marginTop:12}}>
            <h4 className="muted" style={{marginBottom:6}}>Cuentas registradas</h4>
            <ul style={{margin:0, paddingLeft:18}}>
              {registered.length === 0 && <li className="muted">No hay cuentas</li>}
              {registered.map(a => <li key={a.bidder_id}><code>{a.bidder_id}</code></li>)}
            </ul>
          </div>
        </div>

        <div className="card" style={{margin:0}}>
          <h3>Login</h3>
          <p className="muted">Inicia sesión local para filtrar tus notificaciones.</p>
          <div style={{display:'grid', gap:8}}>
            <input placeholder="bidder_id (usuario)" value={lBidder} onChange={e=>setLBidder(e.target.value)} />
            <input placeholder="password" type="password" value={lPass} onChange={e=>setLPass(e.target.value)} />
            <button className="btn" onClick={doLogin}>Entrar</button>
          </div>

          {current && (
            <div style={{marginTop:12}}>
              <div className="muted">Sesión actual:</div>
              <div className="code" style={{marginTop:4}}>{current.bidder_id}</div>
              <button className="btn ghost" style={{marginTop:8}} onClick={doLogout}>Cerrar sesión</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
