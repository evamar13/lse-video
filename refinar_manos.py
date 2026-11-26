#!/usr/bin/env python3
"""Segunda observación CPU sobre recortes del original; no sustituye la primera."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS',
            'TF_NUM_INTRAOP_THREADS','TF_NUM_INTEROP_THREADS'):
    os.environ[key]='2'
import argparse
import hashlib
import html
import itertools
import json
import math
from pathlib import Path
import sys
import time
import uuid

BASE=Path(__file__).resolve().parent
MODEL_URL='https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
MODEL_SHA='fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1'


def crop_box(groups,width,height):
    points=[p for key in ('left_hand','right_hand') for p in groups[key]]
    if not points:return None
    xs=[p['x']*width for p in points];ys=[p['y']*height for p in points]
    cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
    side=max(max(xs)-min(xs),max(ys)-min(ys),64)*2
    return (max(0,int(cx-side/2)),max(0,int(cy-side/2)),
            min(width,math.ceil(cx+side/2)),min(height,math.ceil(cy+side/2)))


def restore(points,box,width,height):
    x,y,x2,y2=box
    return [dict(x=(x+p.x*(x2-x))/width,y=(y+p.y*(y2-y))/height,
                 z_crop=p.z,visibility=None,presence=None) for p in points]


def assign(original,candidates,width,height):
    """Asociación espacial al canal previo, no por orden ni etiqueta de lateralidad."""
    names=[name for name in ('left_hand','right_hand') if original[name]]
    if not names or len(candidates)<len(names):return {},'deteccion_insuficiente'
    def distance(a,b):return math.hypot((a['x']-b['x'])*width,(a['y']-b['y'])*height)
    ranked=sorted((sum(distance(original[n][0],candidates[i][0]) for n,i in zip(names,perm)),perm)
                  for perm in itertools.permutations(range(len(candidates)),len(names)))
    if len(ranked)>1 and ranked[1][0]-ranked[0][0]<8:return {},'asociacion_ambigua'
    result={}
    for name,i in zip(names,ranked[0][1]):
        palm=max(distance(original[name][0],original[name][j]) for j in (5,9,17))
        if distance(original[name][0],candidates[i][0])>max(12,.6*palm):
            return {},'desplazamiento_de_muneca'
        result[name]=candidates[i]
    # Un canal antes ausente no se recupera por adivinar lateralidad.
    return result,'candidato_sin_validar'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all',action='store_true',help='29 muestras; por defecto tres fotogramas piloto')
    parser.add_argument('--galeria',action='store_true',help='Reconstruir solo HTML desde resultados; no cargar modelo')
    args=parser.parse_args()
    out=BASE/'outputs'/('manos-detalle' if args.all else 'manos-piloto-v2')
    if args.galeria:
        write_gallery(json.loads((out/'candidatos.json').read_text()),out)
        return
    model=Path.home()/'AI Models/mediapipe/hand-v1/hand_landmarker.task'
    if hashlib.sha256(model.read_bytes()).hexdigest()!=MODEL_SHA:raise ValueError('Modelo no verificado')
    sys.path.insert(0,str(BASE.parent/'AI Tools/tools'))
    import recursos_locales as guard
    import telemetria
    data=json.loads((BASE/'outputs/movimiento/movimiento.json').read_text())
    from reproducir_2d import validate
    validate(data)
    source=BASE/'datos/videos'/data['video_file']
    if hashlib.sha256(source.read_bytes()).hexdigest()!=data['video_sha256']:raise ValueError('Original modificado')
    if (out/'candidatos.json').exists():raise FileExistsError('Conservar observación existente; no repetir inferencias automáticamente')
    out.mkdir(exist_ok=True,parents=True)
    records=[];metrics=[];started=time.monotonic();run=uuid.uuid4().hex
    with guard.turno_cpu('LSE Video: detalle de manos'):
        import cv2
        import mediapipe as mp
        cv2.setNumThreads(2)
        cap=cv2.VideoCapture(str(source))
        options=mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model),delegate=mp.tasks.BaseOptions.Delegate.CPU),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,num_hands=2,
            min_hand_detection_confidence=.6,min_hand_presence_confidence=.6)
        try:
            with mp.tasks.vision.HandLandmarker.create_from_options(options) as detector:
                indices=range(len(data['frames'])) if args.all else (0,10,20)
                for index in indices:
                    if time.monotonic()-started>90:raise TimeoutError('Presupuesto temporal agotado')
                    if index%5==0:
                        m=guard.medir();metrics.append(m)
                        if guard.causa(m,runtime=True):raise guard.TrabajoAplazado('Recursos ocupados')
                    frame=data['frames'][index]
                    cap.set(cv2.CAP_PROP_POS_MSEC,frame['source_t_ms']);ok,image=cap.read()
                    if not ok:raise ValueError('Fotograma no decodificado')
                    h,w=image.shape[:2];box=crop_box(frame['points'],w,h)
                    if box is None:continue
                    x,y,x2,y2=box;crop=image[y:y2,x:x2]
                    t=time.monotonic()
                    candidates=[];classified=[];inputs=[]
                    for name in ('left_hand','right_hand'):
                        if not frame['points'][name]:continue
                        isolated={k:frame['points'][k] if k==name else [] for k in ('left_hand','right_hand')}
                        local_box=crop_box(isolated,w,h);a,b,c,d=local_box
                        hand_crop=image[b:d,a:c]
                        call_start=time.monotonic()
                        result=detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=cv2.cvtColor(hand_crop,cv2.COLOR_BGR2RGB)))
                        telemetria.operacion('hand_landmark_detection','mediapipe-hand-v1',proj='LSE Video',
                            task='detalle-manos-20261126',agent='motion.hand_refiner',duration=time.monotonic()-call_start,id=f'{run}:{index}:{name}')
                        local=[restore(points,local_box,w,h) for points in result.hand_landmarks]
                        # Elegir dentro del recorte por cercanía a la muñeca del canal de origen.
                        if local:
                            wrist=frame['points'][name][0]
                            best=min(range(len(local)),key=lambda i:math.hypot((local[i][0]['x']-wrist['x'])*w,(local[i][0]['y']-wrist['y'])*h))
                            candidates.append(local[best])
                            classified.append([dict(label=c.category_name,score=c.score) for c in result.handedness[best]])
                        inputs.append(dict(channel=name,crop_box=local_box,detected=len(local)))
                    seconds=time.monotonic()-t
                    matched,status=assign(frame['points'],candidates,w,h)
                    # Se conservan todos los candidatos, incluidos los rechazados.
                    records.append(dict(index=index,t_ms=frame['t_ms'],decoded_source_t_ms=cap.get(cv2.CAP_PROP_POS_MSEC),
                        crop_box=box,source_size=[w,h],candidates=candidates,matched=matched,status=status,
                        handedness=classified,inputs=inputs,
                        seconds=seconds))
                    checkpoint=out/'candidatos.partial.json'
                    temporary=out/'candidatos.partial.tmp'
                    temporary.write_text(json.dumps(dict(status='incomplete',model_sha256=MODEL_SHA,
                        source_motion_sha256=hashlib.sha256((BASE/'outputs/movimiento/movimiento.json').read_bytes()).hexdigest(),
                        frames=records,metrics=metrics),ensure_ascii=False,allow_nan=False)+'\n')
                    temporary.replace(checkpoint)
                    cv2.imwrite(str(out/f'{index:02d}-original.png'),crop)
                    preview=crop.copy()
                    from reproducir_2d import HAND
                    coarse=crop.copy()
                    for name in ('left_hand','right_hand'):
                        points=frame['points'][name]
                        if not points:continue
                        for a,b in HAND:
                            pixel=lambda p:(round(p['x']*w-x),round(p['y']*h-y))
                            cv2.line(coarse,pixel(points[a]),pixel(points[b]),(20,130,240),1)
                    cv2.imwrite(str(out/f'{index:02d}-previo.png'),coarse)
                    for points in candidates:
                        for a,b in HAND:
                            pixel=lambda p:(round(p['x']*w-x),round(p['y']*h-y))
                            cv2.line(preview,pixel(points[a]),pixel(points[b]),(80,200,40),1)
                    cv2.imwrite(str(out/f'{index:02d}-candidato.png'),preview)
                    time.sleep(.15)
        finally:cap.release()
    report=dict(model_url=MODEL_URL,model_sha256=MODEL_SHA,delegate='CPU',
        source_motion_sha256=hashlib.sha256((BASE/'outputs/movimiento/movimiento.json').read_bytes()).hexdigest(),
        status='candidate_not_validated',frames=records,metrics=metrics,
        elapsed_seconds=time.monotonic()-started,interpolation=False,
        z_semantics='z_crop is raw model depth relative to wrist within crop; not comparable across groups')
    (out/'candidatos.json').write_text(json.dumps(report,ensure_ascii=False,allow_nan=False)+'\n')
    (out/'candidatos.partial.json').unlink(missing_ok=True)
    write_gallery(report,out)
    print(json.dumps(dict(frames=len(records),matched=sum(bool(r['matched']) for r in records),
                         seconds=report['elapsed_seconds'],metrics=metrics),ensure_ascii=False))


def write_gallery(report,out):
    rows=[]
    for row in report['frames']:
        i=row['index']
        imgs=''.join(f'<figure><img loading="lazy" src="{i:02d}-{suffix}.png" alt="{label}"><figcaption>{label}</figcaption></figure>'
                     for suffix,label in [('original','Original'),('previo','Detección inicial'),('candidato','Recortes individuales')])
        rows.append(f'<section><h2>{row["t_ms"]/1000:.1f} s · {html.escape(row["status"])}</h2><div>{imgs}</div></section>')
    (out/'VALIDAR.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8"><title>Detalle de manos</title><style>body{font:17px system-ui;margin:30px;background:#f5f0e7;color:#263e39}section{margin:24px 0}section div{display:flex;gap:12px}figure{margin:0;flex:1;min-width:0}img{width:100%}figcaption{padding:10px}</style><h1>Comparación de manos</h1><p>Fuente: LSE-Health-UVigo · CC BY-NC 4.0 según ficha institucional · uso no comercial. Dos estimaciones, ninguna validada como verdad de referencia. La asociación espacial no mide exactitud. No se inventan dedos ocultos.</p><a href="../reproduccion-2d/VALIDAR.html">Volver al visor</a>'+''.join(rows)+'</html>')


if __name__=='__main__':main()
