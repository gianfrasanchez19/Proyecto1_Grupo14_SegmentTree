#!/usr/bin/env python3
"""Compila las pruebas y la demo de C++ con advertencias y (si es posible) sanitizadores.

Uso:  python scripts/build.py [--no-sanitize]
Busca un compilador en este orden: g++, clang++, y por ultimo `python -m ziglang c++`
(paquete pip `ziglang`, util en Windows sin compilador instalado).
Los binarios quedan en build/.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
EXE = ".exe" if sys.platform == "win32" else ""
WARN = ["-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Wshadow", "-Wconversion", "-Wno-nullability-completeness", "-O1", "-g"]


def find_compiler():
    for name in ("g++", "clang++"):
        if shutil.which(name):
            return [name]
    try:
        subprocess.run([sys.executable, "-m", "ziglang", "version"], check=True, capture_output=True)
        return [sys.executable, "-m", "ziglang", "c++"]
    except Exception:
        sys.exit("No se encontro g++, clang++ ni ziglang (pip install ziglang).")


def run(cmd):
    print(" ".join(map(str, cmd)))
    return subprocess.run(cmd, cwd=ROOT)


def main():
    BUILD.mkdir(exist_ok=True)
    cc = find_compiler()
    sanitize = "--no-sanitize" not in sys.argv
    targets = [("tests", "cpp/tests.cpp"), ("demo_trace", "cpp/demo_trace.cpp")]
    for name, src in targets:
        out = str(BUILD / (name + EXE))
        flags = list(WARN)
        if run(cc + flags + [src, "-o", out]).returncode:
            sys.exit(f"Fallo la compilacion de {src}")
        if sanitize and name == "tests":
            san_out = str(BUILD / ("tests_ubsan" + EXE))
            r = run(cc + flags + ["-fsanitize=undefined", "-fno-sanitize-recover=undefined", src, "-o", san_out])
            if r.returncode:
                print("(sanitizador UBSan no disponible con este compilador; se omite)")
    print("Compilacion terminada en", BUILD)


if __name__ == "__main__":
    main()
