"""Dibujo de un fotograma a partir de un `State` (posiciones, colores, transiciones).

Aqui SOLO hay logica visual. Los valores (sumas, resultados, solapamientos) llegan ya
calculados por la traza de C++; este modulo nunca suma ni clasifica intervalos.
"""
import math
from dataclasses import dataclass, field
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
FONTS = "C:/Windows/Fonts/"
BG = (14, 17, 23)
TXT = (232, 237, 246)
MUTED = (140, 150, 168)
PANEL_BG = (22, 27, 38)

# estilo -> (relleno, borde, texto)
STY = {
    "normal": ((28, 34, 46), (96, 108, 130), TXT),
    "none": ((30, 32, 38), (110, 116, 128), (128, 134, 146)),
    "partial": ((72, 54, 14), (247, 182, 52), TXT),
    "total": ((16, 74, 46), (62, 208, 124), TXT),
    "path": ((20, 46, 88), (92, 162, 255), TXT),
    "leafmod": ((96, 30, 38), (255, 108, 108), TXT),
    "recalc": ((54, 36, 94), (184, 134, 255), TXT),
    "built": ((16, 62, 70), (72, 204, 214), TXT),
    "inrange": ((28, 40, 64), (120, 170, 255), TXT),
}

_fonts = {}


def font(size, bold=False, mono=False):
    key = (size, bold, mono)
    if key not in _fonts:
        name = "consolab.ttf" if (mono and bold) else "consola.ttf" if mono else "segoeuib.ttf" if bold else "segoeui.ttf"
        _fonts[key] = ImageFont.truetype(FONTS + name, size)
    return _fonts[key]


@dataclass
class State:
    n: int = 6
    nodes: dict = field(default_factory=dict)      # id -> (l, r)
    title: str = ""
    tag: str = ""
    show_array: bool = False
    show_days: bool = False
    arr: list = field(default_factory=list)
    arr_sty: dict = field(default_factory=dict)
    vis: set = field(default_factory=set)
    sums: dict = field(default_factory=dict)       # id -> valor mostrado (None => "?")
    sty: dict = field(default_factory=dict)
    panel: list = field(default_factory=list)      # (texto, color, tamano, negrita)
    legend: list = field(default_factory=list)     # (estilo, texto)
    extras: list = field(default_factory=list)     # primitivas libres
    focus: int = None
    fly: list = field(default_factory=list)        # (texto, origen, destino, color)


# ---------------------------------------------------------------- geometria
AL, AY, CELL_H = 100, 150, 80
TY0, TDY = 405, 130
BOX_W, BOX_H = 168, 84
PX, PY, PW = 1400, 150, 460
ACC_PT = (PX + PW // 2, 560)


def cell_w(n):
    return min(200, 1240 // max(n, 1))


def cell_center(st, i):
    return (AL + (i + 0.5) * cell_w(st.n), AY + CELL_H // 2)


def node_center(st, node):
    l, r = st.nodes[node]
    return (AL + ((l + r) / 2 + 0.5) * cell_w(st.n), TY0 + (node.bit_length() - 1) * TDY)


def _pt(st, ref):
    if isinstance(ref, int):
        return node_center(st, ref)
    if ref[0] == "cell":
        return cell_center(st, ref[1])
    return (ref[1], ref[2])


def ease(p):
    p = max(0.0, min(1.0, p))
    return p * p * (3 - 2 * p)


def wrap(d, text, fnt, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def render(st, caption, p=1.0):
    """Devuelve un Image RGB 1920x1080. p in [0,1]: progreso de la animacion del paso."""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((60, 28), st.title, font=font(54, True), fill=TXT)
    if st.tag:
        d.text((W - 60, 44), st.tag, font=font(28), fill=MUTED, anchor="ra")
    cw = cell_w(st.n)

    # ---- arreglo
    if st.show_array:
        for i, v in enumerate(st.arr):
            x0 = AL + i * cw + 6
            fill, out, tc = STY[st.arr_sty.get(i, "normal")]
            d.rounded_rectangle([x0, AY, x0 + cw - 12, AY + CELL_H], 10, fill=fill, outline=out, width=3)
            d.text((x0 + (cw - 12) / 2, AY + CELL_H / 2), str(v), font=font(40, True), fill=tc, anchor="mm")
            d.text((x0 + (cw - 12) / 2, AY + CELL_H + 12), f"i = {i}", font=font(24, mono=True), fill=MUTED, anchor="ma")
            if st.show_days:
                d.text((x0 + (cw - 12) / 2, AY + CELL_H + 44), f"día {i + 1}", font=font(24), fill=MUTED, anchor="ma")
        d.text((AL, AY - 34), "a[ ]  (ventas por día)" if st.show_days else "a[ ]", font=font(24), fill=MUTED)

    # ---- aristas
    for node in st.vis:
        for ch in (2 * node, 2 * node + 1):
            if ch in st.vis and ch in st.nodes:
                (x0, y0), (x1, y1) = node_center(st, node), node_center(st, ch)
                s = st.sty.get(ch, "normal")
                col = STY[s][1] if s != "normal" else (70, 80, 100)
                d.line([(x0, y0 + BOX_H // 2), (x1, y1 - BOX_H // 2)], fill=col, width=4 if s != "normal" else 3)

    # ---- nodos
    for node in sorted(st.vis):
        cx, cy = node_center(st, node)
        s = st.sty.get(node, "normal")
        fill, out, tc = STY[s]
        box = [cx - BOX_W / 2, cy - BOX_H / 2, cx + BOX_W / 2, cy + BOX_H / 2]
        if node == st.focus:
            g = int(10 * (1 - ease(p))) + 4
            d.rounded_rectangle([box[0] - g, box[1] - g, box[2] + g, box[3] + g], 16, outline=out, width=2)
        d.rounded_rectangle(box, 12, fill=fill, outline=out, width=4 if node == st.focus else 3)
        l, r = st.nodes[node]
        d.text((cx, cy - 22), f"t[{node}]  [{l},{r}]", font=font(22, mono=True), fill=MUTED if s in ("normal", "none") else tc, anchor="mm")
        v = st.sums.get(node)
        d.text((cx, cy + 12), "?" if v is None else str(v), font=font(40, True), fill=tc if v is not None else MUTED, anchor="mm")

    # ---- panel derecho
    if st.panel or st.legend:
        d.rounded_rectangle([PX, PY, PX + PW, 840], 14, fill=PANEL_BG)
        y = PY + 18
        for text, col, size, bold in st.panel:
            fnt = font(size, bold)
            for ln in wrap(d, text, fnt, PW - 40):
                d.text((PX + 20, y), ln, font=fnt, fill=col)
                y += int(size * 1.35)
            y += 4
        if st.legend:
            ly = 840 - 20 - 56 * len(st.legend)
            for sty_key, label in st.legend:
                fill, out, _ = STY[sty_key]
                d.rounded_rectangle([PX + 20, ly, PX + 66, ly + 40], 8, fill=fill, outline=out, width=3)
                d.text((PX + 82, ly + 20), label, font=font(24), fill=TXT, anchor="lm")
                ly += 56

    # ---- primitivas libres
    for ex in st.extras:
        kind = ex[0]
        if kind == "text":
            _, x, y, s, size, col, bold, anchor, mono = ex
            d.text((x, y), s, font=font(size, bold, mono), fill=col, anchor=anchor)
        elif kind == "rect":
            _, x0, y0, x1, y1, fill, out = ex
            d.rounded_rectangle([x0, y0, x1, y1], 14, fill=fill, outline=out, width=3)
        elif kind == "line":
            _, x0, y0, x1, y1, col, wd = ex
            d.line([(x0, y0), (x1, y1)], fill=col, width=wd)

    # ---- valores en vuelo (transiciones)
    if st.fly and p < 1.0:   # el valor en vuelo solo existe durante el movimiento
        q = ease(p * 1.15)
        for text, src, dst, col in st.fly:
            (x0, y0), (x1, y1) = _pt(st, src), _pt(st, dst)
            x, y = x0 + (x1 - x0) * q, y0 + (y1 - y0) * q
            fnt = font(34, True)
            tw = d.textlength(text, font=fnt)
            d.rounded_rectangle([x - tw / 2 - 12, y - 24, x + tw / 2 + 12, y + 24], 12, fill=(10, 12, 18), outline=col, width=3)
            d.text((x, y), text, font=fnt, fill=col, anchor="mm")

    # ---- subtitulos / texto explicativo
    if caption:
        d.rounded_rectangle([60, 868, W - 60, 1046], 16, fill=PANEL_BG)
        fnt = font(40)
        lines = wrap(d, caption, fnt, W - 160)
        size = 40
        while len(lines) > 3:
            size -= 4
            fnt = font(size)
            lines = wrap(d, caption, fnt, W - 160)
        lh = int(size * 1.3)
        y = 957 - lh * len(lines) / 2
        for ln in lines:
            d.text((90, y), ln, font=fnt, fill=TXT)
            y += lh
    return img
