// NOTE: If this app is hosted in a subdirectory (e.g. username.github.io/matplotgallery/),
// update the fetch handler paths accordingly and ensure sw.js is in the root of that subdirectory.

// ═══════════════════════════════════════════════════════════════════════════════
// MatplotGallery — Service Worker
// ═══════════════════════════════════════════════════════════════════════════════
// Caching strategy:
//   - Cache First for images (figures/*.png) — fast loading, offline support
//   - Network First for HTML/JS/CSS/JSON — always get latest, fallback to cache
// ═══════════════════════════════════════════════════════════════════════════════

const CACHE_NAME = 'matplotgallery-v1';

// Core app shell files to pre-cache on install
const APP_SHELL_FILES = [
  './',
  './index.html',
  './about.html',
  './style.css',
  './app.js',
  './search.js',
  './data.json',
  './manifest.json'
];


// ─── INSTALL EVENT ────────────────────────────────────────────────────────────
// Pre-cache the app shell (core HTML, CSS, JS, JSON files).
// Figure and code snippet files are cached dynamically on first fetch
// since we can't know all filenames at build time.
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Pre-caching app shell files');
        return cache.addAll(APP_SHELL_FILES);
      })
      .then(() => {
        console.log('[SW] App shell cached successfully');
      })
      .catch((error) => {
        console.error('[SW] Failed to cache app shell:', error);
      })
  );
});


// ─── ACTIVATE EVENT ──────────────────────────────────────────────────────────
// Clean up old caches from previous versions.
// Any cache whose name is NOT the current CACHE_NAME gets deleted.
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');

  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name !== CACHE_NAME)
            .map((name) => {
              console.log(`[SW] Deleting old cache: ${name}`);
              return caches.delete(name);
            })
        );
      })
      .then(() => {
        console.log('[SW] Old caches cleaned up');
        // Take control of all open clients immediately
        return self.clients.claim();
      })
  );
});


// ─── FETCH EVENT ─────────────────────────────────────────────────────────────
// Route requests to the appropriate caching strategy:
//   - Images (figures/*.png, icons/*.png): Cache First
//   - Everything else (HTML, JS, CSS, JSON): Network First
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Only handle requests within our scope (same origin)
  if (url.origin !== location.origin) {
    return;
  }

  // ── Cache First strategy for images ────────────────────────────────────
  // Best for static assets that rarely change (plot figures, icons).
  // Try cache first → if miss, fetch from network and cache for next time.
  if (isImageRequest(url)) {
    event.respondWith(cacheFirst(event.request));
    return;
  }

  // ── Network First strategy for HTML/JS/CSS/JSON ────────────────────────
  // Best for files that may be updated (app code, data).
  // Try network first → if offline or error, fall back to cache.
  event.respondWith(networkFirst(event.request));
});


// ─── MESSAGE EVENT ───────────────────────────────────────────────────────────
// Listen for messages from the main thread.
// Supports SKIP_WAITING to immediately activate a new service worker version.
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log('[SW] Received SKIP_WAITING, activating immediately');
    self.skipWaiting();
  }
});


// ═══════════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Check if a request is for an image file (figures or icons).
 * @param {URL} url - The request URL
 * @returns {boolean}
 */
function isImageRequest(url) {
  const path = url.pathname;
  return (
    path.includes('/figures/') ||
    path.includes('/icons/') ||
    path.endsWith('.png') ||
    path.endsWith('.jpg') ||
    path.endsWith('.jpeg') ||
    path.endsWith('.webp') ||
    path.endsWith('.svg')
  );
}


/**
 * Cache First strategy.
 * 1. Check the cache for a match
 * 2. If found, return the cached response
 * 3. If not found, fetch from network, cache the response, and return it
 *
 * @param {Request} request - The fetch request
 * @returns {Promise<Response>}
 */
async function cacheFirst(request) {
  try {
    // Step 1: Try the cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Step 2: Cache miss — fetch from network
    const networkResponse = await fetch(request);

    // Step 3: Cache the fresh response for future use
    // Only cache successful responses (status 200)
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    // Both cache and network failed
    console.error('[SW] Cache First failed for:', request.url, error);
    return new Response('Resource not available offline', {
      status: 503,
      statusText: 'Service Unavailable',
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}


/**
 * Network First strategy.
 * 1. Try to fetch from the network
 * 2. If successful, cache the response and return it
 * 3. If network fails, fall back to the cache
 *
 * @param {Request} request - The fetch request
 * @returns {Promise<Response>}
 */
async function networkFirst(request) {
  try {
    // Step 1: Try the network
    const networkResponse = await fetch(request);

    // Step 2: Cache the fresh response
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    // Step 3: Network failed — try the cache
    console.warn('[SW] Network failed, falling back to cache for:', request.url);
    const cachedResponse = await caches.match(request);

    if (cachedResponse) {
      return cachedResponse;
    }

    // Both network and cache failed
    console.error('[SW] Network First failed completely for:', request.url, error);
    return new Response('Resource not available offline', {
      status: 503,
      statusText: 'Service Unavailable',
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}
