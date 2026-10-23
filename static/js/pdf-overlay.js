// PDF.js is imported only when a reader opens a document.
const dialog = document.getElementById('pdf-overlay');
const container = document.getElementById('pdf-container');
const status = document.getElementById('pdf-status');
const pageLabel = document.getElementById('pdf-page');
const previous = document.getElementById('pdf-previous');
const next = document.getElementById('pdf-next');
const zoomOut = document.getElementById('pdf-zoom-out');
const zoomIn = document.getElementById('pdf-zoom-in');
const fit = document.getElementById('pdf-fit');
const image = document.getElementById('viewer-image');
const pages = document.getElementById('pdf-pages');
const paging = previous.parentElement;
const controls = [previous, next, zoomOut, zoomIn, fit];
const text = JSON.parse(document.getElementById('site-text').textContent);
const vendor = new URL('../vendor/pdfjs/6.4.299/', import.meta.url);
let libraryPromise;
let viewer;
let task;
let session = 0;
let opener;
let scrollY = 0;
let historyEntry;
let imageMode = false;
let imageReady = false;
let imageScale = 1;

function updateControls() {
  if (imageMode) {
    [zoomOut, zoomIn, fit].forEach(control => { control.disabled = !imageReady; });
    zoomOut.disabled = !imageReady || imageScale <= 0.2;
    zoomIn.disabled = !imageReady || imageScale >= 4;
    return;
  }
  const ready = dialog.open && !!viewer?.pagesCount;
  controls.forEach(control => { control.disabled = !ready; });
  if (!ready) return;
  const page = viewer.currentPageNumber;
  const count = viewer.pagesCount;
  pageLabel.textContent = `${page} / ${count}`;
  pageLabel.setAttribute('aria-label', text['js-pdf-page'].replace('{page}', page).replace('{count}', count));
  previous.disabled = page === 1;
  next.disabled = page === count;
  zoomOut.disabled = viewer.currentScale <= 0.2;
  zoomIn.disabled = viewer.currentScale >= 4;
}

function showError() {
  status.textContent = text[imageMode ? 'js-image-error' : 'js-pdf-error'];
  status.hidden = false;
  container.setAttribute('aria-busy', 'false');
}

async function loadLibrary() {
  if (!libraryPromise) {
    libraryPromise = (async () => {
      const core = await import(new URL('build/pdf.min.mjs', vendor));
      core.GlobalWorkerOptions.workerSrc = new URL('build/pdf.worker.min.mjs', vendor).href;
      const { EventBus, PDFViewer, PDFLinkService } = await import(new URL('web/pdf_viewer.mjs', vendor));
      const eventBus = new EventBus();
      const linkService = new PDFLinkService({ eventBus, externalLinkTarget: 2 });
      viewer = new PDFViewer({
        container,
        viewer: document.getElementById('pdf-pages'),
        eventBus,
        linkService,
        imageResourcesPath: new URL('web/images/', vendor).href,
        maxCanvasPixels: 8 * 1024 * 1024,
      });
      linkService.setViewer(viewer);
      eventBus.on('pagesinit', () => {
        viewer.currentScaleValue = 'page-width';
        updateControls();
      });
      eventBus.on('pagechanging', updateControls);
      eventBus.on('scalechanging', updateControls);
      eventBus.on('pagerendered', ({ error }) => {
        if (!dialog.open || imageMode) return;
        if (error) return showError();
        status.hidden = true;
        container.setAttribute('aria-busy', 'false');
      });
      // Use PDF.js's touch recognizer so pinching zooms the document while the toolbar stays put.
      new core.TouchManager({
        container,
        signal: new AbortController().signal,
        isPinchingDisabled: () => !dialog.open || imageMode || !viewer.pdfDocument,
        onPinching: (origin, before, after, panX, panY) => {
          const scale = Math.max(0.2, Math.min(4, viewer.currentScale * after / before));
          viewer.updateScale({ scaleFactor: scale / viewer.currentScale, origin, pan: [panX, panY], drawingDelay: 150 });
        },
        onPanning: (x, y) => viewer.panBy(x, y),
      });
      return { core, linkService };
    })().catch(error => {
      libraryPromise = null;
      throw error;
    });
  }
  return libraryPromise;
}

async function openResource(link) {
  const current = ++session;
  imageMode = link.hasAttribute('data-image-view');
  imageReady = false;
  imageScale = 1;
  image.hidden = !imageMode;
  pages.hidden = imageMode;
  paging.hidden = imageMode;
  container.setAttribute('aria-label', text[imageMode ? 'js-image-document' : 'js-pdf-document']);
  document.querySelector('.pdf-overlay-toolbar').setAttribute('aria-label', text[imageMode ? 'js-image-controls' : 'js-pdf-controls']);
  opener = link;
  scrollY = window.scrollY;
  document.getElementById('pdf-overlay-title').textContent = link.dataset.pdfTitle;
  document.getElementById('pdf-overlay-download').href = link.href;
  document.getElementById('pdf-overlay-download').textContent = text[imageMode ? 'js-image-download' : 'js-pdf-download'];
  status.textContent = text[imageMode ? 'js-image-loading' : 'js-pdf-loading'];
  status.hidden = false;
  pageLabel.textContent = '';
  pageLabel.removeAttribute('aria-label');
  container.setAttribute('aria-busy', 'true');
  controls.forEach(control => { control.disabled = true; });
  document.body.style.top = `-${scrollY}px`;
  document.body.classList.add('pdf-overlay-open');
  dialog.showModal();
  document.getElementById('pdf-overlay-close').focus({ preventScroll: true });
  historyEntry = `pdf-${current}`;
  history.pushState({ ...history.state, saxoPDF: historyEntry }, '');
  if (imageMode) {
    image.alt = link.dataset.pdfTitle;
    image.style.width = '';
    image.onload = () => {
      if (current !== session) return;
      imageReady = true;
      status.hidden = true;
      container.setAttribute('aria-busy', 'false');
      container.scrollTo(0, 0);
      updateControls();
    };
    image.onerror = () => { if (current === session) showError(); };
    image.src = link.href;
    return;
  }
  try {
    const { core, linkService } = await loadLibrary();
    if (current !== session) return;
    const loading = task = core.getDocument({
      url: link.href,
      cMapUrl: new URL('cmaps/', vendor).href,
      cMapPacked: true,
      standardFontDataUrl: new URL('standard_fonts/', vendor).href,
      wasmUrl: new URL('wasm/', vendor).href,
      iccUrl: new URL('iccs/', vendor).href,
      isEvalSupported: false,
    });
    const document = await loading.promise;
    if (current !== session) return;
    linkService.setDocument(document);
    viewer.setDocument(document);
    container.scrollTo(0, 0);
  } catch {
    if (current === session) showError();
  }
}

// Links and downloads still work when modules or dialog are unavailable.
if (typeof dialog.showModal === 'function') {
  document.querySelectorAll('[data-pdf-view], [data-image-view]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      if (!dialog.open) openResource(link);
    });
  });
}
document.getElementById('pdf-overlay-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => {
  const bounds = dialog.getBoundingClientRect();
  if (event.target === dialog && (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom)) dialog.close();
});
dialog.addEventListener('close', () => {
  ++session; // Ignore an import or document request that finishes after closing.
  image.onload = null;
  image.onerror = null;
  image.removeAttribute('src');
  image.hidden = true;
  imageReady = false;
  viewer?.setDocument(null);
  task?.destroy().catch(() => {});
  task = null;
  document.body.classList.remove('pdf-overlay-open');
  document.body.style.top = '';
  window.scrollTo(0, scrollY);
  opener?.focus({ preventScroll: true });
  if (history.state?.saxoPDF === historyEntry) history.back();
  historyEntry = null;
});
window.addEventListener('popstate', () => {
  if (dialog.open && history.state?.saxoPDF !== historyEntry) dialog.close();
});
previous.addEventListener('click', () => viewer.previousPage());
next.addEventListener('click', () => viewer.nextPage());
function setImageScale(scale) {
  imageScale = scale;
  image.style.width = `calc(${scale * 100}% - 20px)`;
  updateControls();
}
zoomOut.addEventListener('click', () => {
  if (imageMode) setImageScale(Math.max(0.2, imageScale / 1.25));
  else viewer.currentScale = Math.max(0.2, viewer.currentScale / 1.25);
});
zoomIn.addEventListener('click', () => {
  if (imageMode) setImageScale(Math.min(4, imageScale * 1.25));
  else viewer.currentScale = Math.min(4, viewer.currentScale * 1.25);
});
fit.addEventListener('click', () => {
  if (imageMode) setImageScale(1);
  else viewer.currentScaleValue = 'page-width';
});
new ResizeObserver(() => {
  if (dialog.open && !imageMode && viewer?.pdfDocument && viewer.currentScaleValue === 'page-width') viewer.currentScaleValue = 'page-width';
}).observe(container);
