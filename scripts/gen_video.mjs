#!/usr/bin/env node
// Text-to-video / image-to-video caller (zero deps, node fetch).
// Default provider is a fal.ai-style queue API (submit -> poll -> download);
// swap the endpoint/model for whatever video model you prefer. Same shape as
// gen_image.mjs. Motion generation is billed per second — use it sparingly.
//
// Key (in order): env VIDEO_API_KEY -> ~/.config/text-to-video/key (single line, chmod 600).
// The key is never printed.
//
// Usage:
//   node scripts/gen_video.mjs --prompt-file <x.txt> --out output/clip/a.mp4 \
//     [--model fal-ai/bytedance/seedance/v1/pro/text-to-video] [--resolution 720p] \
//     [--aspect-ratio 16:9] [--duration 5] [--image-url <URL>]
//
// resolution: 480p|720p|1080p   aspect_ratio: 16:9|9:16|1:1|4:3|3:4|21:9   duration: 4-15 (sec)
// image-to-video: add --image-url (public URL) or --image-file (local, sent as a data URI)
// and switch --model to an .../image-to-video variant.

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join, dirname } from "node:path";

const QUEUE = "https://queue.fal.run";

function loadKey() {
  if (process.env.VIDEO_API_KEY) return process.env.VIDEO_API_KEY.trim();
  const f = join(homedir(), ".config", "text-to-video", "key");
  if (existsSync(f)) return readFileSync(f, "utf8").trim();
  console.error("No video key found: set VIDEO_API_KEY or write ~/.config/text-to-video/key (single line, chmod 600)");
  process.exit(2);
}

function parseArgs(a) {
  const o = {};
  for (let i = 0; i < a.length; i++) {
    if (a[i].startsWith("--")) {
      const k = a[i].slice(2);
      o[k] = a[i + 1] && !a[i + 1].startsWith("--") ? a[++i] : "true";
    }
  }
  return o;
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const model = args.model || "fal-ai/bytedance/seedance/v1/pro/text-to-video";
  const resolution = args.resolution || "720p";
  const duration = args.duration || "5";
  const aspect = args["aspect-ratio"] || "16:9";
  const out = args.out || "output/clip/out.mp4";

  let prompt = args.prompt;
  if (args["prompt-file"]) prompt = readFileSync(args["prompt-file"], "utf8").trim();
  if (!prompt || prompt === "true") { console.error('Need --prompt "..." or --prompt-file <path>'); process.exit(2); }

  const key = loadKey();
  const input = { prompt, resolution, duration };
  // aspect_ratio: image-to-video usually follows the first frame (send "auto" to omit);
  // text-to-video uses an explicit ratio.
  if (aspect && aspect !== "auto") input.aspect_ratio = aspect;
  if (args["image-url"]) input.image_url = args["image-url"];
  // image-to-video first frame from a local file -> base64 data URI (no upload step needed)
  if (args["image-file"]) {
    const p = args["image-file"];
    const lp = p.toLowerCase();
    const ext = lp.endsWith(".png") ? "png" : lp.endsWith(".webp") ? "webp" : "jpeg";
    input.image_url = `data:image/${ext};base64,${readFileSync(p).toString("base64")}`;
  }
  // turn off the model's auto-audio (default true) — you lay your own music/voice in post
  if (args["generate-audio"]) input.generate_audio = args["generate-audio"] === "true";

  console.log(`[gen_video] model=${model}  ${resolution} ${aspect} ${duration}s`);
  const sub = await fetch(`${QUEUE}/${model}`, {
    method: "POST",
    headers: { Authorization: `Key ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  const subt = await sub.text();
  if (!sub.ok) { console.error(`[gen_video] submit failed ${sub.status}:\n${subt}`); process.exit(1); }
  let sj;
  try { sj = JSON.parse(subt); } catch { console.error("submit not JSON:\n" + subt); process.exit(1); }
  const statusUrl = sj.status_url;
  const responseUrl = sj.response_url;
  if (!statusUrl || !responseUrl) { console.error("[gen_video] no status_url/response_url:\n" + subt); process.exit(1); }
  console.log(`[gen_video] request=${sj.request_id} polling (every 5s)...`);

  let done = false;
  for (let i = 0; i < 120; i++) {
    await sleep(5000);
    const s = await fetch(statusUrl, { headers: { Authorization: `Key ${key}` } });
    const stt = await s.text();
    let stj;
    try { stj = JSON.parse(stt); } catch { continue; }
    const st = stj.status;
    process.stdout.write(`\r[gen_video] ${(i + 1) * 5}s status=${st}        `);
    if (st === "COMPLETED") { done = true; break; }
    if (st === "FAILED" || st === "ERROR") { console.error("\n[gen_video] job failed:\n" + stt); process.exit(1); }
  }
  if (!done) { console.error("\n[gen_video] poll timeout"); process.exit(1); }

  const r = await fetch(responseUrl, { headers: { Authorization: `Key ${key}` } });
  const rt = await r.text();
  let rj;
  try { rj = JSON.parse(rt); } catch { console.error("result not JSON:\n" + rt); process.exit(1); }
  const videoUrl = (rj.video && rj.video.url) || rj.video_url || (rj.output && rj.output.video && rj.output.video.url);
  if (!videoUrl) { console.error("[gen_video] no video url in result:\n" + rt); process.exit(1); }
  console.log("\n[gen_video] " + videoUrl);

  mkdirSync(dirname(out), { recursive: true });
  const v = await fetch(videoUrl);
  const buf = Buffer.from(await v.arrayBuffer());
  writeFileSync(out, buf);
  writeFileSync(out.replace(/\.mp4$/i, "") + ".prompt.txt", prompt, "utf8");
  console.log(`[gen_video] saved: ${out} (${(buf.length / 1024 / 1024).toFixed(1)}MB)`);
}

main().catch((e) => { console.error("[gen_video] error:", e.message); process.exit(1); });
