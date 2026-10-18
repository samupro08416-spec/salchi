// Bocado: intenta la red primero (siempre la última versión) y, sin conexión, usa lo guardado.
const CACHE = 'bocado-v1';
const CORE = ['./', './index.html', './foods.js', './manifest.webmanifest', './icon-192.png', './apple-touch-icon.png'];
self.addEventListener('install', e => { self.skipWaiting(); e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).catch(() => {})); });
self.addEventListener('activate', e => { e.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || req.url.includes('openfoodfacts.org')) return;
  e.respondWith(
    fetch(req).then(res => {
      if (res && (res.ok || res.type === 'opaque')) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)).catch(() => {}); }
      return res;
    }).catch(() => caches.match(req, {ignoreSearch: true}))
  );
});
