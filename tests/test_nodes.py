import importlib.util
import sys
import types
import unittest
from collections import namedtuple
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "_cyberzit_node_test"


def load_nodes_with_comfy_stubs():
    package = types.ModuleType(PACKAGE_NAME)
    package.__path__ = [str(ROOT)]
    sys.modules[PACKAGE_NAME] = package

    fake_torch = types.ModuleType("torch")
    fake_torch.float32 = "float32"
    fake_torch.Tensor = tuple
    fake_torch.tensor = lambda values, dtype=None: tuple(values)

    fake_comfy = types.ModuleType("comfy")
    fake_samplers = types.ModuleType("comfy.samplers")
    fake_samplers.SchedulerHandler = namedtuple("SchedulerHandler", "handler use_ms")
    fake_samplers.SCHEDULER_HANDLERS = {}
    fake_samplers.SCHEDULER_NAMES = []

    class FakeKSampler:
        SCHEDULERS = []

    fake_samplers.KSampler = FakeKSampler
    fake_comfy.samplers = fake_samplers

    sys.modules["torch"] = fake_torch
    sys.modules["comfy"] = fake_comfy
    sys.modules["comfy.samplers"] = fake_samplers

    module_name = f"{PACKAGE_NAME}.nodes"
    spec = importlib.util.spec_from_file_location(module_name, ROOT / "nodes.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module, fake_samplers


class CyberZiTNodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nodes, cls.samplers = load_nodes_with_comfy_stubs()

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
        alias = self.samplers.SCHEDULER_HANDLERS["cyberzit"].handler(None, 4)
        named = self.samplers.SCHEDULER_HANDLERS["cyberzit_balanced"].handler(None, 4)
        self.assertEqual(alias, named)

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
