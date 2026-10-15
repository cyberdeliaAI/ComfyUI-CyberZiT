import math
import unittest

from cyberzit_schedule import PRESETS, build_sigma_values


class CyberZiTScheduleTests(unittest.TestCase):
    def test_preset_shifts_are_stable(self):
        self.assertEqual(
            {name: preset.shift for name, preset in PRESETS.items()},
            {"fast": 1.0, "balanced": 1.75, "quality": 3.0},
        )

    def test_every_preset_has_correct_shape_endpoints_and_order(self):
        for preset in PRESETS:
            with self.subTest(preset=preset):
                sigmas = build_sigma_values(9, preset)
                self.assertEqual(len(sigmas), 10)
                self.assertEqual(sigmas[0], 1.0)
                self.assertEqual(sigmas[-1], 0.0)
                self.assertTrue(all(math.isfinite(value) for value in sigmas))
                self.assertTrue(
                    all(left > right for left, right in zip(sigmas, sigmas[1:]))
                )

    def test_fast_is_exactly_linear_at_neutral_detail(self):
        self.assertEqual(
            build_sigma_values(4, "fast"),
            [1.0, 0.75, 0.5, 0.25, 0.0],
        )

    def test_presets_retain_progressively_more_high_mid_sigma(self):
        fast = build_sigma_values(8, "fast")
        balanced = build_sigma_values(8, "balanced")
        quality = build_sigma_values(8, "quality")
        for index in range(1, 8):
            self.assertGreater(balanced[index], fast[index])
            self.assertGreater(quality[index], balanced[index])

    def test_positive_detail_allocates_more_low_sigma_refinement(self):
        negative = build_sigma_values(8, "balanced", -1.0)
        neutral = build_sigma_values(8, "balanced", 0.0)
        positive = build_sigma_values(8, "balanced", 1.0)
        for index in range(1, 8):
            self.assertGreater(negative[index], neutral[index])
            self.assertGreater(neutral[index], positive[index])

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            build_sigma_values(0)
        with self.assertRaises(TypeError):
            build_sigma_values(8.0)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            build_sigma_values(8, "unknown")
        with self.assertRaises(ValueError):
            build_sigma_values(8, detail=1.01)


if __name__ == "__main__":
    unittest.main()
