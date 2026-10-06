/* Searchable catalog for the Repertoire page. Reads index.json (built by Hugo), filters in the browser,
   and keeps the filters in the address bar so a search can be shared. */
(function () {
  const LEVELS = [["Pre-college", "pre"], ["First Year", "1"], ["Second-Year", "2"], ["Third Year", "3"], ["Fourth Year", "4"], ["Advanced", "adv"]];
  const LV_NAME = { "Pre-college": "Pre-college", "First Year": "First year", "Second-Year": "Second year", "Third Year": "Third year", "Fourth Year": "Fourth year", "Advanced": "Advanced", "": "No year assigned" };
  const lvClass = y => "lv-" + ((LEVELS.find(l => l[0] === y) || [0, "none"])[1]);
  const SAX = ["Soprano Saxophone", "Alto Saxophone", "Tenor Saxophone", "Baritone Saxophone", "Bass Saxophone"];
  const WITH = ["Piano", "Unaccompanied", "Orchestra", "Band", "Electronics", "Percussion"];
  const short = t => t.replace(" Saxophone", "");
  const fold = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const esc = s => String(s).replace(/[&<>"]/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
  const nf = new Intl.NumberFormat("en-US");
  const $ = id => document.getElementById(id);
  const state = { q: "", sax: new Set(), lvl: new Set(), with: new Set(), rec: false, women: false, jazz: false, etude: false, limit: 60 };
  let W = [];

  function readUrl() {
    const p = new URLSearchParams(location.search);
    state.q = p.get("q") || "";
    ["sax", "lvl", "with"].forEach(k => p.getAll(k).forEach(v => state[k].add(v)));
    state.rec = p.get("rec") === "1";
    state.women = p.get("women") === "1";
    state.jazz = p.get("jazz") === "1";
    state.etude = p.get("etude") === "1";
  }
  function writeUrl() {
    const p = new URLSearchParams();
    if (state.q) p.set("q", state.q);
    ["sax", "lvl", "with"].forEach(k => state[k].forEach(v => p.append(k, v)));
    if (state.rec) p.set("rec", "1");
    if (state.women) p.set("women", "1");
    if (state.jazz) p.set("jazz", "1");
    if (state.etude) p.set("etude", "1");
    const qs = p.toString();
    try { history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + location.hash); } catch (e) {}
  }

  function chipGroup(label, items, setName, fmt, dotClass, tint) {
    const g = document.createElement("div");
    g.className = "group";
    g.innerHTML = `<span class="label-sm">${label}</span>`;
    items.forEach(v => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "chip" + (tint ? " " + tint(v) : ""); b.dataset.set = setName; b.dataset.val = v;
      b.setAttribute("aria-pressed", "false");
      b.innerHTML = (dotClass ? `<span class="dot ${dotClass(v)}"></span>` : "") + esc(fmt(v));
      b.onclick = () => { const s = state[setName]; s.has(v) ? s.delete(v) : s.add(v); state.limit = 60; update(); };
      g.appendChild(b);
    });
    return g;
  }
  function buildChips() {
    const groups = $("groups");
    groups.appendChild(chipGroup("Saxophone", SAX, "sax", short, null, v => "c-sx-" + short(v).toLowerCase()));
    groups.appendChild(chipGroup("Year of study", LEVELS.map(l => l[0]).concat([""]), "lvl", v => LV_NAME[v], lvClass, v => "c-" + lvClass(v)));
    groups.appendChild(chipGroup("With", WITH, "with", v => v));
    const extra = document.createElement("div");
    extra.className = "group";
    extra.innerHTML = `<span class="label-sm">Only show</span>`;
    [["rec", "Has a recording"], ["women", "Women composers"], ["jazz", "Jazz"], ["etude", "Etudes"]].forEach(([key, lab]) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "chip"; b.dataset.flag = key; b.textContent = lab;
      b.setAttribute("aria-pressed", "false");
      b.onclick = () => { state[key] = !state[key]; state.limit = 60; update(); };
      extra.appendChild(b);
    });
    groups.appendChild(extra);
  }
  function syncChips() {
    document.querySelectorAll("#groups .chip").forEach(b => {
      const on = b.dataset.flag ? state[b.dataset.flag] : state[b.dataset.set].has(b.dataset.val);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
    $("q").value = state.q;
  }
  function reset() { state.q = ""; state.sax.clear(); state.lvl.clear(); state.with.clear(); state.rec = false; state.women = false; state.jazz = false; state.etude = false; state.limit = 60; }

  function matches(w) {
    if (state.q) { const terms = fold(state.q).split(/\s+/).filter(Boolean); if (!terms.every(t => w.hay.includes(t))) return false; }
    if (state.sax.size && ![...state.sax].some(s => w.i.includes(s))) return false;
    if (state.lvl.size && !state.lvl.has(w.y)) return false;
    if (state.with.size && ![...state.with].some(s => w.i.includes(s))) return false;
    if (state.rec && !w.s) return false;
    if (state.women && !w.w) return false;
    if (state.jazz && !w.j) return false;
    if (state.etude && !w.e) return false;
    return true;
  }
  function instLine(w) {
    const sax = w.i.filter(t => SAX.includes(t)).map(short);
    const rest = w.i.filter(t => !SAX.includes(t) && t !== "Unaccompanied");
    let s = sax.length ? sax.join(" or ") + " saxophone" : "";
    if (w.i.includes("Unaccompanied")) s += (s ? ", " : "") + "unaccompanied";
    if (rest.length) s += (s ? " with " : "") + rest.join(", ").toLowerCase();
    return s;
  }

  function render() {
    const hits = W.filter(matches);
    const active = state.q || state.sax.size || state.lvl.size || state.with.size || state.rec || state.women || state.jazz || state.etude;
    $("count").textContent = active ? `${nf.format(hits.length)} of ${nf.format(W.length)} works` : `All ${nf.format(W.length)} works, by composer`;
    $("clear").hidden = !active;
    const list = $("list");
    list.innerHTML = hits.length ? "" : `<li class="empty">No works match. Try removing a filter.</li>`;
    const frag = document.createDocumentFragment();
    hits.slice(0, state.limit).forEach(w => {
      const li = document.createElement("li");
      li.innerHTML = `<a class="row" href="${esc(w.u)}"><div class="main"><div><span class="title">${esc(w.t)}</span> <span class="composer">· ${esc(w.c.join(", ") || "Composer unknown")}</span></div>
<div class="meta"><span class="lvl pill c-${lvClass(w.y)}"><span class="dot ${lvClass(w.y)}"></span>${esc(LV_NAME[w.y] || w.y)}</span><span>${esc(instLine(w))}</span></div></div>
<div class="has">${w.s ? '<span class="tag on">Recording</span>' : ""}${w.p ? '<span class="tag on">Score</span>' : ""}</div></a>`;
      frag.appendChild(li);
    });
    list.appendChild(frag);
    const more = $("more");
    more.hidden = hits.length <= state.limit;
    more.textContent = `Show more (${nf.format(Math.max(0, hits.length - state.limit))} left)`;
  }
  function update() { syncChips(); writeUrl(); render(); }


  /* Side panel: a click on a result opens the work in a panel (a sheet on phones). The work keeps its own page
     and address; the panel loads that page and shows its article, so there is one layout to maintain. */
  const panel = $("panel"), scrim = $("scrim");
  let depth = 0, lastRow = null, token = 0;
  function showPanel(article) {
    panel.innerHTML = '<div class="panel-head"><button class="close" type="button" aria-label="Close">\u00d7</button></div>' + article.outerHTML;
    panel.hidden = false; scrim.hidden = false; panel.scrollTop = 0;
    document.body.classList.add("panel-open");
    panel.querySelector(".close").onclick = closePanel;
    panel.focus({ preventScroll: true });
  }
  async function loadWork(url) {
    const mine = ++token;
    const html = await fetch(url).then(r => { if (!r.ok) throw new Error(r.status); return r.text(); });
    if (mine !== token) return;
    const article = new DOMParser().parseFromString(html, "text/html").querySelector("article.work");
    if (!article) throw new Error("no article");
    showPanel(article);
  }
  function openWork(url, row, push) {
    if (row) lastRow = row;
    loadWork(url).then(() => {
      if (push) { try { history.pushState({ work: url }, "", url); depth++; } catch (e) {} }
    }).catch(() => { location.href = url; });
  }
  function hidePanel() {
    token++;
    panel.hidden = true; scrim.hidden = true; panel.innerHTML = "";
    document.body.classList.remove("panel-open");
    if (lastRow && document.contains(lastRow)) lastRow.focus({ preventScroll: true });
  }
  function closePanel() {
    if (panel.hidden) return;
    if (depth > 0) { const n = depth; depth = 0; history.go(-n); } else { hidePanel(); }
  }
  scrim.onclick = closePanel;
  document.addEventListener("keydown", e => { if (e.key === "Escape") closePanel(); });
  window.addEventListener("popstate", e => {
    if (e.state && e.state.work) { loadWork(e.state.work).catch(() => {}); } else { depth = 0; hidePanel(); }
  });
  $("list").addEventListener("click", e => {
    const a = e.target.closest("a.row");
    if (!a || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    openWork(a.href, a, true);
  });
  // links to other works inside the panel stay in the panel; everything else is a normal link
  panel.addEventListener("click", e => {
    const a = e.target.closest("a[href]");
    if (!a || e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const u = new URL(a.href, location.href);
    if (u.origin === location.origin && /\/works\/[^/]+\/$/.test(u.pathname)) { e.preventDefault(); openWork(u.href, null, true); }
  });

  function start(data) {
    W = data;
    W.forEach(w => {
      const n = w.c.length ? w.c[0] : "zzz", parts = n.split(/\s+/);
      w.k = fold(parts[parts.length - 1] + " " + n + " " + w.t);
      w.hay = fold(w.t + " " + w.c.join(" "));
    });
    W.sort((a, b) => a.k.localeCompare(b.k));
    buildChips(); readUrl(); syncChips(); render();
    $("more").onclick = () => { state.limit += 120; render(); };
    $("clear").onclick = () => { reset(); update(); };
    let tmr;
    $("q").addEventListener("input", e => { clearTimeout(tmr); tmr = setTimeout(() => { state.q = e.target.value.trim(); state.limit = 60; writeUrl(); render(); }, 120); });
  }

  fetch(document.currentScript.dataset.index)
    .then(r => r.json()).then(start)
    .catch(() => { $("count").textContent = "The catalog could not load. Browse every work from the Repertoire list instead."; });
})();
