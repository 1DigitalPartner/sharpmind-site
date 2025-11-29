export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const p = url.pathname;

  // bypass (asset, api, la pagina stessa)
  const bypass =
    p.startsWith("/assets/") ||
    p.startsWith("/api/")    ||
    p === "/coming-soon.html" ||
    p === "/favicon.ico" ||
    p.startsWith("/cdn-cgi/");

  // flag globale
  if (env.MAINTENANCE === "on" && !bypass) {
    // prendi l'asset statico della pagina coming-soon
    const res = await env.ASSETS.fetch(new Request(new URL("/coming-soon.html", url.origin)));
    const ct = res.headers.get("content-type") || "text/html; charset=utf-8";
    return new Response(res.body, {
      status: 503,
      headers: {
        "content-type": ct,
        "cache-control": "no-store",
        "retry-after": "3600",
        "x-robots-tag": "noindex, nofollow"
      }
    });
  }

  // normale
  return context.next();
}
