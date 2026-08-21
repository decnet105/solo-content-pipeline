#!/usr/bin/env node
// Image-generation caller: turn a text prompt into a still (zero deps, node fetch).
// Default provider is an OpenAI Images-class endpoint; swap it for whatever
// image model you prefer. Used for scene plates / marketing stills.
//
// Key (in order): env IMAGE_API_KEY -> ~/.config/image-gen/key (single line, chmod 600).
// The key is never printed and never written to any output or log.
//
// Usage:
//   node scripts/gen_image.mjs \
//     --prompt-file /path/to/prompt.txt \
//     --out output/img/scene-01.png \
//     [--size 1024x1536] [--quality high] [--model gpt-image-2] [--n 1]
//
//   or pass the prompt directly:  --prompt "a photorealistic ..."
//
// size: 1024x1024 | 1024x1536 (portrait) | 1536x1024 (landscape) | auto
// quality: low | medium | high | auto
// Returns data[].b64_json (base64 PNG). Each run also writes <out>.prompt.txt
// so the exact prompt is reproducible.

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join, dirname } from "node:path";

const ENDPOINT = "https://api.openai.com/v1/images/generations";

function parseArgs(argv) {
  const a = {};
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k.startsWith("--")) {
      const key = k.slice(2);
      const val = argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : "true";
      a[key] = val;
    }
  }
  return a;
}

function loadKey() {
  if (process.env.IMAGE_API_KEY) return process.env.IMAGE_API_KEY.trim();
  const keyFile = join(homedir(), ".config", "image-gen", "key");
  if (existsSync(keyFile)) return readFileSync(keyFile, "utf8").trim();
  console.error(
    "No image key found. Set IMAGE_API_KEY, or write the key to ~/.config/image-gen/key (single line, chmod 600)."
  );
  process.exit(2);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const model = args.model || "gpt-image-2";
  const size = args.size || "1024x1536";
  const quality = args.quality || "high";
  const n = parseInt(args.n || "1", 10);
  const out = args.out || "output/img/out.png";

  let prompt = args.prompt;
  if (args["prompt-file"]) prompt = readFileSync(args["prompt-file"], "utf8").trim();
  if (!prompt || prompt === "true") {
    console.error('Must provide --prompt "..." or --prompt-file <path>');
    process.exit(2);
  }

  const key = loadKey();
  console.log(`[gen_image] model=${model} size=${size} quality=${quality} n=${n}`);
  console.log(`[gen_image] out=${out}`);

  const resp = await fetch(ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${key}`,
    },
    body: JSON.stringify({ model, prompt, size, quality, n }),
  });

  if (!resp.ok) {
    const text = await resp.text();
    console.error(`[gen_image] API error ${resp.status}:\n${text}`);
    process.exit(1);
  }

  const data = await resp.json();
  const items = data.data || [];
  if (!items.length) {
    console.error("[gen_image] no image data returned");
    process.exit(1);
  }

  mkdirSync(dirname(out), { recursive: true });
  const outPaths = [];
  items.forEach((item, idx) => {
    const b64 = item.b64_json;
    if (!b64) {
      console.error(`[gen_image] item ${idx} has no b64_json`);
      return;
    }
    const p = n > 1 ? out.replace(/\.png$/i, `-${idx + 1}.png`) : out;
    writeFileSync(p, Buffer.from(b64, "base64"));
    outPaths.push(p);
  });

  // store the prompt used for reproducibility
  writeFileSync(out.replace(/\.png$/i, "") + ".prompt.txt", prompt, "utf8");

  console.log(`[gen_image] done:\n${outPaths.map((p) => "  " + p).join("\n")}`);
  if (data.usage) console.log(`[gen_image] usage: ${JSON.stringify(data.usage)}`);
}

main().catch((e) => {
  console.error("[gen_image] uncaught error:", e.message);
  process.exit(1);
});
