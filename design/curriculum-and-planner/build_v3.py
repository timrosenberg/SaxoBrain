"""Round 3: curriculum mockup without the planner (spun off), one-column listening, no breadcrumb or year counter."""
import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(HERE, f)
t = open(P("template-round2.html"), encoding="utf-8").read()
def cut(s, a, b):
    i = s.index(a); j = s.index(b, i)
    return s[:i] + s[j:]
def rep(s, a, b):
    assert a in s, a[:70]
    return s.replace(a, b)
t = rep(t, "   year page = everything for one year; planner = semesters across, slots down, with a search sheet over the whole catalog.\n", "   year page = everything for one year.\n")
t = re.sub(r"\.myplan[^\n]*\n", "", t)
t = re.sub(r"\.crumbs[^\n]*\n", "", t)
t = re.sub(r"\.y-head \.eyebrow[^\n]*\n", "", t)
t = rep(t, "counter-reset: a; columns: 2 300px; column-gap: 28px; }", "counter-reset: a; }")
t = rep(t, " break-inside: avoid; }", " }")
t = cut(t, "/* ---------- planner ---------- */", "@media (max-width: 820px)")
t = re.sub(r"  \.board[^\n]*\n|  \.slotname[^\n]*\n|  \.slot \.k[^\n]*\n", "", t)
t = rep(t, ".piece, .res, .saved .row { grid-template-columns: 1fr; }", ".piece { grid-template-columns: 1fr; }")
t = rep(t, "body.panel-open { overflow: hidden; }\n", "")
t = rep(t, ".y-head h1 { margin: 2px 0 0; }", ".y-head h1 { margin: 6px 0 0; }")
t = rep(t, "<b>Mockup, round 2</b> · Curriculum and repertoire planner for SaxoBrain", "<b>Mockup, round 3</b> · Curriculum redesign for SaxoBrain")
t = rep(t, '  <a class="myplan" id="myplan" href="#planner">My plan <span class="count" id="plancount">0</span></a>\n', "")
t = rep(t, '<div class="scrim" id="scrim" hidden></div>\n<div class="panel" id="panel" role="dialog" aria-modal="true" aria-labelledby="panel-title" hidden></div>\n', "")
t = rep(t, "const YEARS = DATA.years, CAT = DATA.catalog, SITE = DATA.site;\nconst BY_SLUG = Object.fromEntries(CAT.map(w => [w.s, w]));\n", "const YEARS = DATA.years, SITE = DATA.site;\n")
t = rep(t, 'const app = document.getElementById("app"), panel = document.getElementById("panel"), scrim = document.getElementById("scrim");', 'const app = document.getElementById("app");')
t = cut(t, "const store = {", "const esc =")
t = cut(t, "/* A plan entry is a snapshot", "/* ---------- overview ---------- */")
t = rep(t, """    <div><h3>Plan your semesters</h3><p>Save pieces from the curriculum or anywhere in the catalog, then lay out your fall and spring in <a href="#planner">My plan</a>.</p></div>\n""", "")
t = rep(t, """  const e = entry(p), saved = isSaved(e);\n""", "")
t = rep(t, """\n      <button type="button" class="act save" data-save='${esc(JSON.stringify(e))}' aria-pressed="${saved}">${saved ? "Saved" : "+ Save"}</button></div></li>""", "</div></li>")
t = rep(t, """  <div class="crumbs"><a href="#overview">Curriculum</a><span>/</span><span>${esc(y.name)}</span></div>\n  <div class="y-head"><div class="eyebrow"><span class="dot"></span>Year ${y.n} of 4</div><h1>${esc(y.name)}</h1></div>""",
           """  <div class="y-head"><h1>${esc(y.name)}</h1></div>""")
t = rep(t, """<div class="rule"><p>${esc(ruleText)}</p><a class="btn" href="#planner" data-planyear="${y.n}">Plan your semesters →</a></div>""", """<div class="rule"><p>${esc(ruleText)}</p></div>""")
i = t.index("/* ---------- planner ---------- */")
t = t[:i] + """/* ---------- routing and events ---------- */
function render(scrollTo) {
  const y = YEARS.find(o => o.id === location.hash.slice(1));
  y ? yearPage(y) : overview();
  if (scrollTo) document.getElementById("s-" + scrollTo)?.scrollIntoView();
}
window.addEventListener("hashchange", () => { render(); window.scrollTo(0, 0); });
window.addEventListener("popstate", () => render());
app.addEventListener("click", e => {
  const t = e.target.closest("[data-go],[data-sec]");
  if (!t) return;
  if (t.dataset.go) { history.pushState(null, "", "#" + t.dataset.go); render(t.dataset.sec); }
  else { e.preventDefault(); document.getElementById("s-" + t.dataset.sec)?.scrollIntoView(); }
});
app.addEventListener("keydown", e => { if ((e.key === "Enter" || e.key === " ") && e.target.dataset.go) { e.preventDefault(); e.target.click(); } });
render();
</script>
"""
js = t[t.index("<script>"):]
for bad in ["plan.", "planner", "CAT", "entry(", "isSaved", "crumbs", "of 4", "panel"]:
    assert bad not in js, bad
open(P("template-round3.html"), "w", encoding="utf-8").write(t)
d = json.load(open(P("data2.json"), encoding="utf-8")); d.pop("catalog")
html = t.replace("/*DATA*/", json.dumps(d, ensure_ascii=False, separators=(",", ":")))
open(P("curriculum-mockup.html"), "w", encoding="utf-8").write(html)
print(len(html.encode()))
