(async function(){
  const q = document.getElementById('q'), res = document.getElementById('res');
  const idx = await fetch('/api/search.json').then(r=>r.json()).then(j=>j.items||[]);
  function render(list){
    res.innerHTML = list.map(it=>`
      <div class="item">
        <a href="${it.url}"><b>${it.title}</b></a>
        <div style="opacity:.8;font-size:.9rem">${(it.tags||[]).join(' · ')} — ${it.date||""}</div>
        <p style="margin:8px 0 0">${it.excerpt||""}</p>
      </div>`).join('');
  }
  q.addEventListener('input',()=>{
    const s = q.value.trim().toLowerCase();
    if(!s){ render(idx.slice(0,20)); return; }
    render(idx.filter(it=> (it.title||"").toLowerCase().includes(s)
      || (it.excerpt||"").toLowerCase().includes(s)
      || (it.tags||[]).join(" ").toLowerCase().includes(s)
    ).slice(0,50));
  });
  render(idx.slice(0,20));
})();
