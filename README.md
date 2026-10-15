# ComfyUI-CyberZiT

<p align="center">
  <img src="assets/icon.png" alt="CyberZiT Scheduler icon" width="200">
</p>

[![Tests](https://github.com/cyberdeliaAI/ComfyUI-CyberZiT/actions/workflows/tests.yml/badge.svg)](https://github.com/cyberdeliaAI/ComfyUI-CyberZiT/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

CyberZiT is a lightweight preset sigma scheduler for ComfyUI. It was designed
for [Z-Image Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo) and is also
tested with [Anima-Turbo](https://huggingface.co/circlestone-labs/Anima).

It adds:

- a **CyberZiT Scheduler** node with `fast`, `balanced`, and `quality` presets;
- four CyberZiT entries in the normal KSampler scheduler menu;
- an optional `detail` control when using the standalone scheduler node.

CyberZiT has no additional Python dependencies and does not download models or
make network requests.

## Installation

### ComfyUI Manager

Open ComfyUI Manager, search for **CyberZiT Scheduler**, install it, and restart
ComfyUI.

### Git

Open a terminal in `ComfyUI/custom_nodes` and run:

```bash
git clone https://github.com/cyberdeliaAI/ComfyUI-CyberZiT.git
```

Restart ComfyUI after installation.

### Manual installation

Download this repository as a ZIP, extract it, and place the resulting folder
at:

```text
ComfyUI/custom_nodes/ComfyUI-CyberZiT
```

Restart ComfyUI. No `requirements.txt` installation is needed.

## Model compatibility

CyberZiT generates flow schedules from `1.0` to `0.0`. Its intended models are
Z-Image Turbo and Anima-Turbo. The KSampler entries require ComfyUI's
`ModelSamplingDiscreteFlow` sampling class or a subclass. They stop with a
clear error for other sampling types, including standard EPS-based SDXL,
Pony, and Illustrious workflows, instead of returning an unsuitable schedule.
A maximum sigma near `1.0` alone is not sufficient to pass this check.
Other models using the accepted sampling class have not necessarily been
tested with these presets.

The standalone **CyberZiT Scheduler** node has no model input and cannot
perform this check. When connecting its `SIGMAS` output, use a compatible
flow model; it does not make an EPS model compatible.

Preset shifts are fixed at `1.0`, `1.75`, and `3.0`. They do not inherit or
combine with the model's shift. For example, setting shift `5.0` in
`ModelSamplingAuraFlow` and selecting `cyberzit_balanced` still generates a
schedule with shift `1.75`. CyberZiT does not modify the model's sampling
object or its other settings.

## Quick start

### Normal KSampler nodes

Select one of these entries in the existing `scheduler` menu:

- `cyberzit_fast`
- `cyberzit`
- `cyberzit_balanced`
- `cyberzit_quality`

`cyberzit` is an alias of `cyberzit_balanced`. All four menu entries use the
neutral `detail=0.0` setting.

Useful starting points:

| Model | Steps | CFG | Sampler | Scheduler |
| --- | ---: | ---: | --- | --- |
| Z-Image Turbo | 8-9 | `1.0` | `euler` | `cyberzit_quality` |
| Anima-Turbo | 8-12 | `1.0` | `euler` | `cyberzit_quality` |

These are starting points rather than fixed requirements. `cyberzit_balanced`
is a useful alternative when you want a milder schedule. The `quality` name
does not guarantee better images than another preset or ComfyUI's `simple`
scheduler; see the comparison below.

### SamplerCustomAdvanced

Add **CyberZiT Scheduler** from:

```text
sampling > custom_sampling > schedulers
```

Connect its `SIGMAS` output to the `sigmas` input of
`SamplerCustomAdvanced`. The node exposes:

- `steps`: number of sampling steps;
- `preset`: `fast`, `balanced`, or `quality`;
- `detail`: a small adjustment to the selected trajectory.

## Presets

At neutral `detail=0.0`:

| Preset | Flow shift | Behaviour |
| --- | ---: | --- |
| `fast` | `1.0` | Exact linear `1.0 -> 0.0` trajectory |
| `balanced` | `1.75` | Mild shift; a middle ground between directness and structure |
| `quality` | `3.0` | Retains more sampling points in the high and middle sigma regions |

The `detail` control fine-tunes a preset without changing its identity:

- `0.0` keeps the preset unchanged;
- negative values retain more of the high-sigma structure phase;
- positive values allocate more of the path to low-sigma refinement.

`detail` is available only on the standalone **CyberZiT Scheduler** node. It
does not need to be configured elsewhere. Refiner steps, CFG, denoise, and the
sampler remain settings of your workflow and are not changed by CyberZiT.

All presets use the same number of sampling steps. `fast` does not reduce the
step count, and `quality` does not add steps. Higher shifts keep intermediate
sigmas higher and also increase the final jump to zero. At nine steps and
neutral detail, that final jump is approximately `0.111` for `fast`, `0.179`
for `balanced`, and `0.273` for `quality`. Negative detail increases it further.
Image-quality tradeoffs need to be compared in your own workflow; this
repository does not include a reproducible image benchmark for the presets.

### Comparison with ComfyUI's simple scheduler

ComfyUI's built-in `simple` scheduler selects values from the model's sigma
table. Its default Z-Image and Anima configurations use shift `3.0`, with the
same flow-shift formula as `quality`. With an unchanged 1,000-value flow table,
eight requested steps, and `detail=0.0`, `quality` matches the `simple`
schedule at float32 precision. At nine requested steps the largest difference
is about `0.0018`, due to selection of discrete table entries and floating-point
rounding. Different model shifts, table sizes, denoise settings, or samplers
that adjust the requested step count can change this comparison.

CyberZiT provides explicit fixed-shift presets and, through the standalone
node, a `detail` adjustment. `fast` and `balanced` use lower shifts than the
default `3.0` of these models; `quality` is not claimed to be a new or superior
trajectory compared with `simple` under the matching conditions above.

Implementation references: ComfyUI's
[simple scheduler](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/samplers.py),
[flow sigma table](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/model_sampling.py),
and [model defaults](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/supported_models.py).

## How it works

Every CyberZiT curve:

- contains exactly `steps + 1` sigma values;
- starts at `1.0` and ends at `0.0`;
- is strictly descending;
- is deterministic, making presets easy to compare with the same seed.

The scheduler changes only the sigma trajectory. It does not replace the
sampler and does not modify the model, prompt, CFG, denoise, or latent.

## Troubleshooting

### The CyberZiT entries do not appear in KSampler

Update ComfyUI and restart it. CyberZiT uses ComfyUI's scheduler registration
API for the KSampler menu. If that API is unavailable in an older build, the
standalone **CyberZiT Scheduler** node remains usable with
`SamplerCustomAdvanced`.

### KSampler reports that ModelSamplingDiscreteFlow is required

The selected model uses an unsupported sampling type. Choose a scheduler
compatible with that model. Selecting CyberZiT from the global menu does not
imply that it supports every model. Using the standalone node bypasses the
check but does not resolve the incompatibility.

### Existing workflows

The registered names are intentionally stable. Workflows using `cyberzit`,
`cyberzit_fast`, `cyberzit_balanced`, or `cyberzit_quality` can continue using
those exact names. Preset values, neutral detail, and generated curves for
supported models are unchanged. The compatibility check only changes the
KSampler path for unsupported sampling types, which now raise an error.

## Development

The schedule mathematics is isolated from ComfyUI and PyTorch. Run the test
suite with:

```bash
python -m unittest discover -s tests -v
```

## License

[MIT](LICENSE)
