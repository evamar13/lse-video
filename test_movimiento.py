"""Comprobaciones de datos y límites; nunca cargan MediaPipe ni ejecutan inferencias."""
import contextlib
import io
import math
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from extraer_movimiento import serialize,main

class MotionTests(unittest.TestCase):
    def test_unknown_confidence_is_not_zero(self):
        row=serialize([SimpleNamespace(x=0.2,y=0.4,z=-0.1)])[0]
        self.assertIsNone(row['visibility'])
        self.assertIsNone(row['presence'])
        self.assertEqual(row['z'],-0.1)

    def test_nan_coordinates_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'no finitas'):
            serialize([SimpleNamespace(x=math.nan,y=0,z=0)])

    def test_time_and_sampling_limits_fail_before_loading_models(self):
        for option,value in [('--seconds','7'),('--fps','6')]:
            with patch('sys.argv',['extraer_movimiento.py','--task','synthetic',option,value]):
                with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as error:
                    main()
                self.assertEqual(error.exception.code,2)

if __name__=='__main__':unittest.main()
