import unittest
from reproducir_2d import validate, svg_frame


def observation():
    return dict(status='complete', sample_fps=5, frames=[
        dict(t_ms=0, points={name:[] for name in ('pose','face','left_hand','right_hand')})])


class ReproductionTests(unittest.TestCase):
    def test_missing_hands_are_absent_not_filled(self):
        svg = svg_frame(validate(observation())[0],720,405)
        self.assertIn('data-channel="left_hand" data-present="false"',svg)
        self.assertNotIn('<circle',svg)

    def test_invalid_coordinate_is_rejected(self):
        data=observation()
        data['frames'][0]['points']['left_hand']=[dict(x=float('nan'),y=0)]*21
        with self.assertRaises(ValueError): validate(data)

    def test_duplicate_timestamp_is_rejected(self):
        data=observation();data['frames']*=2
        with self.assertRaises(ValueError): validate(data)

    def test_hands_use_image_aspect_ratio(self):
        frame=observation()['frames'][0]
        frame['points']['right_hand']=[dict(x=.5,y=.5)]*21
        svg=svg_frame(frame,720,405)
        self.assertIn('cx="360.00" cy="202.50"',svg)

    def test_fluid_profile_preserves_all_real_samples(self):
        data=observation();data['sample_fps']=15
        first=data['frames'][0]
        data['frames']=[dict(t_ms=round(i*1000/15),points=first['points']) for i in range(87)]
        self.assertEqual(len(validate(data)),87)
        data['frames']*=2
        with self.assertRaises(ValueError):validate(data)


if __name__ == '__main__': unittest.main()
