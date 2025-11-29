export const b64u = {
  enc(buf){ return btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,''); },
  dec(str){ str=str.replace(/-/g,'+').replace(/_/g,'/'); const pad = str.length%4 ? 4-(str.length%4) : 0; str += '='.repeat(pad); const bin = atob(str); const out = new Uint8Array(bin.length); for(let i=0;i<bin.length;i++) out[i]=bin.charCodeAt(i); return out.buffer; },
  encText(txt){ return btoa(unescape(encodeURIComponent(txt))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,''); },
  decText(txt){ txt=txt.replace(/-/g,'+').replace(/_/g,'/'); const pad = txt.length%4 ? 4-(txt.length%4) : 0; txt += '='.repeat(pad); return decodeURIComponent(escape(atob(txt))); }
};

export async function getHmacKey(secret){
  const keyBytes = new TextEncoder().encode(secret);
  return crypto.subtle.importKey('raw', keyBytes, {name:'HMAC', hash:'SHA-256'}, false, ['sign','verify']);
}

export async function signToken(payloadObj, secret){
  const key = await getHmacKey(secret);
  const payload = JSON.stringify(payloadObj);
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(payload));
  return b64u.encText(payload) + '.' + b64u.enc(sig);
}

export async function verifyToken(token, secret){
  const [p,s] = (token||'').split('.');
  if(!p || !s) return null;
  const payload = b64u.decText(p);
  const key = await getHmacKey(secret);
  const ok = await crypto.subtle.verify('HMAC', key, b64u.dec(s), new TextEncoder().encode(payload));
  if(!ok) return null;
  return JSON.parse(payload);
}

export function basicAuth(user, pass){
  return 'Basic ' + btoa(`${user}:${pass}`);
}

export async function mgFetch(env, path, {method='GET', form=null}={}){
  const url = `${env.MAILGUN_API_BASE}${path}`;
  const headers = { 'Authorization': basicAuth('api', env.MAILGUN_API_KEY) };
  let body, h2 = {};
  if(form){
    body = new URLSearchParams(form);
    h2['Content-Type'] = 'application/x-www-form-urlencoded';
  }
  const r = await fetch(url, { method, headers:{...headers, ...h2}, body });
  return r;
}

export function parseContext(request){
  const url = new URL(request.url);
  const headers = Object.fromEntries(request.headers.entries());
  return {
    origin: url.origin,
    search: url.searchParams,
    referer: headers['referer'] || headers['referrer'] || '',
    utm: {
      source: url.searchParams.get('utm_source') || '',
      medium: url.searchParams.get('utm_medium') || '',
      campaign: url.searchParams.get('utm_campaign') || '',
      term: url.searchParams.get('utm_term') || '',
      content: url.searchParams.get('utm_content') || '',
    }
  };
}
