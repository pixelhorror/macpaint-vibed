// Service worker de MacPaint: funciona offline.
// Sube VERSION cada vez que publiques cambios para forzar la actualización.
const VERSION = 'macpaint-v2';
const ASSETS = [
  './macpaint.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png',
  './icons/favicon-32.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;

  // HTML: primero la red (para ver la última versión), si no hay conexión, la caché
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then(res => { if (res.ok && !res.redirected) { const copy = res.clone(); caches.open(VERSION).then(c => c.put('./macpaint.html', copy)); } return res; })
        .catch(() => caches.match('./macpaint.html'))
    );
    return;
  }

  // Resto: primero la caché
  e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
});
