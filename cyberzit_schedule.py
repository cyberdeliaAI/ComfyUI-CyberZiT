"""Pure schedule mathematics for CyberZiT.

This module intentionally has no ComfyUI or PyTorch dependency.  Keeping the
curve generation separate makes it easy to test and keeps the node wrapper
small.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


# ``math.exp2`` was added in Python 3.11. Keep identical behaviour on newer
# Python versions while retaining compatibility with ComfyUI installations
# that still use Python 3.10.
_EXP2 = getattr(math, "exp2", lambda value: 2.0**value)


@dataclass(frozen=True)
class Preset:
    """Parameters for one calibrated CyberZiT trajectory."""

    shift: float
    description: str


PRESETS: dict[str, Preset] = {
    "fast": Preset(
        shift=1.0,
        description="Uniform sigma spacing for the most direct few-step path.",
    ),
    "balanced": Preset(
        shift=1.75,
        description="A mild flow shift that retains structure without a hard final jump.",
    ),
    "quality": Preset(
        shift=3.0,
        description="More sampling points in the high and middle sigma regions.",
    ),
}


def _validate(steps: int, preset: str, detail: float) -> None:
    if isinstance(steps, bool) or not isinstance(steps, int):
        raise TypeError("steps must be an integer")
    if steps < 1:
        raise ValueError("steps must be at least 1")
    if preset not in PRESETS:
        choices = ", ".join(PRESETS)
        raise ValueError(f"unknown preset {preset!r}; choose one of: {choices}")
    if not math.isfinite(detail):
        raise ValueError("detail must be finite")
    if not -1.0 <= detail <= 1.0:
        raise ValueError("detail must be between -1.0 and 1.0")


def build_sigma_values(
    steps: int,
    preset: str = "balanced",
    detail: float = 0.0,
) -> list[float]:
    """Return a descending ``steps + 1`` sigma schedule from 1 to 0.

    The preset selects the amount of rational flow shift.  ``detail`` adds a
    small power curve before that shift:

    * negative values retain more high-sigma structure;
    * positive values allocate more of the trajectory to low-sigma refinement.

    At ``detail=0`` the fast preset is exactly linear.
    """

    _validate(steps, preset, detail)

    shift = PRESETS[preset].shift
    # A deliberately restrained range: detail=-1 -> 0.75, detail=1 -> 1.333.
    # This tunes the preset without turning one simple control into a curve lab.
    exponent = _EXP2(detail * math.log2(4.0 / 3.0))

    values: list[float] = []
    for index in range(steps + 1):
        progress = index / steps
        sigma = (1.0 - progress) ** exponent
        if shift != 1.0:
            sigma = (shift * sigma) / (1.0 + (shift - 1.0) * sigma)
        values.append(float(sigma))

    # Pin the endpoints to avoid tiny floating-point remnants.
    values[0] = 1.0
    values[-1] = 0.0
    return values


__all__ = ["PRESETS", "Preset", "build_sigma_values"]
