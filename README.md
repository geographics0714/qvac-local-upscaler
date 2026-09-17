# QVAC Local Upscaler

A tiny CLI that upscales a photo entirely on your own machine using
[Tether's QVAC SDK](https://github.com/tetherto/qvac) — no cloud call, no
API key, no bill. The model (RealESRGAN x4plus-anime-6B) downloads once to a
local cache the first time you run it, then every upscale after that runs
fully offline.

It calls the QVAC SDK's `loadModel()` and `upscale()` functions directly.

## What it does

Give it an image, it runs on-device ESRGAN super-resolution and opens a
before/after comparison page in your browser.

```
node src/upscale.js ./samples/photo.jpg
```

## SDK version

Built and tested against `@qvac/sdk` **v0.19.x** (see [package.json](package.json)).

## Requirements

- Node.js `>= 22.17`
- A machine that meets [QVAC's system requirements](https://docs.qvac.tether.io/system-requirements)
  (Windows needs Vulkan `>= 1.4`; macOS/Linux need Metal/Vulkan respectively)
- ~2 GB free disk space for the model weights on first run

## Install

```bash
git clone https://github.com/<your-username>/qvac-local-upscaler.git
cd qvac-local-upscaler
npm install
```

## Run

```bash
node src/upscale.js <path-to-image.png-or-.jpg> [options]
```

Options:

| Flag | Description | Default |
| --- | --- | --- |
| `--repeats <n>` | Number of chained upscale passes (each pass is a native 4x scale) | `1` |
| `--tile-size <n>` | ESRGAN tile size in pixels, tune down on low-memory devices | `128` |
| `--out <path>` | Output file path | `<input>.upscaled.png` |
| `--no-open` | Don't auto-open the before/after comparison page | opens by default |

Example:

```bash
node src/upscale.js ./samples/portrait.jpg --repeats 1 --tile-size 128
```

On first run the model weights download automatically with a progress bar
printed to the terminal. Every run after that loads from the local cache and
runs fully offline — your image never leaves your machine.

## How it uses QVAC

```js
import { loadModel, upscale, unloadModel, REALESRGAN_X4PLUS_ANIME_6B } from "@qvac/sdk";

const modelId = await loadModel({
  modelSrc: REALESRGAN_X4PLUS_ANIME_6B,
  modelType: "diffusion",
  modelConfig: { mode: "upscale", upscaler: { tile_size: 128 } },
});

const { outputs, stats } = upscale({ modelId, image: inputImageBuffer, repeats: 1 });
const [upscaledPng] = await outputs;

await unloadModel({ modelId });
```

See [src/upscale.js](src/upscale.js) for the full implementation.

## License

[MIT](LICENSE)
