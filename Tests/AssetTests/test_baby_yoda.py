"""Identity, timing and reproducibility checks for the new pixel-art model."""
import hashlib
import importlib.util
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("baby_yoda", ROOT / "scripts/generate_baby_yoda.py")
ART = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ART)


class BabyYodaArtTests(unittest.TestCase):
    def test_model_parts_are_never_mutated_by_poses(self):
        def digest():
            head, sleeping_head, body, arms, feet, hood = ART.MODEL
            return [hashlib.sha256(part.tobytes()).hexdigest()
                    for part in [head, sleeping_head, body, *arms, *feet, hood]]
        before = digest()
        ART.animations()
        self.assertEqual(before, digest())

    def test_head_and_gray_torso_stay_identical_across_awake_actions(self):
        sequences = ART.animations()
        base = sequences["idle"][0]
        for name in ["idle", "walk", "interaction", "special", "training"]:
            for index, frame in enumerate(sequences[name]):
                # Sleeves, feet and weapon are outside this unchanged tunic region.
                self.assertEqual(base.crop((24, 48, 40, 56)).tobytes(),
                                 frame.crop((24, 48, 40, 56)).tobytes(), (name, index))
                # During training the blade may occlude the face. Before drawing
                # the weapon, the same face pixels must remain byte-for-byte.
                if name != "training" and (name != "special" or index < 8):
                    self.assertEqual(base.crop((22, 20, 44, 36)).tobytes(),
                                     frame.crop((22, 20, 44, 36)).tobytes(), (name, index))

    def test_saved_frames_match_generator_and_keep_crisp_pixels(self):
        for name, frames in ART.animations().items():
            for index, expected in enumerate(frames):
                path = ART.OUTPUT / name / f"frame_{index:02d}.png"
                with Image.open(path) as image:
                    self.assertEqual(image.mode, "RGBA")
                    self.assertEqual(image.size, (64, 64))
                    self.assertEqual(image.tobytes(), expected.tobytes())
                    self.assertEqual(set(image.getchannel("A").tobytes()), {0, 255})
                    self.assertEqual(image.getchannel("A").crop((0, 62, 64, 64)).getbbox(), None)
                    for y in range(0, 64, 2):
                        for x in range(0, 64, 2):
                            pixel = image.getpixel((x, y))
                            for dx, dy in [(1, 0), (0, 1), (1, 1)]:
                                self.assertEqual(pixel, image.getpixel((x + dx, y + dy)))

    def test_training_is_included_at_the_end_of_the_signature(self):
        sequences = ART.animations()
        self.assertEqual(len(sequences["special"]), 20)
        self.assertEqual([im.tobytes() for im in sequences["special"][12:]],
                         [im.tobytes() for im in sequences["training"]])


if __name__ == "__main__":
    unittest.main()
