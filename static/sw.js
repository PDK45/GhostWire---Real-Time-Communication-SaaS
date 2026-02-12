const CACHE_NAME = 'ghostwire-v1';
const ASSETS = [
    '/',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/images/cyberpunk_app_icon.png',
    'https://cdn.socket.io/4.6.0/socket.io.min.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
