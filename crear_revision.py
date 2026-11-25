#!/usr/bin/env python3
"""Genera una página local de revisión de muestras; no publica material del corpus."""
import argparse
import html
import json
from pathlib import Path
from urllib.parse import quote

def build(base, destination):
    audit = json.loads((base/'datos/auditoria.json').read_text())
    download = json.loads((base/'datos/descarga-muestra.json').read_text())
    videos = {Path(row['file']).stem:row['file'] for row in download['files']}
    cards = []
    for index, sample in enumerate(audit['shortlist'], 1):
        stem = Path(sample['elan_file']).stem
        name = videos[stem]
        source = base/'datos/videos'/name
        if not source.is_file():
            raise FileNotFoundError('Falta un vídeo de la muestra: '+name)
        start, end = sample['start_ms']/1000, sample['end_ms']/1000
        # La salida vive en outputs/, al lado de datos/. No embebe ni redistribuye el vídeo.
        url = '../datos/videos/'+quote(name, safe='')
        cards.append(f'''<article><h2>Muestra {index}</h2>
<p class="timing">{start:.3f}–{end:.3f} s · {(end-start):.2f} segundos</p>
<video controls preload="none" src="{html.escape(url,quote=True)}#t={start},{end}" data-start="{start}" data-end="{end}"></video>
<p class="label">Traducción de referencia del corpus</p><blockquote>{html.escape(sample['translation'])}</blockquote>
<p>Preselección automática: contexto, manos, rostro y comprensión pendientes de revisión. Puede ser una lista o una frase dependiente del contexto.</p>
<div class="actions"><button type="button" data-mode="segment">Reproducir fragmento</button>
<button type="button" data-mode="context">Ver con contexto</button>
<a href="{html.escape(url,quote=True)}">Abrir vídeo completo</a></div>
<details><summary>Procedencia y verificación</summary><p>ELAN: {html.escape(sample['elan_file'])}; anotación {html.escape(sample['annotation_id'])}. Tamaño y CRC del archivo comprobados al extraerlo; SHA-256 registrado localmente. No se verificó el MD5 del ZIP completo.</p></details>
</article>''')
    document = '''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>LSE Video — revisión de originales</title><style>
body{font:17px/1.6 system-ui,sans-serif;background:#f5f5f2;color:#172c31;max-width:1050px;margin:40px auto;padding:0 20px}
h1{line-height:1.2}article{background:white;padding:25px;margin:30px 0;border-radius:14px;border:1px solid #d1dcd6}
video{display:block;width:100%;max-height:600px;background:#101d24}blockquote{border-left:4px solid #477462;margin:12px 0;padding:8px 18px}
.label{font-weight:650;margin-bottom:0}.timing{color:#38564d}.actions{display:flex;gap:15px;align-items:center;flex-wrap:wrap}
button,a{font:inherit}button{padding:9px 14px;cursor:pointer;border:1px solid #416359;background:#edf3ed;border-radius:6px}
a{color:#235c49}button:focus-visible,a:focus-visible{outline:3px solid #a9681c}header{border-bottom:1px solid #bdc8bf;padding-bottom:22px}
.notice{background:#fff2d7;padding:15px;border-radius:8px}details{margin-top:18px}footer{margin:30px 0}
</style><header><p>LSE VIDEO · PRIMERA MUESTRA LOCAL</p><h1>Primero, comprobar los originales</h1>
<p>Tres candidatos de lengua de signos española con traducción al castellano. Aquí todavía no hay vídeo generado, avatar personalizable ni traducción automática.</p>
<p class="notice">Material de investigación no comercial, CC BY-NC 4.0. No publicar estos vídeos sin revisar sus condiciones. El contenido sanitario es una referencia del corpus, no una recomendación médica ni un servicio de interpretación.</p>
<p>Al reproducir una muestra, las otras se pausan. «Ver con contexto» añade tres segundos a cada lado. Para examinar más contexto, abre el vídeo completo.</p></header>
''' + ''.join(cards) + '''<footer>Fuente: <a href="https://zenodo.org/records/10234465">LSE-Health-UVigo — Alba-Castro y colaboradores</a>.
Licencia según <a href="https://portalcientifico.uvigo.gal/documentos/668fc42bb9e7c03b01bd5792?lang=es">ficha de la Universidade de Vigo</a>.
<p>Siguiente comprobación: visibilidad de manos/rostro y frase autónoma. La comprensión debe revisarse con personas sordas signantes y especialistas de LSE.</p></footer>
<script>
const videos = [...document.querySelectorAll('video')];
for (const video of videos) {
  video.addEventListener('play', () => { for(const other of videos) if(other !== video) other.pause(); });
  video.addEventListener('timeupdate', () => { if(video.dataset.stop && video.currentTime >= Number(video.dataset.stop)) video.pause(); });
}
for(const button of document.querySelectorAll('button[data-mode]')) button.addEventListener('click', async () => {
  const video = button.closest('article').querySelector('video');
  const context = button.dataset.mode === 'context' ? 3 : 0;
  video.dataset.stop = String(Number(video.dataset.end)+context);
  try { video.currentTime = Math.max(0, Number(video.dataset.start)-context); await video.play(); }
  catch (_) { button.textContent = 'Usa los controles del vídeo o abre el archivo completo'; }
});
</script></html>'''
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(document)
    return len(cards)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    args = parser.parse_args()
    base = Path(__file__).parent
    output = base/'outputs/VALIDAR.html'
    count = build(base, output)
    print(f'Página local preparada: {count} muestras. {output}')
