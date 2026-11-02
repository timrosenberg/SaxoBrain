(() => {
  const nav = document.querySelector('.site-head nav');
  const toggle = nav?.querySelector('.nav-toggle');
  if (!toggle) return;

  const phone = window.matchMedia('(max-width: 620px)');
  const close = () => toggle.setAttribute('aria-expanded', 'false');

  toggle.addEventListener('click', () => {
    toggle.setAttribute('aria-expanded', String(toggle.getAttribute('aria-expanded') !== 'true'));
  });

  nav.addEventListener('keydown', event => {
    if (event.key === 'Escape' && phone.matches && toggle.getAttribute('aria-expanded') === 'true') {
      close();
      toggle.focus();
    }
  });

  document.addEventListener('click', event => {
    if (!nav.contains(event.target)) close();
  });

  phone.addEventListener('change', close);
  toggle.hidden = false;
  nav.classList.add('nav-ready');
})();
