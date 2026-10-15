"""Convierte el juego publicado en Claude en una web independiente para GitHub Pages."""
import sys, re, pathlib
src = pathlib.Path(sys.argv[1]).read_text()
head = '''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#fde7ef">
<meta name="description" content="Salchi y los lirios: juegos 3D con Salchi, Miso, Rocco y Samu.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Salchi">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
'''
tail = '''
<script>
if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
</script>
</body>
</html>
'''
# La web pública no lleva la dedicatoria (se queda solo en el enlace de Claude de Ashlyn)
src, n = re.subn(r'\s*<p class="ribbon">.*?</p>', '', src, flags=re.S)
assert n == 1, 'no se encontró la dedicatoria'
out = pathlib.Path(sys.argv[2])
out.write_text(head + src + tail)
print('ok', out, len(head + src + tail))
