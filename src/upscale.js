#!/usr/bin/env node
// QVAC Local Upscaler — runs ESRGAN super-resolution entirely on-device via
// Tether's QVAC SDK. No cloud call, no API key: the model downloads once to
// a local cache, then every upscale happens on this machine.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { exec } from "node:child_process";
import {
  loadModel,
  upscale,
  unloadModel,
  REALESRGAN_X4PLUS_ANIME_6B,
} from "@qvac/sdk";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function parseArgs(argv) {
  const args = { repeats: 1, tileSize: 128, open: true };
  const positional = [];
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--repeats") args.repeats = Number(argv[++i]);
    else if (arg === "--tile-size") args.tileSize = Number(argv[++i]);
    else if (arg === "--out") args.out = argv[++i];
    else if (arg === "--no-open") args.open = false;
    else positional.push(arg);
  }
  args.input = positional[0];
  return args;
}

function printUsage() {
  console.log(`
QVAC Local Upscaler — on-device image super-resolution

Usage:
  node src/upscale.js <input.png|input.jpg> [options]

Options:
  --repeats <n>     Number of upscale passes to chain (default: 1, i.e. 4x)
  --tile-size <n>   ESRGAN tile size in pixels (default: 128)
  --out <path>      Output file path (default: <input>.upscaled.png)
  --no-open         Don't auto-open the before/after comparison page

Example:
  node src/upscale.js ./samples/photo.jpg --repeats 1
`);
}

function toBase64Image(buffer, ext) {
  const mime = ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "image/png";
  return `data:${mime};base64,${buffer.toString("base64")}`;
}

function writeComparisonPage({ inputPath, outputPath, inputBuf, outputBuf, stats }) {
  const inExt = path.extname(inputPath).toLowerCase();
  const beforeSrc = toBase64Image(inputBuf, inExt);
  const afterSrc = toBase64Image(outputBuf, ".png");
  const reportPath = path.join(path.dirname(outputPath), "comparison.html");

  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>QVAC Local Upscaler — result</title>
<style>
  body { font-family: system-ui, sans-serif; background: #111; color: #eee; margin: 0; padding: 32px; }
  h1 { font-size: 20px; font-weight: 600; }
  p.meta { color: #9aa; font-size: 13px; margin-top: -8px; }
  .grid { display: flex; gap: 24px; flex-wrap: wrap; margin-top: 24px; }
  figure { margin: 0; flex: 1; min-width: 280px; }
  figcaption { font-size: 13px; color: #9aa; margin-bottom: 8px; }
  img { max-width: 100%; border-radius: 8px; border: 1px solid #333; display: block; }
  .badge { display: inline-block; background: #1f6feb22; color: #58a6ff; border: 1px solid #1f6feb55;
           padding: 2px 8px; border-radius: 999px; font-size: 12px; margin-left: 8px; }
</style>
</head>
<body>
  <h1>QVAC Local Upscaler <span class="badge">ran 100% on-device</span></h1>
  <p class="meta">Model: RealESRGAN x4plus-anime-6B &middot; Stats: ${JSON.stringify(stats)}</p>
  <div class="grid">
    <figure>
      <figcaption>Before</figcaption>
      <img src="${beforeSrc}" alt="original image" />
    </figure>
    <figure>
      <figcaption>After (QVAC upscale())</figcaption>
      <img src="${afterSrc}" alt="upscaled image" />
    </figure>
  </div>
</body>
</html>`;

  fs.writeFileSync(reportPath, html, "utf-8");
  return reportPath;
}

function openInBrowser(filePath) {
  const platform = process.platform;
  const cmd =
    platform === "win32"
      ? `start "" "${filePath}"`
      : platform === "darwin"
      ? `open "${filePath}"`
      : `xdg-open "${filePath}"`;
  exec(cmd, () => {});
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (!args.input) {
    printUsage();
    process.exit(1);
  }

  const inputPath = path.resolve(args.input);
  if (!fs.existsSync(inputPath)) {
    console.error(`✖ Input file not found: ${inputPath}`);
    process.exit(1);
  }

  const ext = path.extname(inputPath).toLowerCase();
  if (![".png", ".jpg", ".jpeg"].includes(ext)) {
    console.error("✖ Input must be a .png, .jpg, or .jpeg file");
    process.exit(1);
  }

  const outputPath = args.out
    ? path.resolve(args.out)
    : inputPath.replace(/(\.[^.]+)$/, ".upscaled.png");

  console.log("▸ Loading RealESRGAN model on-device (first run downloads the weights)...");

  const modelId = await loadModel({
    modelSrc: REALESRGAN_X4PLUS_ANIME_6B,
    modelType: "diffusion",
    modelConfig: {
      mode: "upscale",
      upscaler: { tile_size: args.tileSize },
    },
    onProgress: (p) => {
      const mb = (n) => (n / 1e6).toFixed(1);
      const line = `  ▸ Downloading ${p.percentage.toFixed(0)}% (${mb(p.downloaded)}/${mb(p.total)} MB)`;
      process.stderr.write(process.stderr.isTTY ? `\r${line}` : `${line}\n`);
      if (p.percentage >= 100) process.stderr.write("\n");
    },
  });

  console.log("▸ Model loaded. Running on-device upscale...");

  const inputBuf = fs.readFileSync(inputPath);
  const { outputs, stats } = upscale({
    modelId,
    image: inputBuf,
    repeats: args.repeats,
  });

  const [upscaledPng] = await outputs;
  const finalStats = await stats;

  fs.writeFileSync(outputPath, upscaledPng);
  console.log(`✔ Wrote upscaled image to ${outputPath}`);
  console.log(`  stats: ${JSON.stringify(finalStats)}`);

  await unloadModel({ modelId });

  const reportPath = writeComparisonPage({
    inputPath,
    outputPath,
    inputBuf,
    outputBuf: upscaledPng,
    stats: finalStats,
  });
  console.log(`✔ Wrote before/after comparison page to ${reportPath}`);

  if (args.open) openInBrowser(reportPath);
}

main().catch((error) => {
  console.error("✖", error);
  process.exit(1);
});
