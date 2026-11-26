#!/usr/bin/env python3
"""Prepara el ensayo local del motor 2D compartido; no carga modelos ni fotos."""
import hashlib
import json
import os
from pathlib import Path
from reproducir_2d import validate,FACE,FEATURES

BASE=Path(__file__).resolve().parent


def payload(data):
    frames=validate(data)
    face_ids=sorted(set(FACE+[i for group in FEATURES for i in group]))
    def xy(p):return [p['x']*960,p['y']*540]
    output=[]
    for frame in frames:
        points=frame['points']
        output.append(dict(t_ms=frame['t_ms'],
            pose={str(i):xy(points['pose'][i]) for i in (11,12,13,14,15,16,23,24)} if points['pose'] else {},
            face={str(i):xy(points['face'][i]) for i in face_ids} if points['face'] else {},
            left_hand=[xy(p) for p in points['left_hand']],right_hand=[xy(p) for p in points['right_hand']]))
    if any(not f['pose'] for f in output):raise ValueError('El ensayo requiere cuerpo observado; no se completa por suposición')
    return dict(frames=output,fps=data['sample_fps'])


def main():
    os.umask(0o077)
    source=BASE/'outputs/movimiento-15fps/movimiento.json'
    observation=json.loads(source.read_text());data=payload(observation)
    output=BASE/'outputs/prototipo-modular';output.mkdir(parents=True,exist_ok=True,mode=0o700)
    template=(BASE/'modular.html').read_text();engine=(BASE/'modular.js').read_text()
    page=template.replace('__DATA__',json.dumps(data,separators=(',',':')).replace('<','\\u003c')).replace('__ENGINE__',engine)
    (output/'VALIDAR.html').write_text(page)
    summary=dict(status='technical_prototype_not_lse_validated',frames=len(data['frames']),fps=data['fps'],
        source_motion_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_url=observation['source_url'],
        license=observation['license'],appearances='two_synthetic_profiles_no_personal_photo',
        shared_renderer=True,arms='planar two-bone inverse kinematics',
        hands='shared topology driven by observed 2D points, not a full anatomical rig',
        occlusion='manual diagnostic layer controls, not depth inferred from corpus',
        synthetic_contact='left index fingertip to cheek marker, diagnostic only, not a sign',
        new_inference=False,face_personalization=False,translation=False,obs_integration=False)
    (output/'resumen.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(view=str(output/'VALIDAR.html'),frames=summary['frames'],new_inference=False),ensure_ascii=False))


if __name__=='__main__':main()
