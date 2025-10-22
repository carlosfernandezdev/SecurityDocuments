const API = import.meta.env.VITE_API_BASE || "http://localhost:8001"
export async function api(url, opts = {}) {
  const res = await fetch(API + url, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(opts.headers||{}) },
    ...opts
  })
  if (!res.ok) {
    const msg = await res.text().catch(()=>res.statusText)
    throw new Error(msg || res.statusText)
  }
  const ct = res.headers.get('content-type')||''
  return ct.includes('application/json') ? res.json() : res.text()
}
export { API }
