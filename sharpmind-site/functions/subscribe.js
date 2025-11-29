export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const ct = request.headers.get("content-type") || "";
  let payload = {};
  try {
    if (ct.includes("application/json")) {
      payload = await request.json();
    } else if (ct.includes("application/x-www-form-urlencoded") || ct.includes("multipart/form-data")) {
      const form = await request.formData();
      payload.email = form.get("email");
      payload.name = form.get("name") || "";
    }
  } catch {}

  const email = (payload.email || "").trim().toLowerCase();
  if (!email || !/^\S+@\S+\.\S+$/.test(email)) {
    return json({ ok: false, error: "invalid_email" }, 400);
  }

  const key = env.MAILGUN_API_KEY;
  const domain = env.MAILGUN_DOMAIN;
  const list = env.NEWSLETTER_LIST || "";   // es. newsletter@tanzitech.com
  if (!key || !domain) return json({ ok: false, error: "missing_mailgun_env" }, 500);

  // 1) se hai una LIST, aggiunge/upserta il membro
  if (list) {
    const url = `https://api.mailgun.net/v3/lists/${encodeURIComponent(list)}/members`;
    const body = new URLSearchParams();
    body.set("address", email);
    body.set("name", payload.name || "");
    body.set("subscribed", "yes");
    body.set("upsert", "yes");

    const r = await fetch(url, {
      method: "POST",
      headers: { Authorization: "Basic " + btoa("api:" + key) },
      body,
    });
    if (!r.ok) {
      const txt = await r.text();
      return json({ ok: false, error: "mailgun_failed", details: txt }, 502);
    }
  }

  // 2) opzionale: invia email di benvenuto (se MAILGUN_FROM è configurato)
  if (env.MAILGUN_FROM) {
    const url = `https://api.mailgun.net/v3/${domain}/messages`;
    const body = new URLSearchParams();
    body.set("from", env.MAILGUN_FROM);
    body.set("to", email);
    body.set("subject", "Welcome to SharpMind");
    body.set("text", "Grazie per l’iscrizione a SharpMind. Da oggi riceverai 1 insight premium al giorno.");
    await fetch(url, { method: "POST", headers: { Authorization: "Basic " + btoa("api:" + key) }, body });
  }

  return json({ ok: true }, 200);
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", "Access-Control-Allow-Origin": "*" },
  });
}
