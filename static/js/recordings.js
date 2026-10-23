/* Search and Albums / List switch. Filter the existing HTML and keep the query and view in the URL. */
(function () {
  const bar = document.querySelector(".recordings-index .views");
  if (!bar) return;
  const buttons = [...bar.querySelectorAll("[data-view]")];
  const panels = [...document.querySelectorAll("[data-view-panel]")];
  const search = document.getElementById("rq");
  const clear = document.getElementById("rclear");
  const text = JSON.parse(document.getElementById("site-text").textContent);
  const fold = s => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  const rows = panels.map(panel => [...panel.querySelectorAll("li")].map(li => ({ li, hay: fold(li.dataset.search) })));
  let view = "albums";

  function render() {
    const terms = fold(search.value).split(/\s+/).filter(Boolean);
    buttons.forEach(b => b.setAttribute("aria-pressed", b.dataset.view === view ? "true" : "false"));
    panels.forEach((panel, i) => {
      panel.hidden = panel.dataset.viewPanel !== view;
      let count = 0;
      rows[i].forEach(row => {
        row.li.hidden = !terms.every(term => row.hay.includes(term));
        if (!row.li.hidden) count++;
      });
      if (!panel.hidden) {
        document.getElementById("rcount").textContent = text["js-recordings-count"].replace("{count}", count).replace("{total}", rows[i].length);
        document.getElementById("rempty").hidden = count > 0;
      }
    });
    clear.hidden = terms.length === 0;
  }

  function update() {
    render();
    const url = new URL(location.href);
    if (view === "albums") url.searchParams.delete("view"); else url.searchParams.set("view", view);
    const query = search.value.trim();
    if (query) url.searchParams.set("q", query); else url.searchParams.delete("q");
    history.replaceState(null, "", url);
  }

  bar.addEventListener("click", e => {
    const b = e.target.closest("[data-view]");
    if (!b) return;
    view = b.dataset.view;
    update();
  });

  search.addEventListener("input", update);
  clear.addEventListener("click", () => { search.value = ""; update(); search.focus(); });
  const params = new URLSearchParams(location.search);
  const v = params.get("view");
  view = buttons.some(b => b.dataset.view === v) ? v : "albums";
  search.value = params.get("q") || "";
  render();
  document.getElementById("rcontrols").hidden = false;
  document.getElementById("rstatus").hidden = false;
})();
