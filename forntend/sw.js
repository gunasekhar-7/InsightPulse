const CACHE_VERSION = 'v2';
const CACHE_NAME = `ip-${CACHE_VERSION}`
const CORE_ASSETS = [
  '/',
  '/index.html',
  '/style.css',
  '/script.js',
  '/manifest.json',
  '/icons/icon-192.png',
  '/icons/icon-512.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(CORE_ASSETS))
      .catch(console.error)
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(cacheName => cacheName.startsWith('ip-') && cacheName !== CACHE_NAME)
          .map(cacheName => caches.delete(cacheName))
      );
    })
  );
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return fetch(e.request);
  if (e.request.url.startsWith(location.origin)) {
    e.respondWith(
      caches.match(e.request)
        .then(cachedResponse => cachedResponse || fetch(e.request)
          .then(networkResponse => {
            if (!networkResponse || networkResponse.status !== 200 || networkResponse.type === 'opaque') {
              return networkResponse;
            }
            // Cache API responses as needed
            if (
              e.request.url.includes('/analyze') ||
              e.request.url.includes('/auth/login')
            ) {
              // Clone for cache
              const networkResClone = networkResponse.clone();
              caches.open(CACHE_NAME)
                .then(cache => cache.put(e.request, networkResClone));
            }
            return networkResponse;
          })
          .catch(() => caches.match('/offline.html'))
        )
    );
  }
});
