import httpx
from ..config import settings

async def fetch_calls_with_pubkeys():
    url = f"{settings.CONVOCANTE_BASE}/api/calls"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=20)
        r.raise_for_status()
        calls = r.json()
        out = []
        for c in calls:
            key_id = c.get("key_id")
            call_id = c.get("call_id")
            pub = ""
            try:
                r2 = await client.get(f"{settings.CONVOCANTE_BASE}/public/keys/{call_id}/{key_id}/rsa_pub.pem", timeout=20)
                if r2.status_code == 200:
                    pub = r2.text
            except Exception:
                pub = ""
            out.append({**c, "rsa_pub_pem": pub})
        return out