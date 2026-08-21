#!/usr/bin/env node
// Text-to-speech / narration caller (zero deps, node fetch). Default provider
// is a fal.ai-style queue TTS API; swap the endpoint/model/voice for whatever
// TTS you prefer. Same shape as gen_music.mjs.
//
// Key (in order): env VOICE_API_KEY -> ~/.config/text-to-speech/key. Never printed.
//
// Usage:
//   node scripts/gen_voice.mjs --text-file <x.txt> --out output/audio/narration.mp3 \
//     [--voice-id audiobook_male_2] [--speed 1.0] [--emotion neutral] [--format mp3]
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join, dirname } from "node:path";

const QUEUE = "https://queue.fal.run";
const MODEL = "fal-ai/minimax/speech-02-hd";

function loadKey() {
  if (process.env.VOICE_API_KEY) return process.env.VOICE_API_KEY.trim();
  const f = join(homedir(), ".config", "text-to-speech", "key");
  if (existsSync(f)) return readFileSync(f, "utf8").trim();
  console.error("No voice key found: set VOICE_API_KEY or write ~/.config/text-to-speech/key"); process.exit(2);
}
function parseArgs(a) {
  const o = {};
  for (let i = 0; i < a.length; i++) if (a[i].startsWith("--")) {
    const k = a[i].slice(2);
    o[k] = a[i + 1] && !a[i + 1].startsWith("--") ? a[++i] : "true";
  }
  return o;
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
function findAudioUrl(o) {
  if (!o || typeof o !== "object") return null;
  for (const k of ["audio", "audio_file", "output", "file"]) {
    const v = o[k];
    if (v && typeof v === "object" && typeof v.url === "string") return v.url;
  }
  if (typeof o.audio_url === "string") return o.audio_url;
  for (const v of Object.values(o)) {
    if (v && typeof v === "object") { const u = findAudioUrl(v); if (u) return u; }
  }
  return null;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const out = args.out || "output/audio/narration.mp3";
  let text = args.text;
  if (args["text-file"]) text = readFileSync(args["text-file"], "utf8").trim();
  if (!text || text === "true") { console.error("Need --text or --text-file"); process.exit(2); }

  const input = {
    text,
    voice_setting: {
      voice_id: args["voice-id"] || "audiobook_male_2",
      speed: parseFloat(args.speed || "1.0"),
      vol: parseFloat(args.vol || "1.0"),
      pitch: parseInt(args.pitch || "0", 10),
    },
    output_format: args.format || "url",
  };
  if (args.emotion && args.emotion !== "true") input.voice_setting.emotion = args.emotion;

  const key = loadKey();
  console.log(`[gen_voice] ${MODEL} voice=${input.voice_setting.voice_id} speed=${input.voice_setting.speed}`);
  const sub = await fetch(`${QUEUE}/${MODEL}`, {
    method: "POST",
    headers: { Authorization: `Key ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  const subt = await sub.text();
  if (!sub.ok) { console.error(`[gen_voice] submit failed ${sub.status}:\n${subt}`); process.exit(1); }
  const sj = JSON.parse(subt);
  const { status_url, response_url } = sj;
  if (!status_url) { console.error("[gen_voice] no status_url:\n" + subt); process.exit(1); }
  console.log(`[gen_voice] request=${sj.request_id} polling...`);
  let done = false;
  for (let i = 0; i < 60; i++) {
    await sleep(3000);
    const s = await fetch(status_url, { headers: { Authorization: `Key ${key}` } });
    let stj; try { stj = JSON.parse(await s.text()); } catch { continue; }
    process.stdout.write(`\r[gen_voice] ${(i + 1) * 3}s status=${stj.status}        `);
    if (stj.status === "COMPLETED") { done = true; break; }
    if (stj.status === "FAILED" || stj.status === "ERROR") { console.error("\nfailed"); process.exit(1); }
  }
  if (!done) { console.error("\npoll timeout"); process.exit(1); }
  const r = await fetch(response_url, { headers: { Authorization: `Key ${key}` } });
  const rt = await r.text();
  let rj; try { rj = JSON.parse(rt); } catch { console.error("result not JSON:\n" + rt); process.exit(1); }
  const url = findAudioUrl(rj);
  if (!url) { console.error("[gen_voice] no audio url in result:\n" + rt.slice(0, 800)); process.exit(1); }
  console.log("\n[gen_voice] " + url);
  mkdirSync(dirname(out), { recursive: true });
  const buf = Buffer.from(await (await fetch(url)).arrayBuffer());
  writeFileSync(out, buf);
  console.log(`[gen_voice] saved: ${out} (${(buf.length / 1024).toFixed(0)}KB)`);
}
main().catch((e) => { console.error("[gen_voice] error:", e.message); process.exit(1); });
