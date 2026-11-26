#!/usr/bin/env python3
"""Reproduce observaciones existentes en SVG 2D, sin modelos ni interpolación."""
import hashlib
import html
import argparse
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
HAND = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),
        (9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),
        (0,17),(17,18),(18,19),(19,20)]
BODY = [(11,12),(11,13),(13,15),(12,14),(14,16),(11,23),(12,24),(23,24)]
FACE = [10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,
        400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109,10]
FEATURES = [[61,40,37,0,267,270,291,321,314,17,84,91,61],
            [78,81,13,311,308,402,14,87,78],
            [33,160,158,133,153,144,33],[362,385,387,263,373,380,362],
            [70,63,105,66,107],[336,296,334,293,300]]
FINGERS=[('Pulgar',[0,1,2,3,4],'#ac506a'),('Índice',[0,5,6,7,8],'#267cba'),
         ('Medio',[5,9,10,11,12],'#9a6921'),('Anular',[9,13,14,15,16],'#7655af'),
         ('Meñique',[13,17,18,19,20],'#207e61')]


def hand_detail(points,width,height):
    if not points:
        return '<p class="alert">Mano no detectada. No se reconstruyen dedos ocultos.</p>'
    xs=[p['x']*width for p in points];ys=[p['y']*height for p in points]
    side=max(max(xs)-min(xs),max(ys)-min(ys),20)*1.5
    cx=(min(xs)+max(xs))/2;cy=(min(ys)+max(ys))/2
    result=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{cx-side/2:.3f} {cy-side/2:.3f} {side:.3f} {side:.3f}" role="img" aria-label="Detalle de las 21 articulaciones observadas">']
    # Grosor en unidades relativas al encuadre; zoom no implica más precisión.
    def coord(i):return f'{xs[i]:.3f},{ys[i]:.3f}'
    result.append(f'<polygon points="{" ".join(coord(i) for i in [0,5,9,13,17])}" fill="#e8e2d5" stroke="#8a8a80" stroke-width="{side*.004}"/>')
    for name,chain,color in FINGERS:
        result.append(f'<polyline points="{" ".join(coord(i) for i in chain)}" fill="none" stroke="{color}" stroke-width="{side*.012}" stroke-linecap="round" stroke-linejoin="round"><title>{name}</title></polyline>')
        for i in chain[1:]:
            result.append(f'<circle cx="{xs[i]:.3f}" cy="{ys[i]:.3f}" r="{side*.012}" fill="white" stroke="{color}" stroke-width="{side*.005}"><title>{name} · punto {i}</title></circle>')
            result.append(f'<text x="{xs[i]+side*.018:.3f}" y="{ys[i]-side*.015:.3f}" font-size="{side*.035}" fill="{color}">{i}</text>')
    result.append(f'<circle cx="{xs[0]}" cy="{ys[0]}" r="{side*.013}" fill="#4a6159"><title>0 · muñeca</title></circle></svg>')
    return ''.join(result)


def validate(observation):
    if observation.get('status') != 'complete':
        raise ValueError('Se requiere una extracción completa')
    frames = observation['frames']
    fps=observation['sample_fps']
    if fps not in (5,15) or not frames or len(frames)>6*fps:
        raise ValueError('Solo perfiles acotados de hasta 6 s a 5 o 15 Hz')
    previous = -1
    for frame in frames:
        t = frame['t_ms']
        if not isinstance(t, (int, float)) or not math.isfinite(t) or t <= previous:
            raise ValueError('Tiempos no válidos')
        previous = t
        if t > 6000:
            raise ValueError('Muestra fuera de alcance')
        for name, count in [('pose',33),('face',478),('left_hand',21),('right_hand',21)]:
            points = frame['points'][name]
            if len(points) not in (0,count):
                raise ValueError('Detección incompleta de puntos')
            if any(not math.isfinite(p[axis]) for p in points for axis in ('x','y')):
                raise ValueError('Coordenadas no finitas')
    return frames


def svg_frame(frame, width, height):
    groups = frame['points']
    result = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Reproducción geométrica 2D del movimiento observado">',
              f'<rect width="{width}" height="{height}" fill="#f5f0e7"/>']

    def line(points, indices, color, stroke=2, close=False):
        if not points:
            return
        coords = ' '.join(f'{points[i]["x"]*width:.2f},{points[i]["y"]*height:.2f}' for i in indices)
        tag = 'polygon' if close else 'polyline'
        result.append(f'<{tag} points="{coords}" fill="{"#cadbd7" if close else "none"}" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"/>')

    pose = [dict(p) for p in groups['pose']]
    # Solo anclaje visual: no modificar la observación original de cuerpo/manos.
    if pose:
        for name,index in [('left_hand',15),('right_hand',16)]:
            if groups[name]:pose[index]=groups[name][0]
    line(pose,[11,12,24,23], '#728681',2,True)
    for a,b in BODY:
        line(pose,[a,b],'#58716b',6)
    face = groups['face']
    line(face,FACE,'#ad8d76',2)
    for feature in FEATURES:
        line(face,feature,'#715566',1.7)
    for name, color in [('left_hand','#167b69'),('right_hand','#c15d30')]:
        points = groups[name]
        result.append(f'<g data-channel="{name}" data-present="{str(bool(points)).lower()}">')
        for a,b in HAND:
            line(points,[a,b],color,2.6)
        for p in points:
            result.append(f'<circle cx="{p["x"]*width:.2f}" cy="{p["y"]*height:.2f}" r="2" fill="{color}"/>')
        result.append('</g>')
    result.append('</svg>')
    return ''.join(result)


def build(fluido=False):
    motion_folder='movimiento-15fps' if fluido else 'movimiento'
    motion = BASE/'outputs'/motion_folder/'movimiento.json'
    observation = json.loads(motion.read_text())
    frames = validate(observation)
    video_name = observation['video_file']
    if Path(video_name).name != video_name:
        raise ValueError('Nombre de vídeo no válido')
    original = BASE/'datos/videos'/video_name
    if hashlib.sha256(original.read_bytes()).hexdigest() != observation['video_sha256']:
        raise ValueError('El original no coincide con la observación')
    # La relación de aspecto debe proceder del vídeo, nunca asumir imagen cuadrada.
    import cv2
    cap = cv2.VideoCapture(str(original))
    try:
        width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.set(cv2.CAP_PROP_POS_MSEC,frames[0]['source_t_ms'])
        preview_ok,preview=cap.read()
    finally:
        cap.release()
    if width <= 0 or height <= 0:
        raise ValueError('No se ha podido verificar el tamaño del original')
    width, height = 720, height*720/width
    # Leer la traducción conservada en la página técnica ya generada.
    from html.parser import HTMLParser
    class Translation(HTMLParser):
        active = False
        text = ''
        def handle_starttag(self,tag,attrs):
            if tag == 'blockquote': self.active = True
        def handle_endtag(self,tag):
            if tag == 'blockquote': self.active = False
        def handle_data(self,data):
            if self.active: self.text += data
    parser = Translation()
    parser.feed((BASE/'outputs'/motion_folder/'VALIDAR.html').read_text())
    if not parser.text:
        raise ValueError('Falta traducción de referencia')
    output = BASE/'outputs'/('reproduccion-2d-15fps' if fluido else 'reproduccion-2d')
    output.mkdir(parents=True,exist_ok=True)
    if not preview_ok:raise ValueError('No se pudo crear la vista previa del original')
    preview=cv2.resize(preview,(720,round(preview.shape[0]*720/preview.shape[1])))
    if not cv2.imwrite(str(output/'original-preview.jpg'),preview,[cv2.IMWRITE_JPEG_QUALITY,85]):
        raise ValueError('No se pudo guardar la vista previa')
    svgs = [svg_frame(f,width,height) for f in frames]
    missing = [f['t_ms'] for f in frames if not f['points']['left_hand']]
    payload = dict(svg=svgs, times=[f['t_ms'] for f in frames],
                   missing=[not f['points']['left_hand'] or not f['points']['right_hand'] for f in frames],
                   start=observation['start_ms']/1000, fps=observation['sample_fps'])
    payload['hands']=[[hand_detail(f['points'][name],width,height) for name in ('left_hand','right_hand')] for f in frames]
    candidate_file=BASE/'outputs/manos-detalle/candidatos.json'
    payload['experiments']={}
    if candidate_file.exists() and not fluido:
        from copy import deepcopy
        experiment=json.loads(candidate_file.read_text())
        if experiment['source_motion_sha256']!=hashlib.sha256(motion.read_bytes()).hexdigest():
            raise ValueError('Los candidatos pertenecen a otra extracción')
        for record in experiment['frames']:
            i=record['index'];candidate=deepcopy(frames[i])
            candidate['points'].update(record['matched'])
            payload['experiments'][str(i)]=dict(svg=svg_frame(candidate,width,height),
                hands=[hand_detail(candidate['points'][name],width,height) for name in ('left_hand','right_hand')],
                accepted=bool(record['matched']),status=record['status'])
    template = (BASE/'reproduccion_2d.html').read_text()
    page = template.replace('__VIDEO__',html.escape(video_name,quote=True)).replace('__TRANSLATION__',html.escape(parser.text))
    page = page.replace('__MOTION_FOLDER__',motion_folder)
    alternative='../reproduccion-2d/VALIDAR.html' if fluido else '../reproduccion-2d-15fps/VALIDAR.html'
    page = page.replace('__ALTERNATIVE_URL__',alternative).replace('__ALTERNATIVE_LABEL__','Comparar con la muestra inicial (5 Hz)' if fluido else 'Ver muestra de movimiento más fluida (15 Hz)')
    page = page.replace('__DATA__',json.dumps(payload,ensure_ascii=False).replace('<','\\u003c'))
    (output/'VALIDAR.html').write_text(page)
    (output/'fotograma.svg').write_text(svgs[0])
    report = dict(frames=len(frames), sample_fps=observation['sample_fps'], duration_ms=round(frames[-1]['t_ms']+1000/observation['sample_fps']),
                  missing_left_hand_ms=missing, motion_sha256=hashlib.sha256(motion.read_bytes()).hexdigest(),
                  new_inference=False, interpolation=False, linguistic_review='pending',
                  source=observation['source_url'], license=observation['license'])
    report['hand_candidate_frames']=sum(bool(r['accepted']) for r in payload['experiments'].values())
    report['hand_candidate_status']='experimental_not_validated' if payload['experiments'] else 'not_available'
    (output/'resumen.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(vista=str(output/'VALIDAR.html'),**report),ensure_ascii=False))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fluido',action='store_true',help='Leer la extracción independiente de 15 Hz')
    build(parser.parse_args().fluido)
