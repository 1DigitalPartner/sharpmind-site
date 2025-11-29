function html(s){ return new Response(s, {headers:{'content-type':'text/html; charset=utf-8'}}); }
function b64urlToBytes(s){
  s = s.replace(/-/g,'+').replace(/_/g,'/');
  const pad = s.length % 4 ? 4 - (s.length % 4) : 0;
  if (pad) s += '='.repeat(pad);
  const bin = atob(s);
  const arr = new Uint8Array(bin.length);
  for (let i=0;i<bin.length;i++) arr[i] = bin.charCodeAt(i);
  return arr;
}
async function hmacSignHexKey(hexKey, dataStr){
  const bytes = new Uint8Array(hexKey.match(/.{1,2}/g).map(h=>parseInt(h,16)));
  const key = await crypto.subtle.importKey('raw', bytes, {name:'HMAC', hash:'SHA-256'}, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(dataStr));
  let bin = ''; const b = new Uint8Array(sig); for (let i=0;i<b.length;i++) bin += String.fromCharCode(b[i]);
  return btoa(bin).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
}
async function mgFetch(env, path, init){
  const headers = init?.headers ? new Headers(init.headers) : new Headers();
  if ((init?.form) && !headers.has('Content-Type')) {
    init.body = new URLSearchParams(init.form);
    headers.set('Content-Type', 'application/x-www-form-urlencoded');
  }
  headers.set('Authorization', 'Basic ' + btoa('api:' + env.MAILGUN_API_KEY));
  return fetch(new URL(path, env.MAILGUN_API_BASE), { ...init, headers });
}
export async function onRequestGet({ request, env }) {
  try{
    for (const k of ['MAILGUN_API_BASE','MAILGUN_API_KEY','MAILGUN_DOMAIN','MAILGUN_FROM','CONFIRM_SIGNING_KEY']){
      if(!env[k]) return html(`<p>Missing ${k}</p>`);
    }
    const url = new URL(request.url);
    const token = url.searchParams.get('token')||'';
    const [p64,sig] = token.split('.');
    if (!p64 || !sig) return html('<p>Token mancante o invalido.</p>');

    const expect = await hmacSignHexKey(env.CONFIRM_SIGNING_KEY, p64);
    if (sig !== expect) return html('<p>Token non valido (firma).</p>');
    const payload = JSON.parse(new TextDecoder().decode(b64urlToBytes(p64)));
    if (!payload.e || !payload.l) return html('<p>Token incompleto.</p>');
    // opzionale: scadenza 72h
    if (Date.now() - (payload.ts||0) > 72*3600*1000) return html('<p>Token scaduto.</p>');

    // Abilita subscribed=yes
    const up = await mgFetch(env, `/v3/lists/${encodeURIComponent(payload.l)}/members`, {
      method:'POST',
      form: { address: payload.e, subscribed: 'yes', upsert: 'yes' }
    });
    if (!up.ok) {
      const t = await up.text();
      return html(`<p>Errore aggiornamento iscrizione: ${t}</p>`);
    }

    // Welcome immediata (facoltativa)
    await mgFetch(env, `/v3/${env.MAILGUN_DOMAIN}/messages`, {
      method:'POST',
      form: {
        from: env.MAILGUN_FROM,
        to: payload.e,
        subject: 'Benvenuto in SharpMind',
        'o:tag': 'welcome',
        text: 'Benvenuto a bordo! A breve riceverai contenuti premium.',
        html: '<h2>Benvenuto in SharpMind</h2><p>A breve riceverai contenuti premium.</p>'
      }
    }).catch(()=>{});

    return html('<h2>Iscrizione confermata ✔</h2><p>Controlla la tua casella: ti abbiamo inviato una welcome.</p>');
  }catch(e){
    return html('<p>Errore server.</p>');
  }
}
