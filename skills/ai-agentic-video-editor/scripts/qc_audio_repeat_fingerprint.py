#!/usr/bin/env python3
"""Fail when decoded audio contains bit-exact repeated short windows."""

from __future__ import annotations

import argparse
import hashlib
import json
import mmap
import os
import subprocess
import tempfile
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--window-seconds", type=float, default=5.0)
    parser.add_argument("--hop-seconds", type=float, default=1.0)
    parser.add_argument("--sample-rate", type=int, default=8000)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    if args.window_seconds <= 0 or args.hop_seconds <= 0:
        raise SystemExit("window and hop must be positive")
    if args.sample_rate <= 0:
        raise SystemExit("sample rate must be positive")

    # Canonical mono PCM makes the result independent of the source container.
    with tempfile.NamedTemporaryFile(suffix=".s16le") as raw:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-i",
                str(args.input),
                "-ac",
                "1",
                "-ar",
                str(args.sample_rate),
                "-f",
                "s16le",
                raw.name,
            ],
            check=True,
        )
        raw.flush()
        byte_count = os.path.getsize(raw.name)
        window_bytes = round(args.window_seconds * args.sample_rate) * 2
        hop_bytes = round(args.hop_seconds * args.sample_rate) * 2
        if byte_count < window_bytes:
            raise SystemExit("audio is shorter than the fingerprint window")

        first_offset: dict[bytes, int] = {}
        duplicates: list[dict[str, float | str]] = []
        checked = 0
        with mmap.mmap(raw.fileno(), 0, access=mmap.ACCESS_READ) as pcm:
            for offset in range(0, byte_count - window_bytes + 1, hop_bytes):
                window = pcm[offset : offset + window_bytes]
                digest = hashlib.blake2b(window, digest_size=16).digest()
                checked += 1
                previous = first_offset.get(digest)
                if previous is None:
                    first_offset[digest] = offset
                    continue
                # Verify bytes as well as the digest and ignore overlapping hits.
                if offset - previous < window_bytes:
                    continue
                if pcm[previous : previous + window_bytes] == window:
                    duplicates.append(
                        {
                            "first_seconds": round(previous / (2 * args.sample_rate), 3),
                            "repeat_seconds": round(offset / (2 * args.sample_rate), 3),
                            "fingerprint": digest.hex(),
                        }
                    )

    result = {
        "schema_version": "1.0",
        "file": str(args.input),
        "file_sha256": sha256(args.input),
        "decoded_sample_rate": args.sample_rate,
        "window_seconds": args.window_seconds,
        "hop_seconds": args.hop_seconds,
        "windows_checked": checked,
        "exact_repeat_count": len(duplicates),
        "exact_repeats": duplicates[:100],
        "status": "FAIL" if duplicates else "PASS",
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered)
    print(rendered, end="")
    return 1 if duplicates else 0


if __name__ == "__main__":
    raise SystemExit(main())
