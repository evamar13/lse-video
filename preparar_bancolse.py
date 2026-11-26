#!/usr/bin/env python3
"""Muestra educativa no comercial: tres entradas, sin IA ni entrenamiento."""
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent
BASE = 'https://www.fundacioncnse.org/educa/bancolse/'
LICENSE = 'https://creativecommons.org/licenses/by-nc-sa/3.0/'
LIMIT = 20 * 1024 * 1024


class Downloads(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        link = attrs.get('href', '').strip()
        if tag == 'a' and '/descargas/' in link and link.endswith('.png'):
            self.links.add(link)


def main():
    folder = ROOT / 'datos/bancolse'
    folder.mkdir(parents=True, exist_ok=True)
    received = 0

    def fetch(url, dest):
        nonlocal received
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.netloc != 'www.fundacioncnse.org' or not parsed.path.startswith('/educa/bancolse/'):
            raise ValueError('URL fuera del alcance de la muestra')
        remaining = LIMIT - received
        if remaining <= 0:
            raise ValueError('Presupuesto de transferencia agotado')
        temporary = dest.with_name(dest.name + '.part')
        try:
            subprocess.run(['curl', '--fail', '--silent', '--show-error',
                            '--max-time', '25', '--max-filesize', str(remaining),
                            '--output', str(temporary), url], check=True, timeout=30)
            size = temporary.stat().st_size
            received += size
            if size > remaining:
                raise ValueError('Respuesta excede el presupuesto')
            temporary.replace(dest)
        finally:
            temporary.unlink(missing_ok=True)

    fetch(BASE + 'condiciones-de-uso.php', folder / 'condiciones.html')
    terms = (folder / 'condiciones.html').read_text()
    if 'creativecommons.org/licenses/by-nc-sa/3.0' not in terms:
        raise ValueError('Licencia esperada ausente; revisar antes de descargar')
    records = []
    for sign in ('hola', 'gracias', 'por-favor'):
        page = BASE + f'saludos-y-cortesia-{sign}.php'
        target = folder / f'{sign}.html'
        fetch(page, target)
        parser = Downloads()
        parser.feed(target.read_text())
        if not parser.links or len(parser.links) > 4:
            raise ValueError(f'Descargas inesperadas en {sign}')
        for link in sorted(parser.links):
            url = urljoin(page, link)
            name = Path(urlsplit(url).path).name
            destination = folder / name
            fetch(url, destination)
            data = destination.read_bytes()
            if not data.startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError('El recurso no es un PNG')
            records.append(dict(entrada=sign, pagina=page, url=url, archivo=name,
                                sha256=hashlib.sha256(data).hexdigest(), bytes=len(data),
                                licencia='CC BY-NC-SA 3.0', titular='Fundación CNSE',
                                uso='referencia educativa no comercial',
                                movimiento_validado=False, entrenamiento=False))
    manifest = dict(fuente=BASE, condiciones=BASE+'condiciones-de-uso.php',
                    condiciones_sha256=hashlib.sha256((folder/'condiciones.html').read_bytes()).hexdigest(),
                    transferencia_ejecucion=received, recursos=records)
    (folder / 'inventario.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    output = ROOT / 'outputs/bancolse'
    output.mkdir(parents=True, exist_ok=True)
    cards = ''.join(f'<figure><img style="max-width:320px;max-height:320px" src="../../datos/bancolse/{html.escape(r["archivo"])}"><figcaption>{html.escape(r["entrada"])} · <a href="{html.escape(r["pagina"])}">Fuente</a></figcaption></figure>' for r in records)
    (output/'VALIDAR.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8"><title>Muestra BancoLSE</title><body style="font:18px system-ui;max-width:1000px;margin:40px auto"><h1>Referencia educativa BancoLSE</h1><p>Recursos de Fundación CNSE. Sin modificaciones. <a href="'+LICENSE+'">CC BY-NC-SA 3.0</a>. Uso no comercial. Esta muestra no traduce frases ni valida movimientos.</p><main style="display:flex;flex-wrap:wrap">'+cards+'</main></body></html>')
    print(json.dumps(dict(recursos=len(records), transferencia_bytes=received, vista=str(output/'VALIDAR.html')), ensure_ascii=False))


if __name__ == '__main__':
    main()
