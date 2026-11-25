#!/usr/bin/env python3
"""Obtiene una muestra del ZIP oficial mediante HTTP Range, sin descargar todo el corpus."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile
import zlib

URL = 'https://zenodo.org/records/10234465/files/Videos-LSE-Health-UVigo.zip?download=1'

class RangeFile(io.RawIOBase):
    def __init__(self, budget):
        self.position = 0
        self.size = None
        self.received = 0
        self.budget = budget
        self.cache_start = -1
        self.cache = b''
        self.fetch(0, 0)

    def fetch(self, start, end):
        expected = end-start+1
        if expected > 4*1024*1024 or self.received+expected > self.budget:
            raise ValueError('Límite de descarga alcanzado; no se amplía automáticamente.')
        with tempfile.TemporaryDirectory() as directory:
            header = Path(directory)/'headers'
            body = Path(directory)/'body'
            result = subprocess.run([
                'curl', '--fail', '--location', '--silent', '--show-error', '--max-time', '30',
                '--max-filesize', str(expected), '--range', f'{start}-{end}',
                '--dump-header', str(header), '--output', str(body), URL,
            ], capture_output=True, timeout=35)
            if result.returncode:
                raise RuntimeError(f'No se pudo obtener un rango del ZIP (curl {result.returncode}); no se intenta descarga completa.')
            matches = re.findall(r'content-range:\s*bytes (\d+)-(\d+)/(\d+)', header.read_text(), re.I)
            if not matches:
                raise ValueError('El servidor no ofrece el rango solicitado; descarga detenida.')
            first, last, total = map(int, matches[-1])
            if (first,last) != (start,end) or (self.size is not None and total != self.size):
                raise ValueError('Rango o tamaño del archivo remoto inconsistente.')
            data = body.read_bytes()
            if len(data) != expected:
                raise ValueError('Respuesta incompleta.')
            self.size = total
            self.received += len(data)
            return data

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        new = offset if whence == 0 else self.position+offset if whence == 1 else self.size+offset
        if new < 0:
            raise ValueError('Posición negativa.')
        self.position = new
        return new

    def read(self, count=-1):
        remaining = max(0, self.size-self.position)
        count = remaining if count < 0 else min(count, remaining)
        result = bytearray()
        while count:
            if not self.cache_start <= self.position < self.cache_start+len(self.cache):
                self.cache_start = (self.position//(4*1024*1024))*(4*1024*1024)
                end = min(self.size-1, self.cache_start+4*1024*1024-1)
                self.cache = self.fetch(self.cache_start, end)
            index = self.position-self.cache_start
            part = min(count, len(self.cache)-index)
            result.extend(self.cache[index:index+part])
            self.position += part
            count -= part
        return bytes(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).parent
    parser.add_argument('--auditoria', type=Path, default=base/'datos/auditoria.json')
    parser.add_argument('--descargar', action='store_true', help='Sin esta opción solo consulta tamaños.')
    parser.add_argument('--max-mb', type=int, default=100, help='Presupuesto de transferencia de esta ejecución.')
    args = parser.parse_args()
    if not 1 <= args.max_mb <= 150:
        parser.error('Usar un presupuesto de 1 a 150 MB; no se admite descarga masiva.')
    shortlist = json.loads(args.auditoria.read_text())['shortlist']
    if not 1 <= len(shortlist) <= 3:
        parser.error('La muestra debe contener entre uno y tres vídeos.')
    targets = {Path(row['elan_file']).stem for row in shortlist}
    remote = RangeFile(args.max_mb*1024*1024)
    output = base/'datos/videos'
    report = {'source':URL, 'license':'CC BY-NC 4.0 según ficha institucional; no redistribuir automáticamente',
              'whole_archive_downloaded':False, 'files':[]}
    with zipfile.ZipFile(remote) as archive:
        entries = [f for f in archive.infolist() if Path(f.filename).stem in targets
                   and Path(f.filename).suffix.lower() in {'.mp4','.mov'}]
        if len(entries) != len(targets):
            raise ValueError('No existe una correspondencia unívoca para todos los vídeos solicitados.')
        for entry in entries:
            if entry.file_size > 100*1024*1024 or entry.flag_bits & 1:
                raise ValueError('Archivo supera tamaño permitido o está cifrado.')
            row = {'file':Path(entry.filename).name, 'bytes':entry.file_size,
                   'compressed_bytes':entry.compress_size, 'crc32':f'{entry.CRC:08x}'}
            if args.descargar:
                output.mkdir(parents=True, exist_ok=True)
                target = output/row['file']
                if target.exists():
                    crc, digest = 0, hashlib.sha256()
                    with target.open('rb') as previous:
                        while chunk := previous.read(1024*1024):
                            crc = zlib.crc32(chunk, crc)
                            digest.update(chunk)
                    if target.stat().st_size != entry.file_size or crc != entry.CRC:
                        raise ValueError('El vídeo existente no supera la comprobación; no se sobrescribe: '+target.name)
                    row.update(sha256=digest.hexdigest(), integrity='existing_entry_crc32_and_size_verified')
                    report['files'].append(row)
                    print(target.name+': reutilizado tras verificar tamaño y CRC32')
                    continue
                temporary = target.with_suffix(target.suffix+'.part')
                digest = hashlib.sha256()
                try:
                    with archive.open(entry) as source, temporary.open('xb') as dest:
                        while chunk := source.read(1024*1024):
                            dest.write(chunk)
                            digest.update(chunk)
                    if temporary.stat().st_size != entry.file_size:
                        raise ValueError('Tamaño extraído incorrecto.')
                    # ZipExtFile comprueba CRC al llegar a EOF; no certifica todo el ZIP.
                    temporary.rename(target)
                except Exception:
                    temporary.unlink(missing_ok=True)
                    raise
                row['sha256'] = digest.hexdigest()
                row['integrity'] = 'entry_crc32_and_size_verified_not_whole_archive_md5'
            report['files'].append(row)
            print(f"{row['file']}: {row['bytes']/1024/1024:.1f} MiB; "
                  + ('descargado y verificado' if args.descargar else 'solo listado'))
    report['downloaded_bytes_this_run'] = remote.received
    if args.descargar:
        (base/'datos/descarga-muestra.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'Transferencia: {remote.received/1024/1024:.2f} MiB. Sin modelos ni entrenamiento.')

if __name__ == '__main__':
    main()
