/* Searchable catalog for the Repertoire page. Reads index.json (built by Hugo), filters in the browser,
   and keeps the filters in the address bar so a search can be shared. */
(function () {
  // Visible text lives in content/Site Text (keys js-*), embedded by baseof.html.
  const T = JSON.parse(document.getElementById("site-text").textContent);
  const fill = (s, v) => s.replace(/\{(\w+)\}/g, (m, k) => k in v ? v[k] : m);
  const LEVELS = [["Pre-college", "pre"], ["First Year", "1"], ["Second Year", "2"], ["Third Year", "3"], ["Fourth Year", "4"], ["Advanced", "adv"]];
  const LV_NAME = { "Pre-college": T["level-pre-college"], "First Year": T["level-first-year"], "Second Year": T["level-second-year"], "Third Year": T["level-third-year"], "Fourth Year": T["level-fourth-year"], "Advanced": T["level-advanced"], "": T["level-unassigned"] };
  const lvClass = y => "lv-" + ((LEVELS.find(l => l[0] === y) || [0, "none"])[1]);
  const SAX = ["Soprano Saxophone", "Alto Saxophone", "Tenor Saxophone", "Baritone Saxophone", "Bass Saxophone"];
  const WITH = ["Piano", "Unaccompanied", "Orchestra", "Band", "Electronics", "Percussion"];
  // Sort orders: composer (last name), title (ignoring a leading article), year of study (then composer), newest additions (date added, newest first).
  const SORTS = { composer: { key: "k", label: T["js-sortname-composer"] }, title: { key: "tk", label: T["js-sortname-title"] }, level: { key: "lk", label: T["js-sortname-level"] }, added: { key: "ak", label: T["js-sortname-added"] } };
  const short = t => t.replace(" Saxophone", "");
  const saxName = t => T["js-sax-" + short(t).toLowerCase()];
  const withName = t => T["js-with-" + t.toLowerCase()] || t;
  const fold = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const esc = s => String(s).replace(/[&<>"]/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
  const nf = new Intl.NumberFormat("en-US");
  const $ = id => document.getElementById(id);
  const state = { q: "", sax: new Set(), lvl: new Set(), with: new Set(), rec: false, women: false, poc: false, jazz: false, etude: false, sort: "composer", limit: 60 };
  let W = [];

  function readUrl() {
    const p = new URLSearchParams(location.search);
    state.q = p.get("q") || "";
    ["sax", "lvl", "with"].forEach(k => p.getAll(k).forEach(v => state[k].add(v)));
    state.rec = p.get("rec") === "1";
    state.women = p.get("women") === "1";
    state.poc = p.get("poc") === "1";
    state.jazz = p.get("jazz") === "1";
    state.etude = p.get("etude") === "1";
    state.sort = SORTS[p.get("sort")] ? p.get("sort") : "composer";
  }
  function writeUrl() {
    const p = new URLSearchParams();
    if (state.q) p.set("q", state.q);
    ["sax", "lvl", "with"].forEach(k => state[k].forEach(v => p.append(k, v)));
    if (state.rec) p.set("rec", "1");
    if (state.women) p.set("women", "1");
    if (state.poc) p.set("poc", "1");
    if (state.jazz) p.set("jazz", "1");
    if (state.etude) p.set("etude", "1");
    if (state.sort !== "composer") p.set("sort", state.sort);
    const qs = p.toString();
    try { history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + location.hash); } catch (e) {}
  }

  function chipGroup(label, items, setName, fmt, dotClass, tint) {
    const g = document.createElement("div");
    g.className = "group";
    g.innerHTML = `<span class="label-sm">${esc(label)}</span>`;
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
    groups.appendChild(chipGroup(T["js-group-saxophone"], SAX, "sax", saxName, null, v => "c-sx-" + short(v).toLowerCase()));
    groups.appendChild(chipGroup(T["js-group-level"], LEVELS.map(l => l[0]).concat([""]), "lvl", v => LV_NAME[v], lvClass, v => "c-" + lvClass(v)));
    groups.appendChild(chipGroup(T["js-group-with"], WITH, "with", withName));
    const extra = document.createElement("div");
    extra.className = "group";
    extra.innerHTML = `<span class="label-sm">${esc(T["js-group-only"])}</span>`;
    ["rec", "women", "poc", "jazz", "etude"].forEach(key => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "chip"; b.dataset.flag = key; b.textContent = T["js-flag-" + key];
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
    $("sort").value = state.sort;
  }
  function reset() { state.q = ""; state.sax.clear(); state.lvl.clear(); state.with.clear(); state.rec = false; state.women = false; state.poc = false; state.jazz = false; state.etude = false; state.limit = 60; }

  function matches(w) {
    if (state.q) { const terms = fold(state.q).split(/\s+/).filter(Boolean); if (!terms.every(t => w.hay.includes(t))) return false; }
    if (state.sax.size && ![...state.sax].some(s => w.i.includes(s))) return false;
    if (state.lvl.size && !state.lvl.has(w.y)) return false;
    if (state.with.size && ![...state.with].some(s => w.i.includes(s))) return false;
    if (state.rec && !w.s) return false;
    if (state.women && !w.w) return false;
    if (state.poc && !w.o) return false;
    if (state.jazz && !w.j) return false;
    if (state.etude && !w.e) return false;
    return true;
  }
  function instLine(w) {
    const sax = w.i.filter(t => SAX.includes(t)).map(saxName);
    const rest = w.i.filter(t => !SAX.includes(t) && t !== "Unaccompanied");
    let s = sax.length ? fill(T["js-catalog-inst-saxophone"], { list: sax.join(" " + T["js-catalog-inst-or"] + " ") }) : "";
    if (w.i.includes("Unaccompanied")) s += (s ? ", " : "") + T["js-catalog-inst-unaccompanied"];
    if (rest.length) s += (s ? " " + T["js-catalog-inst-with"] + " " : "") + rest.join(", ").toLowerCase().replace(/\(([a-z]+)\)/g, (m, g) => "(" + g.toUpperCase() + ")");
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  function render() {
    const hits = W.filter(matches);
    const active = state.q || state.sax.size || state.lvl.size || state.with.size || state.rec || state.women || state.poc || state.jazz || state.etude;
    $("count").textContent = fill(T[active ? "js-catalog-count-filtered" : "js-catalog-count-all"], { count: nf.format(hits.length), total: nf.format(W.length), sort: SORTS[state.sort].label });
    $("clear").hidden = !active;
    const list = $("list");
    list.innerHTML = hits.length ? "" : `<li class="empty">${esc(T["js-catalog-empty"])}</li>`;
    const frag = document.createDocumentFragment();
    hits.slice(0, state.limit).forEach(w => {
      const li = document.createElement("li");
      li.innerHTML = `<a class="row" href="${esc(w.u)}"><div class="main"><div><span class="title">${esc(w.t)}${w.d ? ` (${esc(w.d)})` : ""}</span> <span class="composer">· ${esc(w.c.join(", ") || T["js-catalog-composer-unknown"])}</span></div>
<div class="meta"><span class="lvl pill c-${lvClass(w.y)}"><span class="dot ${lvClass(w.y)}"></span>${esc(LV_NAME[w.y] || w.y)}</span><span>${esc(instLine(w))}</span></div></div>
<div class="has">${w.s ? '<span class="tag on">' + esc(T["js-catalog-tag-recording"]) + '</span>' : ""}${w.p ? '<span class="tag on">' + esc(T["js-catalog-tag-score"]) + '</span>' : ""}</div></a>`;
      frag.appendChild(li);
    });
    list.appendChild(frag);
    const more = $("more");
    more.hidden = hits.length <= state.limit;
    more.textContent = fill(T["js-catalog-show-more"], { count: nf.format(Math.max(0, hits.length - state.limit)) });
  }
  function update() { syncChips(); writeUrl(); render(); }
  function applySort() { const key = SORTS[state.sort].key; W.sort((a, b) => a[key].localeCompare(b[key])); }


  /* Side panel: a click on a result opens the work in a panel (a sheet on phones). The work keeps its own page
     and address; the panel loads that page and shows its article, so there is one layout to maintain. */
  const panel = $("panel"), scrim = $("scrim");
  let depth = 0, lastRow = null, token = 0;
  function showPanel(article) {
    panel.innerHTML = '<div class="panel-head"><button class="close" type="button" aria-label="' + esc(T["js-catalog-close"]) + '">\u00d7</button></div>' + article.outerHTML;
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
    if (u.origin === location.origin && u.pathname === location.pathname && u.hash) {
      const target = Array.from(panel.querySelectorAll("[id]")).find(el => "#" + el.id === u.hash);
      if (target) { e.preventDefault(); target.scrollIntoView({ block: "start" }); return; }
    }
    if (u.origin === location.origin && /\/works\/[^/]+\/$/.test(u.pathname)) { e.preventDefault(); openWork(u.href, null, true); }
  });

  function start(data) {
    W = data;
    W.forEach(w => {
      const n = w.c.length ? w.c[0] : "zzz", parts = n.split(/\s+/);
      w.k = fold((w.l || parts[parts.length - 1]) + " " + n + " " + w.t);
      w.hay = fold(w.t + " " + w.c.join(" "));
      w.tk = fold(w.t.replace(/^[^\p{L}\p{N}]+/u, "").replace(/^(?:(?:the|a|an|le|la|les)\s+|l['’])/i, "")) + " " + w.k;
      const li = LEVELS.findIndex(l => l[0] === w.y);
      w.lk = (li < 0 ? 9 : li) + " " + w.k;
      w.ak = (99999999 - Number((w.a || "0").slice(0, 10).replace(/-/g, "") || 0)) + " " + w.k;
    });
    buildChips(); readUrl(); applySort(); syncChips(); render();
    document.querySelector(".sort").hidden = false;
    $("sort").onchange = e => { state.sort = e.target.value; state.limit = 60; applySort(); update(); };
    $("more").onclick = () => { state.limit += 120; render(); };
    $("clear").onclick = () => { reset(); update(); };
    let tmr;
    $("q").addEventListener("input", e => { clearTimeout(tmr); tmr = setTimeout(() => { state.q = e.target.value.trim(); state.limit = 60; writeUrl(); render(); }, 120); });
  }

  fetch(document.currentScript.dataset.index)
    .then(r => r.json()).then(start)
    .catch(() => { $("count").textContent = T["js-catalog-error"]; });
})();
