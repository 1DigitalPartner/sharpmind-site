function J(body, status=200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store', 'access-control-allow-origin': '*' }
  });
}

export async function onRequestGet({ env }) {
  try {
    const base = env.MAILGUN_API_BASE || 'https://api.eu.mailgun.net';
    const key  = env.MAILGUN_API_KEY;
    if (!key) return J({ ok:false, error:'missing_key' }, 500);

    const auth = 'Basic ' + btoa(`api:${key}`);
    const url  = `${base}/v3/lists`;
    const r = await fetch(url, { headers: { Authorization: auth } });
    const t = await r.text();
    return J({ ok:true, status:r.status, bodyPreview: t.slice(0,200) });
  } catch (e) {
    return J({ ok:false, error:'fetch_failed', detail:String(e) }, 502);
  }
}
