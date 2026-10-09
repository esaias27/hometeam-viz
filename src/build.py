import base64, json, os, re, shutil, hashlib
B = '/home/claude/build'
D = B + '/dist'
os.makedirs(D, exist_ok=True)
font = base64.b64encode(open('/home/claude/fonts/fontsource-oswald-5.3.0/package/files/oswald-latin-600-normal.woff2', 'rb').read()).decode()
svg = open(B + '/logo.svg').read()
svg = re.sub(r'\s+width="\d+" height="\d+"', '', svg, count=1)
html = open(B + '/src/app.html').read().replace('{{FONT}}', font).replace('{{LOGO_SVG}}', svg)
open(D + '/index.html', 'w').write(html)
ver = hashlib.sha1(html.encode()).hexdigest()[:10]
manifest = {
    "name": "HOME TEAM Visuals", "short_name": "HOME TEAM", "start_url": "./", "scope": "./",
    "display": "standalone", "orientation": "any", "background_color": "#000000", "theme_color": "#000000",
    "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
open(D + '/manifest.webmanifest', 'w').write(json.dumps(manifest, indent=1))
sw = """const CACHE = 'ht-viz-%s';
const FILES = ['./', './index.html', './manifest.webmanifest', './icon-180.png', './icon-192.png', './icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  // network-first for the page (so updates arrive when online), cache fallback offline
  if (e.request.mode === 'navigate') {
    e.respondWith(fetch(e.request).then(r => { const cp = r.clone(); caches.open(CACHE).then(c => c.put('./index.html', cp)); return r; })
      .catch(() => caches.match('./index.html')));
    return;
  }
  e.respondWith(caches.match(e.request, {ignoreSearch: true}).then(r => r || fetch(e.request)));
});
""" % ver
open(D + '/sw.js', 'w').write(sw)
print('built', len(html)//1024, 'KB, cache', ver)
