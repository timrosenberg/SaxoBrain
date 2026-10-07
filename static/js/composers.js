/* Filters for the Composers page. The list is already on the page; this hides rows that do not match
   and keeps the filters in the address bar (/composers/?nat=French&lvl=First+Year&women=1). */
(function () {
  const LEVELS = [["Pre-college", "pre"], ["First Year", "1"], ["Second-Year", "2"], ["Third Year", "3"], ["Fourth Year", "4"], ["Advanced", "adv"]];
  const LV_NAME = { "Pre-college": "Pre-college", "First Year": "First year", "Second-Year": "Second year", "Third Year": "Third year", "Fourth Year": "Fourth year", "Advanced": "Advanced" };
  const lvCode = y => (LEVELS.find(l => l[0] === y) || [0, "none"])[1];
  const TOP_NATIONS = 8;
  const fold = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const nf = new Intl.NumberFormat("en-US");
  const $ = id => document.getElementById(id);
  const state = { q: "", nat: new Set(), lvl: new Set(), women: false };

  const rows = [...document.querySelectorAll(".clist li")].map(li => ({
    li,
    hay: fold(li.querySelector(".name").textContent),
    nat: li.dataset.nat ? li.dataset.nat.split("|") : [],
    lv: li.dataset.lv.split(" "),
    w: li.dataset.w === "1"
  }));
  const groups = [...document.querySelectorAll(".letter-group")];
  const letterLinks = [...document.querySelectorAll(".letters a")];

  // Nationality chips: the most common ones by name, everything else under "Other".
  // Stored in the URL without the flag, e.g. nat=French.
  const label = n => n.replace(/^[^A-Za-z]+/, "");
  const counts = new Map();
  rows.forEach(r => r.nat.forEach(n => counts.set(n, (counts.get(n) || 0) + 1)));
  const top = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, TOP_NATIONS).map(e => e[0]);
  const topLabels = new Set(top.map(label));
  const natMatch = (r, v) => v === "Other" ? r.nat.some(n => !topLabels.has(label(n))) : r.nat.some(n => label(n) === v);

  function readUrl() {
    const p = new URLSearchParams(location.search);
    state.q = p.get("q") || "";
    ["nat", "lvl"].forEach(k => p.getAll(k).forEach(v => state[k].add(v)));
    state.women = p.get("women") === "1";
  }
  function writeUrl() {
    const p = new URLSearchParams();
    if (state.q) p.set("q", state.q);
    ["nat", "lvl"].forEach(k => state[k].forEach(v => p.append(k, v)));
    if (state.women) p.set("women", "1");
    const qs = p.toString();
    try { history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + location.hash); } catch (e) {}
  }

  function chip(text, pressed, onclick, cls, dot) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip" + (cls ? " " + cls : "");
    b.innerHTML = dot ? `<span class="dot ${dot}"></span>` : "";
    b.appendChild(document.createTextNode(text));
    b.onclick = onclick; b.pressed = pressed;
    return b;
  }
  function group(name, chips) {
    const g = document.createElement("div");
    g.className = "group";
    g.innerHTML = `<span class="label-sm">${name}</span>`;
    chips.forEach(c => g.appendChild(c));
    return g;
  }
  const toggle = (k, v) => () => { state[k].has(v) ? state[k].delete(v) : state[k].add(v); update(); };
  function buildChips() {
    const box = $("cgroups");
    box.appendChild(group("Nationality", top.map(n => chip(n, () => state.nat.has(label(n)), toggle("nat", label(n))))
      .concat([chip("Other", () => state.nat.has("Other"), toggle("nat", "Other"))])));
    box.appendChild(group("Has works at", LEVELS.map(([v, c]) => chip(LV_NAME[v], () => state.lvl.has(v), toggle("lvl", v), "c-lv-" + c, "lv-" + c))));
    box.appendChild(group("Only show", [chip("Women composers", () => state.women, () => { state.women = !state.women; update(); })]));
  }
  function syncChips() {
    document.querySelectorAll("#cgroups .chip").forEach(b => b.setAttribute("aria-pressed", b.pressed() ? "true" : "false"));
    $("cq").value = state.q;
  }

  function matches(r) {
    if (state.q) { const terms = fold(state.q).split(/\s+/).filter(Boolean); if (!terms.every(t => r.hay.includes(t))) return false; }
    if (state.nat.size && ![...state.nat].some(v => natMatch(r, v))) return false;
    if (state.lvl.size && ![...state.lvl].some(v => r.lv.includes(lvCode(v)))) return false;
    if (state.women && !r.w) return false;
    return true;
  }
  function render() {
    let n = 0;
    rows.forEach(r => { const on = matches(r); r.li.hidden = !on; if (on) n++; });
    const live = new Set();
    groups.forEach(g => { const any = !!g.querySelector("li:not([hidden])"); g.hidden = !any; if (any) live.add(g.dataset.letter); });
    letterLinks.forEach(a => {
      const off = !live.has(a.dataset.letter);
      a.classList.toggle("off", off);
      if (off) a.setAttribute("aria-disabled", "true"); else a.removeAttribute("aria-disabled");
    });
    const active = state.q || state.nat.size || state.lvl.size || state.women;
    $("ccount").textContent = active ? `${nf.format(n)} of ${nf.format(rows.length)} composers` : `${nf.format(rows.length)} composers`;
    $("cclear").hidden = !active;
    $("cempty").hidden = n > 0;
  }
  function update() { syncChips(); writeUrl(); render(); }

  buildChips(); readUrl(); syncChips(); render();
  $("cq").hidden = false;
  let tmr;
  $("cq").addEventListener("input", e => { clearTimeout(tmr); tmr = setTimeout(() => { state.q = e.target.value.trim(); writeUrl(); render(); }, 100); });
  $("cclear").onclick = () => { state.q = ""; state.nat.clear(); state.lvl.clear(); state.women = false; update(); };
  letterLinks.forEach(a => a.addEventListener("click", e => { if (a.classList.contains("off")) e.preventDefault(); }));
})();
