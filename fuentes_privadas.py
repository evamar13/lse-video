#!/usr/bin/env python3
"""Muestras privadas limitadas; sin inferencias, entrenamiento ni publicación."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import struct
import subprocess
import zlib

BASE=Path(__file__).resolve().parent
ROOT=BASE/'datos/fuentes-privadas'
SOURCES=[
    dict(id='uvigo-health',url='https://zenodo.org/records/10234465',license='CC BY-NC 4.0',
         status='muestra_local_existente',use='Vídeos continuos, traducciones y glosas; análisis no comercial',path='datos/videos'),
    dict(id='bancolse',url='https://www.fundacioncnse.org/educa/bancolse/',license='CC BY-NC-SA 3.0',
         status='muestra_local_existente',use='Seis imágenes de referencia educativa no comercial',path='datos/bancolse'),
    dict(id='isignos',url='https://isignos.uvigo.es/',license='CC BY-NC 4.0 declarada en texto',
         status='muestra_pendiente',use='Un vídeo y subtítulos castellanos; análisis privado no comercial',
         caution='El enlace CC apunta a BY 4.0, el texto dice BY-NC 4.0: conservar ambas evidencias y aplicar NC.'),
    dict(id='dactilologia-lse',url='https://zenodo.org/records/21351703',license='CC BY 4.0',
         status='muestra_pendiente',use='Una imagen del ZIP 192; no corpus de frases ni verdad de referencia de articulaciones'),
    dict(id='lse-horeco',url='https://taalmaterialen.ivdnt.org/download/lse_horeco/',license='CC BY-NC 3.0',
         status='requiere_login',use='Vídeo y castellano paralelo',caution='Acceso legítimo mediante cuenta; no se elude el inicio de sesión.'),
    dict(id='dilse',url='https://fundacioncnse-dilse.org/condiciones-uso.php',license='CC BY-NC-SA 3.0 en página indexada; restricciones adicionales',
         status='referencia_pendiente_verificacion_actual',use='Consulta; no corpus incorporado',
         caution='La respuesta directa actual es una aplicación Flutter. Texto indexado declara CC y prohíbe redistribución como diccionario; verificar alcance actual antes de extracción.'),
    dict(id='cervantes',url='https://data.cervantesvirtual.com/condiciones-de-uso/',license='CC0 solo para metadatos',
         status='metadatos_reutilizables_videos_pendientes',use='Inventario bibliográfico',caution='No extender CC0 a grabaciones; no se descargan vídeos.'),
    dict(id='congreso',url='https://www.congreso.es/gl/cem/aviso-legal',license='Reutilización institucional con condiciones; vídeo concreto pendiente',
         status='pendiente_derechos_y_muestra',use='Candidato de interpretación continua',caution='No equiparar documento público a grabación sin derechos ni permiso de clonación.'),
    dict(id='youtube-ies',url='https://www.youtube.com/watch?v=JOpFHf5efe0',license='No confirmada',
         status='pendiente_licencia',use='Referencia candidata; sin descarga ni extracción'),
]


def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    temporary.replace(path)


def fetch(url,path,limit):
    """Solo URLs fijadas por el ejecutor; sin cookies, credenciales ni redirecciones."""
    if path.exists():
        raise FileExistsError('Existe muestra: no sobrescribir ni repetir transferencia')
    temp=path.with_suffix(path.suffix+'.part')
    try:
        subprocess.run(['curl','--fail','--silent','--show-error','--max-time','40',
            '--max-filesize',str(limit),'--output',str(temp),url],check=True,timeout=45)
        if temp.stat().st_size>limit:raise ValueError('Límite de tamaño excedido')
        temp.replace(path)
    finally:temp.unlink(missing_ok=True)
    return dict(url=url,file=str(path.relative_to(BASE)),bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def isignos():
    out=ROOT/'isignos';out.mkdir(parents=True,exist_ok=True,mode=0o700)
    entries=[]
    entries.append(fetch('https://isignos.uvigo.es/en/',out/'condiciones.html',500_000))
    terms=(out/'condiciones.html').read_text()
    if 'CC BY-NC 4.0' not in terms:raise ValueError('Declaración de licencia no localizada')
    page='https://isignos.uvigo.es/es/metadata/16a90a5a-3406-4544-81d5-2e9f10905440'
    entries.append(fetch(page,out/'ficha.html',500_000))
    page_text=(out/'ficha.html').read_text()
    for expected in ('/videos/PS-NXG.mp4','/videos/PS-NXG.vtt'):
        if expected not in page_text:raise ValueError('Los recursos ya no figuran en la ficha')
    entries.append(fetch('https://isignos.uvigo.es/videos/PS-NXG.vtt',out/'PS-NXG.vtt',500_000))
    subtitle=(out/'PS-NXG.vtt').read_text(encoding='utf-8-sig')
    if not subtitle.startswith('WEBVTT'):raise ValueError('No es WebVTT')
    entries.append(fetch('https://isignos.uvigo.es/videos/PS-NXG.mp4',out/'PS-NXG.mp4',30_000_000))
    entries.append(fetch('https://isignos.uvigo.es/convenciones_anotacion.pdf',out/'convenciones.pdf',3_000_000))
    result=dict(status='muestra_privada_no_comercial',resources=entries,
                attribution='Cabeza, Carmen / García-Miguel, José M. (dirs). iSignos, versión 1.0. Universidade de Vigo.',
                scope='Un vídeo y subtítulos castellanos; alineación lingüística no validada; no se han extraído glosas.',
                license='CC BY-NC 4.0 declarada en texto; enlace discrepante BY 4.0 conservado; se aplica NC')
    save(out/'inventario.json',result)
    return result


def central_start(remote):
    remote.seek(max(0,remote.size-65557));tail=remote.read(65557)
    index=tail.rfind(b'PK\x05\x06')
    if index<0:raise ValueError('EOCD no encontrado')
    eocd=struct.unpack('<4s4H2IH',tail[index:index+22])
    if eocd[1] or eocd[2]:raise ValueError('No se admiten ZIP multidisco')
    offset=eocd[6]
    if offset==0xffffffff:
        absolute=remote.size-len(tail)+index
        remote.seek(absolute-20)
        locator=struct.unpack('<4sIQI',remote.read(20))
        if locator[0]!=b'PK\x06\x07' or locator[1] or locator[3]!=1:raise ValueError('ZIP64 no válido')
        remote.seek(locator[2]);record=struct.unpack('<4sQHHIIQQQQ',remote.read(56))
        if record[0]!=b'PK\x06\x06' or record[4] or record[5]:raise ValueError('ZIP64 multidisco o inválido')
        offset=record[9]
    return offset


def single_image(remote):
    """Lee hasta 256 cabeceras centrales y una entrada; nunca todo el directorio."""
    remote.seek(central_start(remote))
    for _ in range(256):
        header=remote.read(46)
        if len(header)!=46 or header[:4]!=b'PK\x01\x02':raise ValueError('Cabecera central no válida')
        fields=struct.unpack('<4s6H3I5H2I',header)
        flags,method,crc,compressed,size=fields[3],fields[4],fields[7],fields[8],fields[9]
        filename=remote.read(fields[10]);extra=remote.read(fields[11]);remote.read(fields[12])
        offset=fields[16]
        if size==0xffffffff or compressed==0xffffffff or offset==0xffffffff:
            cursor=0;found=False
            while cursor+4<=len(extra):
                kind,length=struct.unpack('<HH',extra[cursor:cursor+4]);values=extra[cursor+4:cursor+4+length];cursor+=4+length
                if kind!=1:continue
                found=True;position=0
                for name in ('size','compressed','offset'):
                    current={'size':size,'compressed':compressed,'offset':offset}[name]
                    if current==0xffffffff:
                        value=struct.unpack('<Q',values[position:position+8])[0];position+=8
                        if name=='size':size=value
                        elif name=='compressed':compressed=value
                        else:offset=value
            if not found:raise ValueError('Falta campo ZIP64')
        name=filename.decode('utf-8' if flags&0x800 else 'cp437')
        if not name.lower().endswith(('.png','.jpg','.jpeg')):continue
        if flags&1 or method not in (0,8) or size>1_000_000 or compressed>1_000_000:raise ValueError('Entrada no admitida')
        remote.seek(offset);local=remote.read(30)
        if local[:4]!=b'PK\x03\x04':raise ValueError('Cabecera local inválida')
        name_len,extra_len=struct.unpack('<HH',local[26:30]);local_name=remote.read(name_len);remote.read(extra_len)
        if local_name!=filename:raise ValueError('Nombre local/central inconsistente')
        payload=remote.read(compressed)
        if method==8:
            decoder=zlib.decompressobj(-15);content=decoder.decompress(payload,size+1)
            if not decoder.eof or decoder.unconsumed_tail or len(content)>size:raise ValueError('Descompresión no válida')
        else:content=payload
        if len(content)!=size or zlib.crc32(content)&0xffffffff!=crc:raise ValueError('Tamaño/CRC no coincide')
        return name,content,crc
    raise ValueError('No hay imagen entre las primeras 256 entradas; no se amplía la búsqueda')


def fingerspelling():
    import muestra_videos as partial
    out=ROOT/'dactilologia';out.mkdir(parents=True,exist_ok=True,mode=0o700)
    if (out/'inventario.json').exists():raise FileExistsError('Muestra ya incorporada')
    evidence=fetch('https://zenodo.org/records/21351703',out/'licencia.html',1_000_000)
    terms=(out/'licencia.html').read_text()
    if 'CC BY 4.0' not in terms and 'creativecommons.org/licenses/by/4.0' not in terms:
        raise ValueError('Licencia esperada no localizada')
    # Reutiliza la guardia HTTP Range existente; no descargar los ZIP de 12 GB.
    partial.URL='https://zenodo.org/records/21351703/files/192.zip?download=1'
    remote=partial.RangeFile(24*1024*1024)
    name,content,crc=single_image(remote)
    suffix=Path(name).suffix.lower()
    image=out/('muestra'+suffix);image.write_bytes(content)
    result=dict(status='una_imagen_privada',url='https://zenodo.org/records/21351703',license='CC BY 4.0',
                attribution='Marroquín Garcia de Madariaga, Ignacio; Cabana Garceran del Vall, Elisa; Lillo, Rosa E. (2026). DOI 10.5281/zenodo.21351703.',
                archive_url=partial.URL,member=name,crc32=f'{crc:08x}',sha256=hashlib.sha256(content).hexdigest(),
                license_evidence=evidence,
                file=str(image.relative_to(BASE)),bytes=len(content),transfer_bytes=remote.received,
                full_archive_verified=False,scope='Primera imagen accesible, no muestra representativa; revisar variante original/keypoints y etiqueta antes de usar.')
    save(out/'inventario.json',result)
    return result


def main():
    os.umask(0o077)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--incorporar',choices=['isignos','dactilologia'])
    args=parser.parse_args();ROOT.mkdir(parents=True,exist_ok=True,mode=0o700)
    if args.incorporar:
        result={'isignos':isignos,'dactilologia':fingerspelling}[args.incorporar]()
        print(json.dumps(dict(source=args.incorporar,status=result['status']),ensure_ascii=False))
    rows=[]
    for source in SOURCES:
        row=dict(source);folder={'isignos':'isignos','dactilologia-lse':'dactilologia'}.get(source['id'])
        if folder and (ROOT/folder/'inventario.json').exists():
            row['status']='muestra_local_incorporada';row['manifest']=str((ROOT/folder/'inventario.json').relative_to(BASE))
        rows.append(row)
    save(ROOT/'registro.json',dict(updated=datetime.now(timezone.utc).isoformat(),
        policy='Solo análisis privado no comercial; sin publicación, entrenamiento ni APIs externas. Licencia explícita preferida; excepción TDM no presumida.',sources=rows))
    links={'uvigo-health':'../reproduccion-2d/VALIDAR.html','bancolse':'../bancolse/VALIDAR.html',
           'isignos':'../../datos/fuentes-privadas/isignos/PS-NXG.mp4'}
    spelling=ROOT/'dactilologia/inventario.json'
    if spelling.exists():links['dactilologia-lse']='../../'+json.loads(spelling.read_text())['file']
    cards=[]
    for row in rows:
        action=f'<a href="{html.escape(links[row["id"]],quote=True)}">Abrir muestra local</a>' if row['id'] in links and 'local' in row['status'] else ''
        cards.append('<article><h2>'+html.escape(row['id'])+'</h2><b>'+html.escape(row['status'])+'</b><p>'+html.escape(row['use'])+'</p><p>'+html.escape(row['license'])+'</p><p>'+html.escape(row.get('caution',''))+'</p>'+action+'</article>')
    output=BASE/'outputs/fuentes';output.mkdir(parents=True,exist_ok=True,mode=0o700)
    (output/'ESTADO.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fuentes privadas LSE</title><style>body{font:17px/1.5 system-ui;background:#f5f0e7;color:#263e39;max-width:1100px;margin:35px auto;padding:20px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}article{background:white;padding:22px;border-radius:12px}b{font-size:14px}a{color:#17664c}</style><h1>Fuentes para análisis privado de LSE</h1><p>Inventario local. Las fuentes pendientes no se han incorporado como corpus. Sin publicación de materiales, entrenamiento ni APIs de IA externas. Las muestras no validan traducción o comprensión.</p><main>'+''.join(cards)+'</main></html>')
    print(json.dumps(dict(sources=len(rows),local_samples=sum('local' in r['status'] for r in rows),registry=str(ROOT/'registro.json')),ensure_ascii=False))


if __name__=='__main__':main()
