import { mgFetch } from './_helpers';

export async function onRequestGet({ request, env }){
  if((env.DEBUG_SUBSCRIBE||'0')!=='1') return new Response('forbidden', {status:403});
  const email = new URL(request.url).searchParams.get('email')||'';
  if(!email) return new Response(JSON.stringify({ok:false,error:'missing_email'}),{status:400});
  const r = await mgFetch(env, `/v3/lists/${encodeURIComponent(env.NEWSLETTER_LIST)}/members/${encodeURIComponent(email)}`, {
    method:'PUT', form:{ subscribed:'yes', upsert:'yes' }
  });
  return new Response(JSON.stringify({ok:r.ok,status:r.status}), {headers:{'content-type':'application/json'}});
}
