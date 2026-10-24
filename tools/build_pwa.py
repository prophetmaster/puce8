"""Construit la version installable (PWA) de Puce8 Studio dans le dossier docs/,
celui que GitHub Pages publie.

Source unique : puce8-studio.html. Relancer ce script après chaque modification :
    python tools/build_pwa.py
"""
import hashlib
import json
import pathlib
import struct
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "puce8-studio.html"
OUT = ROOT / "docs"

BG = "#1b1a20"
DESCRIPTION = "Studio de musique 8-bit : séquenceur 4 canaux façon NES, sonothèque rétro et moderne, convertisseur audio vers chiptune."

PWA_HEAD = f"""<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="{BG}">
<meta name="description" content="{DESCRIPTION}">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Puce8">"""

# ---------- Icône pixel art (grille 16 x 16) ----------
COLORS = {
    ".": (0x1B, 0x1A, 0x20),  # boîtier
    "B": (0x3D, 0x3B, 0x48),  # cadre de l'écran
    "L": (0xB7, 0xC4, 0x9A),  # écran LCD
    "I": (0x26, 0x30, 0x1F),  # encre LCD
    "R": (0xD2, 0x3A, 0x5C),  # boutons rouges
    "D": (0xA2, 0x9D, 0xAC),  # croix directionnelle
}


def icon_grid():
    g = [["."] * 16 for _ in range(16)]
    for y in range(2, 11):
        for x in range(2, 14):
            g[y][x] = "B" if y in (2, 10) or x in (2, 13) else "L"
    # onde carrée sur l'écran
    prev = None
    for x in range(3, 13):
        high = (x - 3) % 6 < 3
        y = 4 if high else 8
        g[y][x] = "I"
        if prev is not None and prev != high:
            for yy in range(4, 9):
                g[yy][x] = "I"
        prev = high
    for x, y in ((4, 12), (3, 13), (4, 13), (5, 13), (4, 14)):
        g[y][x] = "D"
    for x, y in ((12, 12), (13, 12), (12, 13), (13, 13), (9, 13), (10, 13), (9, 14), (10, 14)):
        g[y][x] = "R"
    return g


def png(path, size, pad_cells=0):
    grid = icon_grid()
    cells = 16 + 2 * pad_cells
    rows = []
    for py in range(size):
        cy = py * cells // size - pad_cells
        row = bytearray([0])
        for px in range(size):
            cx = px * cells // size - pad_cells
            ch = grid[cy][cx] if 0 <= cx < 16 and 0 <= cy < 16 else "."
            row += bytes(COLORS[ch])
        rows.append(bytes(row))
    raw = zlib.compress(b"".join(rows), 9)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)) + chunk(b"IDAT", raw) + chunk(b"IEND", b"")
    path.write_bytes(data)


def build():
    (OUT / "icons").mkdir(parents=True, exist_ok=True)
    png(OUT / "icons" / "icon-192.png", 192)
    png(OUT / "icons" / "icon-512.png", 512)
    png(OUT / "icons" / "icon-maskable-512.png", 512, pad_cells=3)  # zone de sécurité pour Android
    png(OUT / "icons" / "apple-touch-icon.png", 180, pad_cells=1)

    src = SRC.read_text(encoding="utf-8")
    cut = src.index("</style>") + len("</style>")
    head = src[:cut].replace("<title>Puce8 Studio</title>", "<title>Puce8 Studio</title>\n" + PWA_HEAD)
    html = '<!doctype html>\n<html lang="fr">\n<head>\n' + head + "\n</head>\n<body>\n" + src[cut:].strip() + "\n</body>\n</html>\n"
    (OUT / "index.html").write_text(html, encoding="utf-8")

    manifest = {
        "name": "Puce8 Studio",
        "short_name": "Puce8",
        "description": DESCRIPTION,
        "lang": "fr",
        "id": "./",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "orientation": "any",
        "background_color": BG,
        "theme_color": BG,
        "categories": ["music", "entertainment"],
        "icons": [
            {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    (OUT / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # La version du cache change dès que l'app change : les appareils installés se mettent à jour.
    version = hashlib.sha1(html.encode("utf-8")).hexdigest()[:10]
    sw = SW_TEMPLATE.replace("__VERSION__", version)
    (OUT / "sw.js").write_text(sw, encoding="utf-8")
    print(f"PWA construite dans {OUT} (version {version})")


SW_TEMPLATE = """// Service worker de Puce8 Studio : fait marcher l'app hors ligne.
const CACHE = 'puce8-__VERSION__';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png',
  './icons/icon-maskable-512.png', './icons/apple-touch-icon.png'];
const FONT_HOSTS = ['fonts.googleapis.com', 'fonts.gstatic.com'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('puce8-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Polices : servies depuis le cache, rafraîchies en arrière-plan.
  if (FONT_HOSTS.includes(url.hostname)) {
    e.respondWith(caches.open(CACHE).then(async c => {
      const hit = await c.match(req);
      const fresh = fetch(req).then(r => { if (r.ok || r.type === 'opaque') c.put(req, r.clone()); return r; }).catch(() => hit);
      return hit || fresh;
    }));
    return;
  }
  if (url.origin !== location.origin) return;

  // Pages : le réseau d'abord pour avoir la dernière version, le cache si hors ligne.
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(r => {
      const copy = r.clone(); caches.open(CACHE).then(c => c.put('./index.html', copy)); return r;
    }).catch(() => caches.match('./index.html')));
    return;
  }

  e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
});
"""

if __name__ == "__main__":
    build()
