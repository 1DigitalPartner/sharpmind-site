export async function onRequestGet({ env }) {
  return new Response(JSON.stringify({
    ok: true,
    env: {
      MAILGUN_API_BASE: !!env.MAILGUN_API_BASE,
      MAILGUN_API_KEY:  (env.MAILGUN_API_KEY||'').length,
      MAILGUN_DOMAIN:   !!env.MAILGUN_DOMAIN,
      MAILGUN_FROM:     !!env.MAILGUN_FROM,
      NEWSLETTER_LIST:  !!env.NEWSLETTER_LIST,
      CONFIRM_SIGNING_KEY: (env.CONFIRM_SIGNING_KEY||'').length
    }
  }), { headers:{ 'content-type':'application/json' }});
}
