// Calls.jsx
export default function Calls({ items }) {
  return (
    <table className="table">
      <thead>
        <tr>
          <th>call_id</th>
          <th>key_id</th>
          <th>RSA pública</th>
        </tr>
      </thead>
      <tbody>
        {items.length === 0 && (
          <tr>
            <td colSpan={3} className="muted">Sin convocatorias</td>
          </tr>
        )}
        {items.map((c) => (
          <tr key={`${c.call_id}-${c.key_id}`}>
            <td className="code">{c.call_id}</td>
            <td className="code">{c.key_id}</td>
            <td>
              <pre className="code" style={{ whiteSpace: 'pre-wrap', maxHeight: 120, overflow: 'auto' }}>
                {c.rsa_pub_pem || '(sin publicar)'}
              </pre>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
