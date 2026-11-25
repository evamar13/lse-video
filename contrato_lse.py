#!/usr/bin/env python3
"""Contrato 0.1 de observaciones LSE: conserva evidencia y huecos; no genera traducciones."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
from auditar_anotaciones import EXPECTED_MD5

VERSION = '0.1'
MISSING = ['finger_joint_rotations', 'hand_orientation', 'arm_trajectories',
           'contacts', 'gaze', 'eyebrows', 'mouth_components', 'body_motion']

def text_of(annotation):
    value = annotation.find('ANNOTATION_VALUE')
    return ''.join(value.itertext()).strip() if value is not None else ''

def parse_elan(root):
    times = {slot.get('TIME_SLOT_ID'):int(slot.get('TIME_VALUE'))
             for slot in root.findall('./TIME_ORDER/TIME_SLOT') if slot.get('TIME_VALUE') is not None}
    aligned, references = {}, []
    for tier in root.findall('TIER'):
        for wrapper in tier.findall('ANNOTATION'):
            for row in wrapper:
                identity = row.get('ANNOTATION_ID')
                if not identity or identity in aligned or any(r['id']==identity for r in references):
                    raise ValueError('Identificador ausente o duplicado en ELAN.')
                if row.tag == 'ALIGNABLE_ANNOTATION':
                    start,end = times.get(row.get('TIME_SLOT_REF1')),times.get(row.get('TIME_SLOT_REF2'))
                    if start is None or end is None or not 0 <= start < end:
                        raise ValueError('Intervalo ELAN inválido.')
                    aligned[identity] = {'id':identity,'tier':tier.get('TIER_ID'),
                                         'start_ms':start,'end_ms':end,'value':text_of(row)}
                elif row.tag == 'REF_ANNOTATION':
                    references.append({'id':identity,'tier':tier.get('TIER_ID'),
                                       'parent_id':row.get('ANNOTATION_REF'),'value':text_of(row)})
    for row in references:
        if row['parent_id'] not in aligned:
            raise ValueError('Referencia ELAN no resoluble por este adaptador; no se descarta silenciosamente.')
    return aligned,references

def packet_from_elan(root, selection, evidence):
    aligned, references = parse_elan(root)
    anchor = aligned.get(selection['annotation_id'])
    if not anchor or anchor['tier'].lower() != 'trad':
        raise ValueError('La selección no identifica una traducción alineada.')
    if (anchor['start_ms'],anchor['end_ms']) != (selection['start_ms'],selection['end_ms']):
        raise ValueError('La selección no coincide con los tiempos de la fuente.')
    if 'translation' in selection and selection['translation'] != anchor['value']:
        raise ValueError('La selección no coincide con el texto de la fuente.')
    start,end = anchor['start_ms'],anchor['end_ms']
    signs=[]
    for item in aligned.values():
        if item['tier'].lower() != 'm_glosa' or item['end_ms'] <= start or item['start_ms'] >= end:
            continue
        signs.append({'annotation_id':item['id'],'label':item['value'],
                      'start_ms':max(start,item['start_ms'])-start,
                      'end_ms':min(end,item['end_ms'])-start,
                      'source_start_ms':item['start_ms'],'source_end_ms':item['end_ms'],
                      'clipped':item['start_ms']<start or item['end_ms']>end})
    signs.sort(key=lambda row:(row['start_ms'],row['end_ms'],row['annotation_id']))
    ids={row['annotation_id'] for row in signs}
    packet={'schema_version':VERSION,'kind':'observed_lse_segment',
            'evidence':dict(evidence,annotation_id=anchor['id'],start_ms=start,end_ms=end),
            'input':{'language':'es-ES','text':anchor['value'],
                     'role':'corpus_translation_of_lse_not_asr','audio':None},
            'linguistic':{'status':'unreviewed','gloss_annotations':signs,
                          'variants':[row for row in references if row['parent_id'] in ids],
                          'coverage':'selected_gloss_inventory_not_complete_sentence_annotation',
                          'spatial_references':None,'nonmanuals':None},
            'motion':{'status':'unavailable','coordinate_system':None,'frames':None,
                      'missing_channels':list(MISSING)},
            'review':{'technical':'metadata_only','linguistic':'pending',
                      'ready_for_translation':False,'ready_for_rendering':False}}
    validate(packet)
    return packet

def validate(packet):
    if packet.get('schema_version') != VERSION or packet.get('kind') != 'observed_lse_segment':
        raise ValueError('Versión o tipo de contrato no soportados.')
    evidence=packet['evidence']
    start,end=evidence['start_ms'],evidence['end_ms']
    if type(start) is not int or type(end) is not int or not 0 <= start < end:
        raise ValueError('Tiempos de evidencia inválidos.')
    if not evidence.get('source_url') or not evidence.get('license'):
        raise ValueError('Falta procedencia o licencia.')
    linguistic,motion,review=packet['linguistic'],packet['motion'],packet['review']
    if (linguistic['status']!='unreviewed' or review['linguistic']!='pending'
            or review['technical']!='metadata_only'
            or review['ready_for_translation'] is not False or review['ready_for_rendering'] is not False):
        raise ValueError('Este contrato de observaciones no certifica traducción, movimiento o revisión.')
    if (motion['status']!='unavailable' or motion['frames'] is not None
            or motion['coordinate_system'] is not None or set(motion['missing_channels'])!=set(MISSING)):
        raise ValueError('No se pueden declarar movimientos que no contiene esta evidencia.')
    if linguistic['spatial_references'] is not None or linguistic['nonmanuals'] is not None:
        raise ValueError('La extracción actual no aporta espacio ni canales no manuales.')
    if packet['input']['role']!='corpus_translation_of_lse_not_asr' or packet['input']['audio'] is not None:
        raise ValueError('No confundir traducción escrita con voz reconocida.')
    ids=set()
    previous=-1
    for row in linguistic['gloss_annotations']:
        a,b=row['start_ms'],row['end_ms']
        sa,sb=row['source_start_ms'],row['source_end_ms']
        if (any(type(x) is not int for x in [a,b,sa,sb]) or not 0 <= a < b <= end-start
                or not 0 <= sa < sb or a<previous or row['annotation_id'] in ids):
            raise ValueError('Tiempos, orden o identificadores de glosas inválidos.')
        if a!=max(start,sa)-start or b!=min(end,sb)-start or row['clipped']!=(sa<start or sb>end):
            raise ValueError('Recorte incoherente con la fuente original.')
        previous=a
        ids.add(row['annotation_id'])
    if any(row['parent_id'] not in ids for row in linguistic['variants']):
        raise ValueError('Variante sin glosa de referencia.')
    return True

def export(base):
    archive_path=base/'datos/anotaciones.zip'
    raw=archive_path.read_bytes()
    if hashlib.md5(raw).hexdigest()!=EXPECTED_MD5:
        raise ValueError('El ZIP de anotaciones no coincide con la versión auditada.')
    shortlist=json.loads((base/'datos/auditoria.json').read_text())['shortlist']
    output=base/'datos/contratos';output.mkdir(parents=True,exist_ok=True)
    summary=[]
    with zipfile.ZipFile(archive_path) as archive:
        for row in shortlist:
            info=archive.getinfo(row['elan_file'])
            if info.file_size>5_000_000:
                raise ValueError('ELAN demasiado grande.')
            root=ET.fromstring(archive.read(info))
            evidence={'dataset':'LSE-Health-UVigo','source_url':'https://zenodo.org/records/10234465',
                      'license':'CC BY-NC 4.0','elan_file':row['elan_file'],
                      'annotations_zip_sha256':hashlib.sha256(raw).hexdigest()}
            packet=packet_from_elan(root,row,evidence)
            name=Path(row['elan_file']).stem+'-'+row['annotation_id']+'.json'
            (output/name).write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
            signs=packet['linguistic']['gloss_annotations']
            summary.append({'file':name,'annotated_glosses':len(signs),
                            'clipped_glosses':sum(r['clipped'] for r in signs),
                            'variants':len(packet['linguistic']['variants']),
                            'motion_available':False,'linguistic_review':'pending'})
    (output/'inventario.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'observations':len(summary),'glosses_in_sample':sum(r['annotated_glosses'] for r in summary),
                      'motion_available':False,'linguistic_review':'pending'},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',type=Path,default=Path(__file__).parent)
    export(parser.parse_args().base)
