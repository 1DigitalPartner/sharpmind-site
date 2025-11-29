async function subscribe(ev) {
  ev.preventDefault();
  const form = ev.currentTarget;
  const email = form.querySelector('input[name="email"]').value.trim();
  const name  = form.querySelector('input[name="name"]')?.value.trim() || "";
  const btn   = form.querySelector('button[type="submit"]');
  const msgEl = form.querySelector('[data-msg]');

  btn.disabled = true; msgEl.textContent = "Submitting…";

  try {
    const r = await fetch("/api/subscribe", {
      method: "POST",
      headers: { "content-type":"application/json" },
      body: JSON.stringify({ email, name })
    });
    const j = await r.json();
    if (j.ok) {
      msgEl.textContent = "You're in. Check your inbox.";
      form.reset();
    } else {
      msgEl.textContent = "Error: " + (j.error || "try again");
    }
  } catch (e) {
    msgEl.textContent = "Network error. Retry.";
  } finally {
    btn.disabled = false;
  }
}

window.addEventListener("DOMContentLoaded", () => {
  const f = document.getElementById("newsletter-form");
  if (f) f.addEventListener("submit", subscribe);
});
