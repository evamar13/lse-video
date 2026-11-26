import io
import unittest
import zipfile
from fuentes_privadas import central_start, single_image,validate_dilse


class Remote(io.BytesIO):
    def __init__(self,data):super().__init__(data);self.size=len(data)


def archive(method=zipfile.ZIP_DEFLATED):
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',compression=method) as z:
        z.writestr('Original/A/muestra.png',b'synthetic-test-image')
    return buffer.getvalue()


class PrivateSourceTests(unittest.TestCase):
    def test_reads_one_compressed_member(self):
        name,content,crc=single_image(Remote(archive()))
        self.assertEqual(name,'Original/A/muestra.png')
        self.assertEqual(content,b'synthetic-test-image')

    def test_rejects_changed_content(self):
        data=archive(zipfile.ZIP_STORED).replace(b'synthetic-test-image',b'changed---test-image')
        with self.assertRaises(ValueError):single_image(Remote(data))

    def test_rejects_oversized_image(self):
        buffer=io.BytesIO()
        with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('large.png',b'x'*1_000_001)
        with self.assertRaises(ValueError):single_image(Remote(buffer.getvalue()))

    def test_rejects_non_zip(self):
        with self.assertRaises(ValueError):central_start(Remote(b'not a zip'))

    def test_dilse_rejects_media_outside_reviewed_scope(self):
        data=[dict(id=1697,entrada='hola',foto='https://unreviewed.example/image',video='https://panel.fundacioncnse-dilse.org/storage/hola.mov')]
        with self.assertRaises(ValueError):validate_dilse(data,dict(creditos=[]))

    def test_dilse_requires_express_legal_evidence(self):
        data=[dict(id=1697,entrada='hola',foto='https://panel.fundacioncnse-dilse.org/storage/hola.png',video='https://panel.fundacioncnse-dilse.org/storage/hola.mov')]
        with self.assertRaises(ValueError):validate_dilse(data,dict(creditos=[dict(titulo='Propiedad intelectual',contenido='Aviso sin autorización de uso')]))


if __name__=='__main__':unittest.main()
