#!/usr/bin/env python3
"""Genera el video MP4 a partir de la traza JSON exportada por el programa C++.

Uso:
  python animation/render_video.py --trace trace/trace_demo.json --out Video_Proyecto1_Grupo14.mp4
Opciones:
  --frames DIR   guarda un PNG representativo por cada paso marcado con `key`
  --no-video     solo verifica la traza, genera audio/tiempos e imprime la duracion (sin render)
  --rate N       velocidad de la voz de Windows (-10..10, por defecto 3)
Requiere: Pillow, numpy, imageio-ffmpeg (ver requirements.txt) y Windows (voz System.Speech).
"""
import argparse
import hashlib
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import trace_model  # noqa: E402
from scene_draw import render, W, H  # noqa: E402
from storyboard import build_storyboard  # noqa: E402

FPS = 20
ANIM_S = 1.2      # los movimientos duran ~1.2 s; despues el fotograma es estatico
FADE_S = 0.35     # fundido entre pasos
PAD_S = 0.7       # pausa tras cada narracion
VOICE = "Microsoft Helena Desktop"


def synthesize(steps, workdir, rate):
    """Genera un WAV por paso narrado (cache por hash del texto) y devuelve sus duraciones."""
    if sys.platform != "win32":
        print("AVISO: sin Windows no hay voz System.Speech; el video se genera sin voz en off (solo texto en pantalla).")
        return {}
    audio_dir = workdir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    jobs, files = [], {}
    for i, s in enumerate(steps):
        if s.narr:
            h = hashlib.sha1(f"{VOICE}|{rate}|{s.narr}".encode("utf-8")).hexdigest()[:16]
            f = audio_dir / f"{h}.wav"
            files[i] = f
            jobs.append({"file": str(f), "text": s.narr})
    jobs_json = workdir / "tts_jobs.json"
    jobs_json.write_text(json.dumps(jobs, ensure_ascii=False), encoding="utf-8")
    subprocess.run(["powershell", "-NoProfile", "-File", str(HERE / "tts.ps1"), "-Jobs", str(jobs_json),
                    "-Voice", VOICE, "-Rate", str(rate)], check=True)
    return files


def read_wav(path):
    with wave.open(str(path), "rb") as w:
        assert w.getsampwidth() == 2 and w.getnchannels() == 1
        return w.getframerate(), np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames")
    ap.add_argument("--no-video", action="store_true")
    ap.add_argument("--rate", type=int, default=3)
    a = ap.parse_args()

    tr = trace_model.load(a.trace)   # verifica coherencia de eventos y capturas
    print("traza verificada:", len(tr.nodes), "nodos,", sum(len(v) for v in tr.sections.values()), "eventos")
    steps = build_storyboard(tr)
    workdir = Path(a.out).resolve().parent / "build"
    workdir.mkdir(exist_ok=True)
    files = synthesize(steps, workdir, a.rate)

    # --- duraciones: la voz manda; un paso dura lo que su narracion + pausa (o su minimo)
    sr = 16000
    clips = {}
    for i, f in files.items():
        sr, clips[i] = read_wav(f)
    for i, s in enumerate(steps):
        if i in clips:
            s.dur = max(s.dur, len(clips[i]) / sr + PAD_S)
        elif not files and s.caption:   # sin voz: tiempo de lectura (~14 caracteres por segundo)
            s.dur = max(s.dur, len(s.caption) / 14 + 1.0)
    total = sum(s.dur for s in steps)
    t0, timeline = 0.0, []
    for i, s in enumerate(steps):
        timeline.append({"step": i, "key": s.key, "start": round(t0, 2), "dur": round(s.dur, 2), "caption": s.caption or s.narr})
        t0 += s.dur
    (workdir / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"pasos: {len(steps)}  duracion total: {total:.1f} s = {int(total // 60)}:{int(total % 60):02d}")
    if a.no_video:
        if a.frames:   # vista previa: un PNG por paso (sin video)
            Path(a.frames).mkdir(parents=True, exist_ok=True)
            for i, s in enumerate(steps):
                render(s.state, s.caption, 1.0).save(Path(a.frames) / f"{i:03d}.png")
        return

    # --- pista de audio completa
    chunks = []
    for i, s in enumerate(steps):
        n = int(round(s.dur * sr))
        buf = np.zeros(n, dtype=np.int16)
        if i in clips:
            buf[:len(clips[i])] = clips[i][:n]
        chunks.append(buf)
    audio = np.concatenate(chunks)
    wav_path = workdir / "narracion.wav"
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(audio.tobytes())

    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", str(wav_path), "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(a.out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    frames_dir = Path(a.frames) if a.frames else None
    if frames_dir:
        frames_dir.mkdir(parents=True, exist_ok=True)

    prev_img, written = None, 0
    for i, s in enumerate(steps):
        nframes = max(1, int(round(s.dur * FPS)))
        n_anim = min(nframes, int(ANIM_S * FPS))
        n_fade = int(FADE_S * FPS)
        static = render(s.state, s.caption, 1.0)
        for f in range(nframes):
            if f < n_anim and (s.state.fly or s.state.focus is not None):
                img = render(s.state, s.caption, (f + 1) / n_anim)
            else:
                img = static
            if prev_img is not None and f < n_fade:
                img = Image.blend(prev_img, img, (f + 1) / (n_fade + 1))
            proc.stdin.write(img.tobytes())
            written += 1
        prev_img = static
        if frames_dir and s.key:
            static.save(frames_dir / f"{i:03d}_{s.key}.png")
        if i % 10 == 0:
            print(f"  paso {i + 1}/{len(steps)}", flush=True)
    proc.stdin.close()
    if proc.wait():
        sys.exit("ffmpeg fallo")
    print(f"video escrito: {a.out}  ({written} fotogramas a {FPS} fps)")


if __name__ == "__main__":
    main()

