#!/usr/bin/env node
// Music-generation caller (zero deps, node fetch). Default provider is a
// fal.ai-style queue API; swap the endpoint/model for whatever music model you
// prefer. Same shape as gen_video.mjs. Instrumental by default (no vocals to
// fight the subtitles).
//
// Key (in order): env MUSIC_API_KEY -> ~/.config/music/key. Never printed.
//
// Usage:
//   node scripts/gen_music.mjs --prompt-file <x.txt> --out output/audio/bgm.mp3 \
//     [--model fal-ai/minimax-music/v2.6] [--vocals]   (add --vocals for a vocal track)
// prompt: describe style / mood / genre / scenario + BPM (write it in the text,
// e.g. "115 BPM"). 10-2000 characters.
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { homedir } from "node:os";
import { join, dirname } from "node:path";

const QUEUE = "https://queue.fal.run";
function loadKey() {
  if (process.env.MUSIC_API_KEY) return process.env.MUSIC_API_KEY.trim();
  const f = join(homedir(), ".config", "music", "key");
  if (existsSync(f)) return readFileSync(f, "utf8").trim();
  console.error("No music key found: set MUSIC_API_KEY or write ~/.config/music/key"); process.exit(2);
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

// recursively find the first audio url (music models return varied shapes)
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
  const model = args.model || "fal-ai/minimax-music/v2.6";
  const out = args.out || "output/audio/bgm.mp3";
  let prompt = args.prompt;
  if (args["prompt-file"]) prompt = readFileSync(args["prompt-file"], "utf8").trim();
  if (!prompt || prompt === "true") { console.error("Need --prompt or --prompt-file"); process.exit(2); }

  const key = loadKey();
  const input = { prompt, is_instrumental: !args.vocals };
  console.log(`[gen_music] model=${model}  instrumental=${input.is_instrumental}`);
  const sub = await fetch(`${QUEUE}/${model}`, {
    method: "POST",
    headers: { Authorization: `Key ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  const subt = await sub.text();
  if (!sub.ok) { console.error(`[gen_music] submit failed ${sub.status}:\n${subt}`); process.exit(1); }
  const sj = JSON.parse(subt);
  const { status_url, response_url } = sj;
  if (!status_url) { console.error("[gen_music] no status_url:\n" + subt); process.exit(1); }
  console.log(`[gen_music] request=${sj.request_id} polling...`);
  let done = false;
  for (let i = 0; i < 120; i++) {
    await sleep(5000);
    const s = await fetch(status_url, { headers: { Authorization: `Key ${key}` } });
    let stj; try { stj = JSON.parse(await s.text()); } catch { continue; }
    process.stdout.write(`\r[gen_music] ${(i + 1) * 5}s status=${stj.status}        `);
    if (stj.status === "COMPLETED") { done = true; break; }
    if (stj.status === "FAILED" || stj.status === "ERROR") { console.error("\nfailed"); process.exit(1); }
  }
  if (!done) { console.error("\npoll timeout"); process.exit(1); }
  const r = await fetch(response_url, { headers: { Authorization: `Key ${key}` } });
  const rt = await r.text();
  let rj; try { rj = JSON.parse(rt); } catch { console.error("result not JSON:\n" + rt); process.exit(1); }
  const url = findAudioUrl(rj);
  if (!url) { console.error("[gen_music] no audio url in result:\n" + rt.slice(0, 800)); process.exit(1); }
  console.log("\n[gen_music] " + url);
  mkdirSync(dirname(out), { recursive: true });
  const buf = Buffer.from(await (await fetch(url)).arrayBuffer());
  writeFileSync(out, buf);
  writeFileSync(out.replace(/\.\w+$/i, "") + ".prompt.txt", prompt, "utf8");
  console.log(`[gen_music] saved: ${out} (${(buf.length / 1024 / 1024).toFixed(2)}MB)`);
}
main().catch((e) => { console.error("[gen_music] error:", e.message); process.exit(1); });
