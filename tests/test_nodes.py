import importlib.util
import sys
import types
import unittest
from collections import namedtuple
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "_cyberzit_node_test"


def load_nodes_with_comfy_stubs():
    package = types.ModuleType(PACKAGE_NAME)
    package.__path__ = [str(ROOT)]

    fake_torch = types.ModuleType("torch")
    fake_torch.float32 = "float32"
    fake_torch.Tensor = tuple
    fake_torch.tensor = lambda values, dtype=None: tuple(values)

    fake_comfy = types.ModuleType("comfy")
    fake_model_sampling = types.ModuleType("comfy.model_sampling")

    class ModelSamplingDiscreteFlow:
        def __init__(self, shift=3.0):
            self.shift = shift
            self.sigma_max = 1.0

    fake_model_sampling.ModelSamplingDiscreteFlow = ModelSamplingDiscreteFlow
    fake_comfy.model_sampling = fake_model_sampling
    fake_samplers = types.ModuleType("comfy.samplers")
    fake_samplers.SchedulerHandler = namedtuple("SchedulerHandler", "handler use_ms")
    fake_samplers.SCHEDULER_HANDLERS = {}
    fake_samplers.SCHEDULER_NAMES = []

    class FakeKSampler:
        SCHEDULERS = []

    fake_samplers.KSampler = FakeKSampler
    fake_comfy.samplers = fake_samplers

    module_name = f"{PACKAGE_NAME}.nodes"
    spec = importlib.util.spec_from_file_location(module_name, ROOT / "nodes.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    with patch.dict(sys.modules, {
        PACKAGE_NAME: package,
        "torch": fake_torch,
        "comfy": fake_comfy,
        "comfy.model_sampling": fake_model_sampling,
        "comfy.samplers": fake_samplers,
        module_name: module,
    }):
        spec.loader.exec_module(module)
    return module, fake_samplers


class CyberZiTNodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nodes, cls.samplers = load_nodes_with_comfy_stubs()
        cls.flow_type = cls.nodes.comfy.model_sampling.ModelSamplingDiscreteFlow

    def test_registers_all_dropdown_names(self):
        expected = {
            "cyberzit_fast",
            "cyberzit",
            "cyberzit_balanced",
            "cyberzit_quality",
        }
        self.assertEqual(set(self.samplers.SCHEDULER_HANDLERS), expected)
        self.assertEqual(set(self.samplers.SCHEDULER_NAMES), expected)
        self.assertEqual(set(self.samplers.KSampler.SCHEDULERS), expected)

    def test_balanced_alias_uses_balanced_schedule(self):
        model_sampling = self.flow_type()
        alias = self.samplers.SCHEDULER_HANDLERS["cyberzit"].handler(model_sampling, 4)
        named = self.samplers.SCHEDULER_HANDLERS["cyberzit_balanced"].handler(model_sampling, 4)
        self.assertEqual(alias, named)

    def test_supported_flow_models_keep_existing_preset_values(self):
        expected = {
            "cyberzit_fast": (1.0, 0.75, 0.5, 0.25, 0.0),
            "cyberzit": (1.0, 0.84, 7 / 11, 7 / 19, 0.0),
            "cyberzit_balanced": (1.0, 0.84, 7 / 11, 7 / 19, 0.0),
            "cyberzit_quality": (1.0, 0.9, 0.75, 0.5, 0.0),
        }

        # ComfyUI combines the flow base with a prediction type in a subclass.
        class ModelSamplingAdvanced(self.flow_type):
            pass

        for model_type in (self.flow_type, ModelSamplingAdvanced):
            for shift in (1.0, 3.0, 5.0):
                for name, sigmas in expected.items():
                    with self.subTest(model_type=model_type.__name__, shift=shift, name=name):
                        model_sampling = model_type(shift=shift)
                        handler = self.samplers.SCHEDULER_HANDLERS[name]
                        self.assertTrue(handler.use_ms)
                        self.assertEqual(handler.handler(model_sampling, 4), sigmas)
                        self.assertEqual(model_sampling.shift, shift)

    def test_ksampler_handlers_reject_unsupported_models_before_building_sigmas(self):
        unsupported = (
            types.SimpleNamespace(sigma_max=14.6),
            types.SimpleNamespace(sigma_max=1.0, shift=3.0),
            object(),
            None,
        )
        with patch.object(self.nodes, "_as_sigmas") as build_sigmas:
            for name, handler in self.samplers.SCHEDULER_HANDLERS.items():
                for model_sampling in unsupported:
                    with self.subTest(name=name, model_sampling=model_sampling):
                        with self.assertRaisesRegex(ValueError, "require ModelSamplingDiscreteFlow"):
                            handler.handler(model_sampling, 4)
            build_sigmas.assert_not_called()

    def test_standalone_node_returns_sigmas_tuple(self):
        result = self.nodes.CyberZiTScheduler().generate(4, "fast", 0.0)
        self.assertEqual(result, ((1.0, 0.75, 0.5, 0.25, 0.0),))

    def test_node_mappings_are_exposed(self):
        self.assertIs(
            self.nodes.NODE_CLASS_MAPPINGS["CyberZiTScheduler"],
            self.nodes.CyberZiTScheduler,
        )
        self.assertEqual(
            self.nodes.NODE_DISPLAY_NAME_MAPPINGS["CyberZiTScheduler"],
            "CyberZiT Scheduler",
        )


if __name__ == "__main__":
    unittest.main()
