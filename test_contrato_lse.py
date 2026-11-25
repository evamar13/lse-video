"""Fixtures sintéticos de estructura temporal; no contienen traducciones ni signos LSE reales."""
import copy
import unittest
import xml.etree.ElementTree as ET
from contrato_lse import packet_from_elan,validate

XML='''<ANNOTATION_DOCUMENT><TIME_ORDER>
<TIME_SLOT TIME_SLOT_ID="t0" TIME_VALUE="800"/><TIME_SLOT TIME_SLOT_ID="t1" TIME_VALUE="1000"/>
<TIME_SLOT TIME_SLOT_ID="t2" TIME_VALUE="1200"/><TIME_SLOT TIME_SLOT_ID="t3" TIME_VALUE="2000"/>
<TIME_SLOT TIME_SLOT_ID="t4" TIME_VALUE="2800"/><TIME_SLOT TIME_SLOT_ID="t5" TIME_VALUE="3000"/>
<TIME_SLOT TIME_SLOT_ID="t6" TIME_VALUE="4000"/></TIME_ORDER>
<TIER TIER_ID="Trad"><ANNOTATION><ALIGNABLE_ANNOTATION ANNOTATION_ID="translation" TIME_SLOT_REF1="t1" TIME_SLOT_REF2="t5">
<ANNOTATION_VALUE>Texto sintético, no es una traducción de LSE.</ANNOTATION_VALUE></ALIGNABLE_ANNOTATION></ANNOTATION></TIER>
<TIER TIER_ID="M_Glosa">
<ANNOTATION><ALIGNABLE_ANNOTATION ANNOTATION_ID="partial" TIME_SLOT_REF1="t0" TIME_SLOT_REF2="t2"><ANNOTATION_VALUE>TEST_ONLY_A</ANNOTATION_VALUE></ALIGNABLE_ANNOTATION></ANNOTATION>
<ANNOTATION><ALIGNABLE_ANNOTATION ANNOTATION_ID="complete" TIME_SLOT_REF1="t3" TIME_SLOT_REF2="t4"><ANNOTATION_VALUE>TEST_ONLY_B</ANNOTATION_VALUE></ALIGNABLE_ANNOTATION></ANNOTATION>
<ANNOTATION><ALIGNABLE_ANNOTATION ANNOTATION_ID="outside" TIME_SLOT_REF1="t5" TIME_SLOT_REF2="t6"><ANNOTATION_VALUE>TEST_ONLY_C</ANNOTATION_VALUE></ALIGNABLE_ANNOTATION></ANNOTATION>
</TIER><TIER TIER_ID="VAR"><ANNOTATION><REF_ANNOTATION ANNOTATION_ID="variant" ANNOTATION_REF="partial"><ANNOTATION_VALUE>TEST_ONLY_VARIANT</ANNOTATION_VALUE></REF_ANNOTATION></ANNOTATION></TIER></ANNOTATION_DOCUMENT>'''

class ContractTests(unittest.TestCase):
    def packet(self):
        return packet_from_elan(ET.fromstring(XML),
             {'annotation_id':'translation','start_ms':1000,'end_ms':3000},
             {'source_url':'https://example.org/synthetic','license':'synthetic-test-fixture'})

    def test_clipping_and_parent_references(self):
        packet=self.packet();signs=packet['linguistic']['gloss_annotations']
        self.assertEqual([s['annotation_id'] for s in signs],['partial','complete'])
        self.assertEqual((signs[0]['start_ms'],signs[0]['end_ms'],signs[0]['clipped']),(0,200,True))
        self.assertEqual((signs[1]['start_ms'],signs[1]['end_ms'],signs[1]['clipped']),(1000,1800,False))
        self.assertEqual(packet['linguistic']['variants'][0]['parent_id'],'partial')
        self.assertIsNone(packet['motion']['frames'])

    def test_changed_source_interval_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'tiempos'):
            packet_from_elan(ET.fromstring(XML),
                {'annotation_id':'translation','start_ms':0,'end_ms':3000},
                {'source_url':'https://example.org','license':'test'})

    def test_fake_render_readiness_is_rejected(self):
        packet=self.packet();packet['review']['ready_for_rendering']=True
        with self.assertRaisesRegex(ValueError,'no certifica'):validate(packet)

    def test_invented_motion_is_rejected(self):
        packet=self.packet();packet['motion']['frames']=[{'x':1}]
        with self.assertRaisesRegex(ValueError,'movimientos'):validate(packet)

    def test_sign_extending_outside_segment_is_rejected(self):
        packet=self.packet();packet['linguistic']['gloss_annotations'][0]['end_ms']=2001
        with self.assertRaises(ValueError):validate(packet)

    def test_broken_variant_link_is_rejected(self):
        packet=self.packet();packet['linguistic']['variants'][0]['parent_id']='not-present'
        with self.assertRaisesRegex(ValueError,'Variante'):validate(packet)

    def test_empty_gloss_coverage_does_not_invent_signs(self):
        root=ET.fromstring(XML)
        root.remove(next(t for t in root.findall('TIER') if t.get('TIER_ID')=='M_Glosa'))
        root.remove(next(t for t in root.findall('TIER') if t.get('TIER_ID')=='VAR'))
        packet=packet_from_elan(root,{'annotation_id':'translation','start_ms':1000,'end_ms':3000},
                                {'source_url':'https://example.org','license':'test'})
        self.assertEqual(packet['linguistic']['gloss_annotations'],[])
        self.assertFalse(packet['review']['ready_for_translation'])

if __name__=='__main__':unittest.main()
