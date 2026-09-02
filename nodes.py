"""ComfyUI nodes and KSampler registration for CyberZiT."""

from __future__ import annotations

import logging
from collections.abc import Callable

import torch

import comfy.samplers

from .cyberzit_schedule import PRESETS, build_sigma_values


LOGGER = logging.getLogger(__name__)
SCHEDULER_CATEGORY = "sampling/custom_sampling/schedulers"


def _as_sigmas(steps: int, preset: str, detail: float = 0.0) -> torch.Tensor:
    values = build_sigma_values(steps=steps, preset=preset, detail=detail)
    return torch.tensor(values, dtype=torch.float32)


def cyberzit_fast_scheduler(_model_sampling: object, steps: int) -> torch.Tensor:
    return _as_sigmas(steps, "fast")


def cyberzit_balanced_scheduler(_model_sampling: object, steps: int) -> torch.Tensor:
    return _as_sigmas(steps, "balanced")


def cyberzit_quality_scheduler(_model_sampling: object, steps: int) -> torch.Tensor:
    return _as_sigmas(steps, "quality")


def _register_ksampler_scheduler(name: str, function: Callable[..., torch.Tensor]) -> bool:
    """Register with the current ComfyUI scheduler API when it is available."""

    handlers = getattr(comfy.samplers, "SCHEDULER_HANDLERS", None)
    handler_type = getattr(comfy.samplers, "SchedulerHandler", None)
    names = getattr(comfy.samplers, "SCHEDULER_NAMES", None)

    if handlers is None or handler_type is None or names is None:
        LOGGER.warning(
            "CyberZiT could not add %s to KSampler: this ComfyUI version does "
            "not expose the scheduler registration API. The SIGMAS node still works.",
            name,
        )
        return False

    handlers[name] = handler_type(function, use_ms=True)
    if name not in names:
        names.append(name)

    # Current ComfyUI points this at SCHEDULER_NAMES.  Keep older compatible
    # builds working too if they copied the list instead of sharing it.
    ksampler = getattr(comfy.samplers, "KSampler", None)
    ksampler_names = getattr(ksampler, "SCHEDULERS", None)
    if isinstance(ksampler_names, list) and name not in ksampler_names:
        ksampler_names.append(name)
    return True


def register_ksampler_schedulers() -> tuple[str, ...]:
    registrations = (
        ("cyberzit_fast", cyberzit_fast_scheduler),
        ("cyberzit", cyberzit_balanced_scheduler),
        ("cyberzit_balanced", cyberzit_balanced_scheduler),
        ("cyberzit_quality", cyberzit_quality_scheduler),
    )
    return tuple(
        name for name, function in registrations if _register_ksampler_scheduler(name, function)
    )


class CyberZiTScheduler:
    """Generate a CyberZiT sigma trajectory for SamplerCustomAdvanced."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "steps": (
                    "INT",
                    {
                        "default": 9,
                        "min": 1,
                        "max": 100,
                        "step": 1,
                        "tooltip": "Number of sampling steps. Try 8-9 for Z-Image Turbo or 8-12 for Anima-Turbo.",
                    },
                ),
                "preset": (
                    list(PRESETS),
                    {
                        "default": "balanced",
                        "tooltip": "Fast is linear; Balanced adds a mild shift; Quality retains more high/mid sigma steps.",
                    },
                ),
                "detail": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": -1.0,
                        "max": 1.0,
                        "step": 0.05,
                        "round": 0.01,
                        "tooltip": "Negative favors high-sigma structure; positive favors low-sigma refinement.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("SIGMAS",)
    RETURN_NAMES = ("sigmas",)
    FUNCTION = "generate"
    CATEGORY = SCHEDULER_CATEGORY
    DESCRIPTION = (
        "CyberZiT sigma schedules for Z-Image Turbo and Anima-Turbo: fast, "
        "balanced, and quality, with one restrained detail control."
    )

    def generate(self, steps: int, preset: str, detail: float):
        return (_as_sigmas(steps, preset, detail),)


REGISTERED_KSAMPLER_SCHEDULERS = register_ksampler_schedulers()

NODE_CLASS_MAPPINGS = {
    "CyberZiTScheduler": CyberZiTScheduler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CyberZiTScheduler": "CyberZiT Scheduler",
}


__all__ = [
    "CyberZiTScheduler",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "REGISTERED_KSAMPLER_SCHEDULERS",
]
