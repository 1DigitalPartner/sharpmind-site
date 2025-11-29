export async function onRequestPost({ request, env }) {
  try {
    const { email, name = "", source = "site" } = await request.json();
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return new Response(JSON.stringify({ ok:false, error:"invalid_email" }), { status: 400 });
    }

    const list   = env.NEWSLETTER_LIST;                // es. insights@tanzitech.com
    const apiKey = env.MAILGUN_API_KEY;
    const apiBase= env.MAILGUN_API_BASE || "https://api.mailgun.net";

    const body = new URLSearchParams({
      address: email,
      name,
      subscribed: "yes",
      upsert: "yes",
      vars: JSON.stringify({ source, t: Date.now() })
    });

    const res = await fetch(`${apiBase}/v3/lists/${encodeURIComponent(list)}/members`, {
      method: "POST",
      headers: { "Authorization": "Basic " + btoa("api:" + apiKey) },
      body
    });

    if (!res.ok) {
      const text = await res.text();
      return new Response(JSON.stringify({ ok:false, error:"mailgun_error", detail:text }), { status: 502 });
    }
    return new Response(JSON.stringify({ ok:true }), { headers:{ "content-type":"application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ ok:false, error:"server_error" }), { status: 500 });
  }
}
