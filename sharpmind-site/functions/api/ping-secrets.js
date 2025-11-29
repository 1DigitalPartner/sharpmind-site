export async function onRequestGet({ env }) {
  const keys = ["MAILGUN_API_BASE","MAILGUN_API_KEY","NEWSLETTER_LIST","MAILGUN_FROM"];
  const present = Object.fromEntries(keys.map(k => [k, !!env[k]]));
  return new Response(JSON.stringify({ ok:true, present }), { headers:{ "content-type":"application/json" }});
}
