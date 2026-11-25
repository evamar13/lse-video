"""Pruebas sin red del acceso parcial a ZIP y sus límites."""
import io
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile
from muestra_videos import RangeFile

class RangeTests(unittest.TestCase):
    @staticmethod
    def responder(payload, ignore_range=False):
        def respond(command, **kwargs):
            first,last = map(int, command[command.index('--range')+1].split('-'))
            header = Path(command[command.index('--dump-header')+1])
            output = Path(command[command.index('--output')+1])
            header.write_text('HTTP/1.1 200 OK\n' if ignore_range else
                              f'HTTP/1.1 206 Partial Content\nContent-Range: bytes {first}-{last}/{len(payload)}\n')
            output.write_bytes(payload[first:last+1])
            return SimpleNamespace(returncode=0)
        return respond

    def test_zip_across_multiple_ranges_and_eof(self):
        content = b'LSE sample\x00' * 500_000
        stream = io.BytesIO()
        with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_STORED) as archive:
            archive.writestr('sample.mp4', content)
        payload = stream.getvalue()
        with patch('muestra_videos.subprocess.run',side_effect=self.responder(payload)):
            remote = RangeFile(16*1024*1024)
            with zipfile.ZipFile(remote) as archive:
                self.assertEqual(archive.read('sample.mp4'), content)
            remote.seek(len(payload))
            self.assertEqual(remote.read(100),b'')
            self.assertLessEqual(remote.received,remote.budget)

    def test_server_without_content_range_is_rejected(self):
        with patch('muestra_videos.subprocess.run',side_effect=self.responder(b'abc',True)):
            with self.assertRaisesRegex(ValueError,'no ofrece el rango'):
                RangeFile(1024)

    def test_budget_stops_reads_before_network_call(self):
        with patch('muestra_videos.subprocess.run',side_effect=self.responder(b'a'*4096)) as run:
            remote = RangeFile(32)
            with self.assertRaisesRegex(ValueError,'Límite de descarga'):
                remote.read(100)
            self.assertEqual(run.call_count,1)

if __name__ == '__main__':
    unittest.main()
