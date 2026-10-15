/* "Back to top" appears once the search and filters have scrolled out of view (they scroll away on phones). */
(function () {
  const toTop = document.getElementById("totop"), bar = document.querySelector(".bar");
  if (!toTop || !bar) return;
  function onScroll() { toTop.hidden = bar.getBoundingClientRect().bottom > 0; }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  toTop.onclick = () => {
    const smooth = !matchMedia("(prefers-reduced-motion: reduce)").matches;
    window.scrollTo({ top: 0, behavior: smooth ? "smooth" : "auto" });
  };
})();
