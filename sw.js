/* ATXGreene service worker — offline shell + fast static assets.
   Strategy:
     - navigations (HTML): network-first, fall back to cache/offline shell (so deploys show immediately when online).
     - same-origin static assets: cache-first, then network (fonts/api/iframes are cross-origin and pass straight through).
   Bump VERSION to invalidate the old cache on the next deploy. */
'use strict';

var VERSION = 'v1';
var CACHE = 'atxgreene-' + VERSION;
var PRECACHE = [
  '/',
  '/index.html',
  '/404.html',
  '/favicon.png',
  '/apple-touch-icon.png',
  '/manifest.webmanifest',
  '/assets/brand/phoenix-mark.png',
  '/assets/brand/icon-192.png'
];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE)
      .then(function (cache) { return cache.addAll(PRECACHE); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys()
      .then(function (keys) {
        return Promise.all(keys.map(function (k) { if (k !== CACHE) { return caches.delete(k); } }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (event) {
  var req = event.request;
  if (req.method !== 'GET') { return; }

  var url;
  try { url = new URL(req.url); } catch (e) { return; }
  // Never touch cross-origin requests (Google Fonts, GitHub API, embedded iframes).
  if (url.origin !== self.location.origin) { return; }

  // Network-first for page navigations so fresh deploys win when online.
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then(function (res) {
          var copy = res.clone();
          caches.open(CACHE).then(function (c) { c.put(req, copy); });
          return res;
        })
        .catch(function () {
          return caches.match(req).then(function (r) { return r || caches.match('/index.html'); });
        })
    );
    return;
  }

  // Cache-first for same-origin static assets (images, css, js).
  event.respondWith(
    caches.match(req).then(function (cached) {
      if (cached) { return cached; }
      return fetch(req).then(function (res) {
        if (res && res.ok && res.type === 'basic') {
          var copy = res.clone();
          caches.open(CACHE).then(function (c) { c.put(req, copy); });
        }
        return res;
      });
    })
  );
});
