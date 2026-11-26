import copy
import unittest
from crear_modular import payload


def observation():
    point=dict(x=.5,y=.25,z=0)
    return dict(status='complete',sample_fps=15,frames=[dict(t_ms=0,points=dict(
        pose=[dict(point) for _ in range(33)],face=[dict(point) for _ in range(478)],
        left_hand=[],right_hand=[dict(point) for _ in range(21)]))])


class ModularPayloadTests(unittest.TestCase):
    def test_absent_hand_preserved_and_input_not_modified(self):
        data=observation();before=copy.deepcopy(data);out=payload(data)
        self.assertEqual(out['frames'][0]['left_hand'],[])
        self.assertEqual(len(out['frames'][0]['right_hand']),21)
        self.assertEqual(data,before)

    def test_normalized_coordinates_use_source_aspect(self):
        out=payload(observation())
        self.assertEqual(out['frames'][0]['right_hand'][0],[480,135])

    def test_body_absence_blocks_unsupported_template(self):
        data=observation();data['frames'][0]['points']['pose']=[]
        with self.assertRaises(ValueError):payload(data)


if __name__=='__main__':unittest.main()
