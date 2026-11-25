#!/usr/bin/env python3
"""Inspección determinista de ELAN. No descarga vídeos ni ejecuta modelos."""
import argparse
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

EXPECTED_MD5 = 'c3ca411d1ec24c4d4c39c250a60903da'

def audit(path):
    raw = path.read_bytes()
    digest = hashlib.md5(raw).hexdigest()
    if digest != EXPECTED_MD5:
        raise ValueError('El archivo no coincide con el MD5 del registro consultado; revisar versión.')
    tiers = Counter()
    candidates = []
    files = []
    with zipfile.ZipFile(path) as archive:
        for name in sorted(archive.namelist()):
            if not name.endswith('.eaf') or name.startswith('__MACOSX/'):
                continue
            info = archive.getinfo(name)
            if info.file_size > 5_000_000:
                raise ValueError('ELAN supera el límite de lectura: ' + name)
            root = ET.fromstring(archive.read(name))
            files.append(name)
            times = {s.get('TIME_SLOT_ID'): int(s.get('TIME_VALUE'))
                     for s in root.findall('./TIME_ORDER/TIME_SLOT') if s.get('TIME_VALUE')}
            for tier in root.findall('TIER'):
                tier_id = tier.get('TIER_ID', '')
                annotations = tier.findall('./ANNOTATION/ALIGNABLE_ANNOTATION')
                tiers[tier_id] += len(annotations)
                if tier_id.lower() != 'trad':
                    continue
                for item in annotations:
                    start = times.get(item.get('TIME_SLOT_REF1'))
                    end = times.get(item.get('TIME_SLOT_REF2'))
                    value = item.find('ANNOTATION_VALUE')
                    text = ''.join(value.itertext()).strip() if value is not None else ''
                    if start is None or end is None:
                        continue
                    if (5_000 <= end-start <= 12_000 and 35 <= len(text) <= 115
                            and not re.search(r'[\[\]<>]', text) and text.endswith(('.', '?', '!'))):
                        candidates.append({'elan_file': name, 'annotation_id': item.get('ANNOTATION_ID'),
                                           'start_ms': start, 'end_ms': end, 'translation': text,
                                           'status': 'mechanical_candidate_not_visually_or_linguistically_validated'})
    shortlist = []
    seen = set()
    for row in candidates:
        if row['elan_file'] not in seen:
            shortlist.append(row)
            seen.add(row['elan_file'])
        if len(shortlist) == 3:
            break
    return {'source': 'https://zenodo.org/records/10234465', 'md5': digest,
            'sha256': hashlib.sha256(raw).hexdigest(), 'elan_files': len(files),
            'aligned_annotations_by_tier': dict(tiers), 'mechanical_candidates': len(candidates),
            'shortlist': shortlist, 'videos_downloaded': 0, 'model_runs': 0,
            'limitations': ['Puntuación y duración no prueban que una frase sea autónoma.',
                            'Sin revisión de vídeo, calidad de poses ni comprensión humana.',
                            'No usar la selección automática como consejo sanitario.']}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', type=Path, default=Path(__file__).parent/'datos/anotaciones.zip')
    parser.add_argument('--output', type=Path, default=Path(__file__).parent/'datos/auditoria.json')
    args = parser.parse_args()
    if not args.zip.is_file():
        parser.error('Faltan las anotaciones. Consulta README.md; no se descargan automáticamente.')
    report = audit(args.zip)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(f"Verificado: {report['elan_files']} ELAN; {report['mechanical_candidates']} candidatos mecánicos; "
          f"{len(report['shortlist'])} preseleccionados sin validar. Vídeos: 0. Modelos: 0.")
