export async function onRequest(context) {
  const { request, env, next } = context;
  const url  = new URL(request.url);
  const path = url.pathname;

  // MAINTENANCE toggle (set MAINTENANCE=1 per attivare)
  const maintenance = (env.MAINTENANCE || '').trim() === '1';

  // Allowlist: API vitali, asset, file tecnici
  const ALLOW = [ /^\/api\/httpcheck(\/|$)/,
    /^\/api\/(ping|subscribe)(\/|$)/,
    /^\/assets\//,
    /^\/favicon\.ico$/,
    /^\/robots\.txt$/,
    /^\/sitemap\.xml$/,
    /^\/_edge_check\.txt$/,
    /^\/cdn-cgi\//
  ];

  const allowed = ALLOW.some(r => r.test(path));
  if (!maintenance || allowed) {
    return next(); // passa alla build normale / altre funzioni
  }

  // Maintenance page (EN) con CTA line
  const html = `<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>We’re Shipping Upgrades</title>
<meta name="robots" content="noindex,nofollow">
<style>
  body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:#0f172a;color:#e5e7eb;display:grid;place-items:center;min-height:100vh}
  .card{max-width:680px;padding:28px;border-radius:16px;background:#111827;border:1px solid #1f2937;box-shadow:0 10px 30px rgba(0,0,0,.35)}
  h1{margin:0 0 10px 0;font-size:28px}
  p{margin:0 0 14px 0;line-height:1.55}
  form{margin-top:12px;display:flex;gap:8px;flex-wrap:wrap}
  input[type=email]{padding:10px 12px;border-radius:10px;border:1px solid #334155;background:#0b1220;color:#e5e7eb;min-width:260px}
  button{padding:10px 16px;border-radius:10px;background:#4F46E5;color:#fff;border:0;font-weight:600;cursor:pointer}
  .msg{margin-left:8px;font-size:14px}
</style>
<div class="card">
  <h1>We’re Shipping Upgrades</h1>
  <p>We’re rolling out major improvements to SharpMind. The site is temporarily in maintenance mode while we complete deployment. APIs and newsletter sign-ups remain available.</p>
  <p><strong>Want a heads-up when we’re back?</strong> Join the newsletter below.</p>

  <form id="nl" onsubmit="return subscribe(event)">
    <input type="email" name="email" placeholder="you@example.com" required>
    <button type="submit">Subscribe</button>
    <span id="nl-msg" class="msg"></span>
  </form>
</div>
<script>
async function subscribe(e){
  e.preventDefault();
  const f=e.target, m=document.getElementById('nl-msg');
  if(!f.email.value){ m.textContent='Please enter a valid email.'; return false; }
  m.textContent='Sending…';
  try{
    const r=await fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},
                body:JSON.stringify({email:f.email.value,website:f.website?.value||''})});
    const j=await r.json().catch(()=>({}));
    if(r.ok && j.ok){ m.textContent='Almost done—check your inbox to confirm.'; f.reset(); }
    else{ m.textContent='Subscription failed. Please try again.'; }
  }catch{ m.textContent='Network error. Please try again.'; }
  return false;
}
</script>
</html>`;
  return new Response(html, {
    status: 503,
    headers: {
      'content-type': 'text/html; charset=utf-8',
      'cache-control': 'no-store',
      'retry-after': '3600',
      'x-robots-tag': 'noindex, nofollow'
    }
  });
}
