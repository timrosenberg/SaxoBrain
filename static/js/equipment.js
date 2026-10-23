/* Progressive controls: the complete guides remain readable without JavaScript. */
(() => {
  const anchor = () => {
    try { return decodeURIComponent(location.hash.slice(1)); } catch { return ""; }
  };

  document.querySelectorAll("[data-equipment-instruments]").forEach(group => {
    const picker = group.querySelector(".equipment-instrument-picker");
    const panels = [...group.querySelectorAll("[data-instrument-panel]")];
    const buttons = [...picker.querySelectorAll("[data-instrument-target]")];
    const select = id => {
      panels.forEach(panel => { panel.hidden = panel.id !== id; });
      buttons.forEach(button => button.setAttribute("aria-pressed", String(button.dataset.instrumentTarget === id)));
    };
    const fromAnchor = () => {
      const match = panels.find(panel => panel.id === anchor());
      if (match) select(match.id);
      return !!match;
    };
    buttons.forEach(button => button.addEventListener("click", () => select(button.dataset.instrumentTarget)));
    if (!fromAnchor()) select(panels.find(panel => panel.id === group.dataset.defaultInstrument)?.id || panels[0]?.id);
    picker.hidden = false;
    window.addEventListener("hashchange", fromAnchor);
  });

  document.querySelectorAll("[data-equipment-symptoms]").forEach(group => {
    const control = group.querySelector(".equipment-symptom-control");
    const select = control.querySelector("select");
    const symptoms = [...group.querySelectorAll("[data-symptom]")];
    symptoms.forEach(symptom => {
      const option = document.createElement("option");
      option.value = symptom.id;
      option.textContent = symptom.querySelector("summary").textContent;
      select.append(option);
    });
    const show = id => {
      symptoms.forEach(symptom => {
        symptom.hidden = !!id && symptom.id !== id;
        if (id && symptom.id === id) symptom.open = true;
      });
    };
    const fromAnchor = () => {
      const match = symptoms.find(symptom => symptom.id === anchor());
      if (!match) return;
      select.value = match.id;
      show(match.id);
      let parent = match.parentElement;
      while (parent) {
        if (parent instanceof HTMLDetailsElement) parent.open = true;
        parent = parent.parentElement;
      }
    };
    select.addEventListener("change", () => show(select.value));
    control.hidden = false;
    fromAnchor();
    window.addEventListener("hashchange", fromAnchor);
  });
})();
