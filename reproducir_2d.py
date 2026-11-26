#!/usr/bin/env python3
"""Reproduce observaciones existentes en SVG 2D, sin modelos ni interpolación."""
import hashlib
import html
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


def validate(observation):
    if observation.get('status') != 'complete':
        raise ValueError('Se requiere una extracción completa')
    frames = observation['frames']
    if not frames or len(frames) > 30 or observation['sample_fps'] != 5:
        raise ValueError('Solo muestra existente de hasta 30 fotogramas a 5 Hz')
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

    pose = groups['pose']
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


def build():
    motion = BASE/'outputs/movimiento/movimiento.json'
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
    parser.feed((BASE/'outputs/movimiento/VALIDAR.html').read_text())
    if not parser.text:
        raise ValueError('Falta traducción de referencia')
    output = BASE/'outputs/reproduccion-2d'
    output.mkdir(parents=True,exist_ok=True)
    svgs = [svg_frame(f,width,height) for f in frames]
    missing = [f['t_ms'] for f in frames if not f['points']['left_hand']]
    payload = dict(svg=svgs, times=[f['t_ms'] for f in frames],
                   missing=[not f['points']['left_hand'] or not f['points']['right_hand'] for f in frames],
                   start=observation['start_ms']/1000, fps=observation['sample_fps'])
    template = (BASE/'reproduccion_2d.html').read_text()
    page = template.replace('__VIDEO__',html.escape(video_name,quote=True)).replace('__TRANSLATION__',html.escape(parser.text))
    page = page.replace('__DATA__',json.dumps(payload,ensure_ascii=False).replace('<','\\u003c'))
    (output/'VALIDAR.html').write_text(page)
    (output/'fotograma.svg').write_text(svgs[0])
    report = dict(frames=len(frames), sample_fps=5, duration_ms=frames[-1]['t_ms']+200,
                  missing_left_hand_ms=missing, motion_sha256=hashlib.sha256(motion.read_bytes()).hexdigest(),
                  new_inference=False, interpolation=False, linguistic_review='pending',
                  source=observation['source_url'], license=observation['license'])
    (output/'resumen.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(vista=str(output/'VALIDAR.html'),**report),ensure_ascii=False))


if __name__ == '__main__':
    build()
