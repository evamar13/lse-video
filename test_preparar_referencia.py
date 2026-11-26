import base64
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import preparar_referencia as ref


class PhotoWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.photo=self.root/'test.png'
        self.photo.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a1ZkAAAAASUVORK5CYII='))
        self.original=self.photo.read_bytes()
        self.patch=patch.object(ref,'ROOT',self.root/'casos');self.patch.start();self.addCleanup(self.patch.stop)
        # Fijar metadatos en pruebas portátiles; no se llama a modelos.
        self.meta=patch.object(ref.subprocess,'run',return_value=type('Result',(),dict(returncode=0,stdout='pixelWidth: 1\npixelHeight: 1'))())
        self.meta.start();self.addCleanup(self.meta.stop)

    def case_with_candidate(self):
        case=ref.new_case(self.photo)
        candidate=ref.attach(case,self.photo,'ia',['Manos reconstruidas'])
        return case,candidate

    def test_no_reference_before_explicit_review(self):
        case,candidate=self.case_with_candidate()
        with self.assertRaises(ValueError):ref.resolver_referencia(case)
        ref.review(case,candidate,'aceptar')
        self.assertEqual(ref.resolver_referencia(case).read_bytes(),self.original)
        self.assertEqual(self.photo.read_bytes(),self.original)

    def test_modified_reference_invalidates_resolution(self):
        case,candidate=self.case_with_candidate();ref.review(case,candidate,'aceptar')
        ref.resolver_referencia(case).write_bytes(b'changed')
        with self.assertRaises(ValueError):ref.resolver_referencia(case)

    def test_rejecting_selected_candidate_revokes_reference(self):
        case,candidate=self.case_with_candidate();ref.review(case,candidate,'aceptar')
        ref.review(case,candidate,'rechazar')
        with self.assertRaises(ValueError):ref.resolver_referencia(case)

    def test_new_candidate_keeps_accepted_reference(self):
        case,candidate=self.case_with_candidate();ref.review(case,candidate,'aceptar')
        accepted=ref.resolver_referencia(case)
        ref.attach(case,self.photo,'ia',['Corrección de encuadre'])
        self.assertEqual(ref.resolver_referencia(case),accepted)
        with self.assertRaises(ValueError):ref.attach(case,self.photo,'ia',['Tercer intento'])

    def test_case_paths_and_unrecorded_reconstruction_rejected(self):
        with self.assertRaises(ValueError):ref.case_path('../outside')
        case=ref.new_case(self.photo)
        with self.assertRaises(ValueError):ref.attach(case,self.photo,'ia',[])


if __name__=='__main__':unittest.main()
