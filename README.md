# ComfyUI-CyberZiT

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
is a useful alternative when you want a milder schedule.

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

| Preset | Flow shift | Behaviour |
| --- | ---: | --- |
| `fast` | `1.0` | Exact linear `1.0 -> 0.0` trajectory |
| `balanced` | `1.75` | Mild shift; a middle ground between directness and structure |
| `quality` | `3.0` | Retains more sampling points in the high and middle sigma regions |

The `detail` control fine-tunes a preset without changing its identity:

- `0.0` keeps the calibrated preset unchanged;
- negative values retain more of the high-sigma structure phase;
- positive values allocate more of the path to low-sigma refinement.

`detail` is available only on the standalone **CyberZiT Scheduler** node. It
does not need to be configured elsewhere. Refiner steps, CFG, denoise, and the
sampler remain settings of your workflow and are not changed by CyberZiT.

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

### Existing workflows

The registered names are intentionally stable. Workflows using `cyberzit`,
`cyberzit_fast`, `cyberzit_balanced`, or `cyberzit_quality` can continue using
those exact names.

## Development

The schedule mathematics is isolated from ComfyUI and PyTorch. Run the test
suite with:

```bash
python -m unittest discover -s tests -v
```

## License

[MIT](LICENSE)
