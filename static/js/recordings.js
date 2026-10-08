/* Albums / List switch on the Recordings page. Both views are already on the page; this shows one
   and keeps the choice in the address bar (/recordings/?view=list; albums are the default). */
(function () {
  const bar = document.querySelector(".views");
  if (!bar) return;
  const buttons = [...bar.querySelectorAll("[data-view]")];
  const panels = [...document.querySelectorAll("[data-view-panel]")];

  function show(view) {
    buttons.forEach(b => b.setAttribute("aria-pressed", b.dataset.view === view ? "true" : "false"));
    panels.forEach(p => { p.hidden = p.dataset.viewPanel !== view; });
  }

  bar.addEventListener("click", e => {
    const b = e.target.closest("[data-view]");
    if (!b) return;
    show(b.dataset.view);
    const url = new URL(location.href);
    if (b.dataset.view === "albums") url.searchParams.delete("view"); else url.searchParams.set("view", b.dataset.view);
    history.replaceState(null, "", url);
  });

  const v = new URLSearchParams(location.search).get("view");
  show(buttons.some(b => b.dataset.view === v) ? v : "albums");
  bar.hidden = false;
})();
