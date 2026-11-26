#!/usr/bin/env python3
"""Expedientes privados de preparación de fotos; no genera imágenes ni llama a APIs."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import uuid

ROOT=Path(__file__).resolve().parent/'datos/avatar-personal/casos'
FORMATS={'.png','.jpg','.jpeg','.webp','.heic','.heif'}


def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def case_path(case):
    if not re.fullmatch('[a-f0-9]{12}',case):raise ValueError('ID de caso no válido')
    path=ROOT/case
    if path.is_symlink():raise ValueError('No se admiten enlaces en expedientes')
    return path


def write(case,data):
    path=case_path(case);path.mkdir(parents=True,exist_ok=True,mode=0o700)
    data['updated_utc']=now()
    tmp=path/'expediente.tmp'
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');tmp.chmod(0o600)
    tmp.replace(path/'expediente.json')


def read(case):return json.loads((case_path(case)/'expediente.json').read_text())


def copy_photo(source,destination):
    source=Path(source)
    if not source.is_file() or source.suffix.lower() not in FORMATS:
        raise ValueError('Se necesita una foto PNG, JPEG, WebP o HEIC/HEIF')
    if not 0<source.stat().st_size<=25*1024*1024:raise ValueError('Límite de entrada: 25 MiB')
    destination=destination.with_suffix(source.suffix.lower())
    if destination.exists():raise FileExistsError('Conservar la versión existente')
    shutil.copyfile(source,destination);destination.chmod(0o600)
    dimensions=None
    if Path('/usr/bin/sips').is_file():
        result=subprocess.run(['/usr/bin/sips','-g','pixelWidth','-g','pixelHeight',str(destination)],capture_output=True,text=True,timeout=10)
        width=re.search(r'pixelWidth:\s*(\d+)',result.stdout);height=re.search(r'pixelHeight:\s*(\d+)',result.stdout)
        if result.returncode or not width or not height:
            destination.unlink()
            raise ValueError('No se ha podido leer esta imagen; conservar el original y revisar el formato')
        dimensions=dict(width=int(width[1]),height=int(height[1]))
    return dict(file=destination.name,sha256=sha(destination),dimensions=dimensions)


def new_case(photo):
    case=uuid.uuid4().hex[:12];folder=case_path(case)
    folder.mkdir(parents=True,mode=0o700)
    try:original=copy_photo(photo,folder/'original')
    except Exception:
        shutil.rmtree(folder)
        raise
    write(case,dict(version='1.0',created_utc=now(),status='needs_visual_assessment',original=original,
                   candidates=[],selected=None,scope='private_appearance_reference',
                   visual_checks='pending',linguistic_validation='not_applicable'))
    return case


def attach(case,photo,origin,changes):
    data=read(case)
    if len(data['candidates'])>=2:raise ValueError('Dos candidatas ya registradas; no generar otra automáticamente')
    if origin not in ('ia','original'):raise ValueError('Origen no válido')
    if origin=='ia' and not changes:raise ValueError('Registrar qué partes se reconstruyeron o cambiaron')
    candidate=uuid.uuid4().hex[:12]
    image=copy_photo(photo,case_path(case)/('candidata-'+candidate))
    data['candidates'].append(dict(id=candidate,**image,origin=origin,changes=changes,
                                   review='pending',created_utc=now(),tokens=None))
    # Una nueva candidata no revoca la referencia ya aceptada.
    data['status']='appearance_ready' if data['selected'] else 'needs_appearance_review'
    write(case,data)
    return candidate


def review(case,candidate,decision):
    if decision not in ('aceptar','rechazar'):raise ValueError('Decisión no válida')
    data=read(case)
    row=next((r for r in data['candidates'] if r['id']==candidate),None)
    if row is None:raise ValueError('Candidata desconocida')
    if sha(case_path(case)/row['file'])!=row['sha256']:raise ValueError('Imagen modificada desde su incorporación')
    row['review']='accepted' if decision=='aceptar' else 'rejected';row['reviewed_utc']=now()
    if decision=='aceptar':data['selected']=candidate
    elif data['selected']==candidate:data['selected']=None
    data['status']='appearance_ready' if data['selected'] else 'needs_appearance_review'
    write(case,data)


def resolver_referencia(case):
    data=read(case)
    row=next((r for r in data['candidates'] if r['id']==data['selected']),None)
    if data['status']!='appearance_ready' or row is None or row['review']!='accepted':
        raise ValueError('Falta una candidata aceptada explícitamente')
    path=case_path(case)/row['file']
    if sha(path)!=row['sha256']:raise ValueError('La referencia cambió; volver a revisar')
    return path


def main():
    os.umask(0o077)
    p=argparse.ArgumentParser(description=__doc__);commands=p.add_subparsers(dest='command',required=True)
    n=commands.add_parser('nuevo');n.add_argument('--foto',type=Path,required=True)
    a=commands.add_parser('adjuntar');a.add_argument('--caso',required=True);a.add_argument('--imagen',type=Path,required=True);a.add_argument('--origen',choices=['ia','original'],required=True);a.add_argument('--cambio',action='append',default=[])
    r=commands.add_parser('revisar');r.add_argument('--caso',required=True);r.add_argument('--candidata',required=True);r.add_argument('--decision',choices=['aceptar','rechazar'],required=True)
    f=commands.add_parser('resolver');f.add_argument('--caso',required=True)
    args=p.parse_args();ROOT.mkdir(parents=True,exist_ok=True,mode=0o700)
    if args.command=='nuevo':result=dict(case=new_case(args.foto),next='Revisión visual; reutilizar si sirve o preparar candidata con imagegen')
    elif args.command=='adjuntar':result=dict(candidate=attach(args.caso,args.imagen,args.origen,args.cambio),review='pending')
    elif args.command=='revisar':review(args.caso,args.candidata,args.decision);result=dict(status=read(args.caso)['status'])
    else:result=dict(reference=str(resolver_referencia(args.caso)))
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
