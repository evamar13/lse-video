import copy
import unittest
from types import SimpleNamespace
from refinar_manos import crop_box, restore, assign
from reproducir_2d import hand_detail, svg_frame


def hand(x=.5,y=.5):
    return [dict(x=x+i*.002,y=y+i*.002) for i in range(21)]


class HandDetailTests(unittest.TestCase):
    def test_crop_to_source_transform(self):
        point=SimpleNamespace(x=.5,y=.25,z=-.1)
        result=restore([point],(100,50,300,250),1000,500)[0]
        self.assertEqual(result['x'],.2)
        self.assertEqual(result['y'],.2)
        self.assertEqual(result['z_crop'],-.1)

    def test_unknown_hand_not_assigned(self):
        result,_=assign(dict(left_hand=[],right_hand=hand()),[hand(),hand(.1)],1000,500)
        self.assertNotIn('left_hand',result)

    def test_ambiguous_assignment_rejected(self):
        result,status=assign(dict(left_hand=hand(),right_hand=hand()),[hand(),hand()],1000,500)
        self.assertEqual(result,{})
        self.assertEqual(status,'asociacion_ambigua')

    def test_crop_stays_inside_image(self):
        box=crop_box(dict(left_hand=hand(0,0),right_hand=[]),1000,500)
        self.assertTrue(0<=box[0]<box[2]<=1000)
        self.assertTrue(0<=box[1]<box[3]<=500)

    def test_renderer_keeps_original_points(self):
        frame=dict(points=dict(pose=[dict(x=.4,y=.3)]*33,face=[],left_hand=hand(),right_hand=[]))
        before=copy.deepcopy(frame)
        svg_frame(frame,720,405)
        self.assertEqual(frame,before)

    def test_detail_names_every_finger(self):
        svg=hand_detail(hand(),720,405)
        for name in ['Pulgar','Índice','Medio','Anular','Meñique']:self.assertIn(name,svg)
        self.assertEqual(svg.count('<circle'),21)


if __name__=='__main__':unittest.main()
