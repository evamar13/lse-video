#!/usr/bin/env python3
"""Extracción experimental CPU de un único fragmento (máximo 6 s y 5 muestras/s)."""
import os
# Son indicaciones de hilos para bibliotecas; MediaPipe no expone un tope universal.
for variable in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS',
                 'TF_NUM_INTRAOP_THREADS','TF_NUM_INTEROP_THREADS']:
    try:
        os.environ[variable]=str(min(2,max(1,int(os.environ.get(variable,'2')))))
    except ValueError:
        os.environ[variable]='2'
import argparse
import hashlib
import html
import importlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

MODEL_SHA='e2dab61191e2dcd0a15f943d8e3ed1dce13c82dfa597b9dd39f562975a50c3f8'
MODEL_URL='https://storage.googleapis.com/mediapipe-models/holistic_landmarker/holistic_landmarker/float16/1/holistic_landmarker.task'
HAND_EDGES=[(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),
            (10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),(0,17),(17,18),(18,19),(19,20)]
BODY_EDGES=[(11,12),(11,13),(13,15),(12,14),(14,16),(11,23),(12,24),(23,24)]
MOUTH=[61,146,91,181,84,17,314,405,321,375,291,308,324,318,402,317,14,87,178,88,95,78]

def serialize(points):
    result=[]
    for point in points:
        if not all(math.isfinite(float(getattr(point,k))) for k in ['x','y','z']):
            raise ValueError('Coordenadas no finitas; no se sustituyen por puntos inventados.')
        result.append({key:float(getattr(point,key)) if getattr(point,key,None) is not None else None
                       for key in ['x','y','z','visibility','presence']})
    return result

def draw(cv2,image,points,edges,color):
    height,width=image.shape[:2]
    def pixel(p):return (round(p['x']*width),round(p['y']*height))
    for a,b in edges:
        if max(a,b)<len(points):cv2.line(image,pixel(points[a]),pixel(points[b]),color,2)
    for point in points:cv2.circle(image,pixel(point),2,color,-1)

def make_page(output,video_name,start,end,translation,summary):
    source='../../datos/videos/'+video_name
    counts=summary['detection_counts']
    text=f'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LSE Video — primera extracción</title><style>
body{{font:17px/1.6 system-ui;background:#f5f5f2;color:#17332f;max-width:1200px;margin:40px auto;padding:20px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}}section{{background:white;padding:18px;border-radius:12px}}
video{{width:100%;background:#132229}}.note{{background:#fff0ca;padding:16px}}h1{{line-height:1.2}}a{{color:#245b48}}
</style><h1>Primera extracción de movimiento</h1>
<p class="note">Estos puntos son estimaciones del vídeo original. No son signos nuevos, una traducción automática ni una persona generada. Los dos vídeos no tienen audio.</p>
<div class="grid"><section><h2>Original</h2><video controls preload="none" src="{html.escape(source,quote=True)}#t={start},{end}"></video><p>Intervalo fuente: {start:.3f}–{end:.3f} s.</p></section>
<section><h2>Original con seguimiento superpuesto</h2><video controls preload="metadata" src="seguimiento.mp4"></video><p>CPU · {summary['frames']} fotogramas analizados · {summary['sample_fps']} muestras/s. Verde y naranja: manos; azul: rostro/boca; amarillo: cuerpo.</p></section></div>
<h2>Traducción escrita de referencia</h2><blockquote>{html.escape(translation)}</blockquote>
<h2>Qué se ha detectado</h2><p>Fotogramas con cuerpo: {counts['pose']}; rostro: {counts['face']}; mano izquierda: {counts['left_hand']}; mano derecha: {counts['right_hand']}, de {summary['frames']}.</p>
<p>Detección no equivale a exactitud. Los puntos de boca describen geometría estimada, no su función gramatical. La baja frecuencia puede perder movimientos rápidos y no sirve todavía como captura completa para entrenar generación.</p>
<p>Eva puede valorar visibilidad y aspecto; la corrección de LSE requiere personas competentes. La lectura de la traducción no certifica los signos.</p>
<p>Datos locales: <a href="movimiento.json">coordenadas y procedencia</a> · <a href="resumen.json">resumen técnico</a>. No publicar derivados del corpus automáticamente.</p></html>'''
    (output/'VALIDAR.html').write_text(text)

def main():
    base=Path(__file__).resolve().parent
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guard-tools',type=Path,default=base.parent/'AI Tools/tools',
                        help='Adaptador de recursos_locales.py y telemetria.py del espacio de trabajo.')
    parser.add_argument('--model',type=Path,default=Path(os.environ.get('AI_MODELS_DIR',str(Path.home()/'AI Models')))/'mediapipe/holistic-v1/holistic_landmarker.task')
    parser.add_argument('--ffmpeg',default=shutil.which('ffmpeg'))
    parser.add_argument('--task',required=True)
    parser.add_argument('--agent',default='motion.extractor')
    parser.add_argument('--seconds',type=float,default=6)
    parser.add_argument('--fps',type=int,default=5)
    args=parser.parse_args()
    if not 0<args.seconds<=6 or not 1<=args.fps<=5:parser.error('Muestra máxima: 6 segundos y 5 muestras/s.')
    if not args.ffmpeg or not Path(args.ffmpeg).is_file():parser.error('Indicar un ejecutable FFmpeg existente con --ffmpeg.')
    if not (args.guard_tools/'recursos_locales.py').is_file() or not (args.guard_tools/'telemetria.py').is_file():
        parser.error('Falta adaptador de recursos/contabilidad. No se ejecuta sin guardia; consultar MOVIMIENTO.md.')
    if not args.model.is_file():parser.error('Falta el modelo local; consultar MOVIMIENTO.md. No se descarga automáticamente.')
    if hashlib.sha256(args.model.read_bytes()).hexdigest()!=MODEL_SHA:parser.error('Modelo no coincide con la versión fijada.')
    sys.path.insert(0,str(args.guard_tools.resolve()))
    guard=importlib.import_module('recursos_locales');telemetry=importlib.import_module('telemetria')
    selection=json.loads((base/'datos/auditoria.json').read_text())['shortlist']
    # El fragmento con más etiquetas observadas proporciona una referencia técnica adicional.
    inventories=json.loads((base/'datos/contratos/inventario.json').read_text())
    chosen=max(inventories,key=lambda r:r['annotated_glosses'])['file']
    sample=next(r for r in selection if chosen==Path(r['elan_file']).stem+'-'+r['annotation_id']+'.json')
    packets=json.loads((base/'datos/contratos'/chosen).read_text())
    files=json.loads((base/'datos/descarga-muestra.json').read_text())['files']
    media=next(r for r in files if Path(r['file']).stem==Path(sample['elan_file']).stem)
    video=base/'datos/videos'/media['file']
    if hashlib.sha256(video.read_bytes()).hexdigest()!=media['sha256']:raise ValueError('Vídeo modificado desde la descarga.')
    output=base/'outputs/movimiento';output.mkdir(parents=True,exist_ok=True)
    if (output/'resumen.json').exists():raise FileExistsError('La muestra ya existe; conservarla antes de repetir inferencias.')
    start=sample['start_ms']/1000;duration=min(args.seconds,(sample['end_ms']-sample['start_ms'])/1000)
    frames=[];counts=dict.fromkeys(['pose','face','left_hand','right_hand'],0)
    measurements=[];run_id=uuid.uuid4().hex;started=time.monotonic();status='running';thread_hint=2
    try:
        with guard.turno_cpu('LSE Video: muestra de movimiento CPU'):
            # Importación y carga solo después de adquirir el bloqueo y comprobar recursos.
            thread_hint=guard.politica()['hilos_cpu']
            for variable in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','TF_NUM_INTRAOP_THREADS','TF_NUM_INTEROP_THREADS']:
                os.environ[variable]=str(thread_hint)
            import cv2
            import mediapipe as mp
            cv2.setNumThreads(thread_hint)
            capture=cv2.VideoCapture(str(video))
            encoder=None
            options=mp.tasks.vision.HolisticLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(args.model),delegate=mp.tasks.BaseOptions.Delegate.CPU),
                running_mode=mp.tasks.vision.RunningMode.VIDEO,output_face_blendshapes=True)
            try:
                with mp.tasks.vision.HolisticLandmarker.create_from_options(options) as model:
                    total=math.ceil(duration*args.fps)
                    for index in range(total):
                        if time.monotonic()-started>90:raise TimeoutError('Límite temporal de 90 segundos; conservar avance.')
                        if index%5==0:
                            metric=guard.medir();measurements.append(metric)
                            reason=guard.causa(metric,runtime=True)
                            if reason:raise guard.TrabajoAplazado('Muestra pausada: '+reason)
                        relative=index/args.fps;absolute=start+relative
                        capture.set(cv2.CAP_PROP_POS_MSEC,absolute*1000)
                        ok,image=capture.read()
                        if not ok:raise ValueError('No se pudo decodificar un fotograma; no se omite silenciosamente.')
                        decoded_source_ms=float(capture.get(cv2.CAP_PROP_POS_MSEC))
                        original_h,original_w=image.shape[:2]
                        width=min(960,original_w);height=round(original_h*width/original_w)//2*2;width=width//2*2
                        image=cv2.resize(image,(width,height))
                        rgb=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
                        infer_start=time.monotonic()
                        result=model.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb),round(relative*1000))
                        elapsed=time.monotonic()-infer_start
                        telemetry.operacion('landmark_detection','mediapipe-holistic-v1',proj='LSE Video',task=args.task,
                                             agent=args.agent,duration=elapsed,id=f'{run_id}:{index}')
                        groups={'pose':serialize(result.pose_landmarks),'face':serialize(result.face_landmarks),
                                'left_hand':serialize(result.left_hand_landmarks),'right_hand':serialize(result.right_hand_landmarks)}
                        for key,points in groups.items():counts[key]+=bool(points)
                        blendshapes=[{'name':r.category_name,'score':float(r.score)} for r in (result.face_blendshapes or [])]
                        frames.append({'t_ms':round(relative*1000),'source_t_ms':round(absolute*1000),
                                       'decoded_source_t_ms':decoded_source_ms if math.isfinite(decoded_source_ms) else None,
                                       'points':groups,'face_blendshapes':blendshapes,'inference_seconds':elapsed})
                        draw(cv2,image,groups['pose'],BODY_EDGES,(0,220,220))
                        draw(cv2,image,groups['left_hand'],HAND_EDGES,(60,230,70))
                        draw(cv2,image,groups['right_hand'],HAND_EDGES,(20,150,250))
                        face=groups['face'];mouth=[face[i] for i in MOUTH if i<len(face)]
                        draw(cv2,image,mouth,[(i,i+1) for i in range(len(mouth)-1)],(255,160,70))
                        for point in face[::8]:cv2.circle(image,(round(point['x']*width),round(point['y']*height)),1,(255,160,70),-1)
                        if encoder is None:
                            log=(output/'ffmpeg.log').open('wb')
                            encoder=subprocess.Popen([args.ffmpeg,'-hide_banner','-loglevel','error','-nostdin','-y',
                              '-f','rawvideo','-pix_fmt','bgr24','-s',f'{width}x{height}','-r',str(args.fps),'-i','pipe:0',
                              '-an','-c:v','libx264','-threads','2','-preset','ultrafast','-crf','20','-pix_fmt','yuv420p',
                              '-movflags','+faststart',str(output/'seguimiento.mp4')],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=log)
                        encoder.stdin.write(image.tobytes())
                        time.sleep(0.15)
                status='complete'
            finally:
                capture.release()
                if encoder:
                    encoder.stdin.close()
                    code=encoder.wait(timeout=15);log.close()
                    if code:raise RuntimeError('No se pudo codificar la vista previa; revisar log local.')
    except Exception as exc:
        status='paused_or_failed'
        print(str(exc),file=sys.stderr)
    finally:
        observation={'version':'0.1-motion-observation','status':status,'run_id':run_id,
            'project':'LSE Video','task':args.task,'agent':args.agent,'source_url':'https://zenodo.org/records/10234465',
            'license':'CC BY-NC 4.0 según ficha del corpus; no redistribuir automáticamente',
            'video_file':media['file'],'video_sha256':media['sha256'],'start_ms':sample['start_ms'],
            'model_url':MODEL_URL,'model_sha256':MODEL_SHA,'delegate':'CPU','sample_fps':args.fps,
            'coordinates':{'x_y':'normalized image coordinates; may lie outside the image',
                           'z':'raw model-specific depth estimate; not metric or comparable across groups',
                           'not_provided':['finger_rotations','verified_contacts','linguistic_mouth_function']},
            'timing_semantics':'source_t_ms is requested seek; decoded_source_t_ms, when present, is reported by decoder',
            'linguistic_review':'pending','frames':frames}
        (output/'movimiento.json').write_text(json.dumps(observation,ensure_ascii=False,allow_nan=False)+'\n')
        summary={'status':status,'frames':len(frames),'sample_fps':args.fps,'detection_counts':counts,
                 'duration_seconds':time.monotonic()-started,'metrics_samples':measurements,
                 'model_delegate':'CPU','thread_hint':thread_hint,'threads':'OpenCV and environment configured; no hard MediaPipe thread cap exposed',
                 'linguistic_review':'pending','preview_is_original_with_overlay':True}
        (output/'resumen.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
        if status=='complete':make_page(output,media['file'],start,start+duration,sample['translation'],summary)
        print(json.dumps({k:summary[k] for k in ['status','frames','detection_counts','duration_seconds']},ensure_ascii=False))
    return 0 if status=='complete' else 75

if __name__=='__main__':raise SystemExit(main())
