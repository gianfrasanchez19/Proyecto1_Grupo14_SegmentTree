#!/usr/bin/env python3
"""Extrae del MP4 final (con ffmpeg) un fotograma por cada paso clave. Usa build/timeline.json.
Uso: python scripts/extract_evidence.py [video.mp4]   -> evidence/<clave>.png"""
import json
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent.parent
video = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "Video_Proyecto1_Grupo14.mp4"
timeline = json.loads((ROOT / "build" / "timeline.json").read_text(encoding="utf-8"))
out = ROOT / "evidence"
out.mkdir(exist_ok=True)
ff = imageio_ffmpeg.get_ffmpeg_exe()
for t in timeline:
    if not t["key"]:
        continue
    ts = t["start"] + max(0.0, t["dur"] - 0.3)   # casi al final del paso: animacion ya terminada
    dst = out / f"{t['key']}.png"
    subprocess.run([ff, "-y", "-loglevel", "error", "-ss", f"{ts:.2f}", "-i", str(video), "-frames:v", "1", str(dst)], check=True)
    print(dst.name, f"@ {ts:.1f}s")
