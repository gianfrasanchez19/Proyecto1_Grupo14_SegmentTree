#!/usr/bin/env python3
"""Fuente editable del informe. Genera Informe_Proyecto1_Grupo14.pdf con reportlab.
Uso (desde la raiz del proyecto): python report/build_report.py
Lee: evidence/*.png (fotogramas extraidos del MP4), evidence/salida_pruebas.txt, build/timeline.json y el MP4."""
import json
import re
import subprocess
from pathlib import Path

import imageio_ffmpeg
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Informe_Proyecto1_Grupo14.pdf"
VIDEO = ROOT / "Video_Proyecto1_Grupo14.mp4"

# ------------------------------------------------------------------ fuentes (Arial/Consolas de Windows; si no, Helvetica)
FD = Path("C:/Windows/Fonts")
try:
    pdfmetrics.registerFont(TTFont("Body", str(FD / "arial.ttf")))
    pdfmetrics.registerFont(TTFont("Body-B", str(FD / "arialbd.ttf")))
    pdfmetrics.registerFont(TTFont("Body-I", str(FD / "ariali.ttf")))
    pdfmetrics.registerFont(TTFont("Mono", str(FD / "consola.ttf")))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-B", italic="Body-I", boldItalic="Body-B")
    BODY, BOLD, MONO = "Body", "Body-B", "Mono"
except Exception:
    BODY, BOLD, MONO = "Helvetica", "Helvetica-Bold", "Courier"

s_body = ParagraphStyle("b", fontName=BODY, fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=6)
s_h1 = ParagraphStyle("h1", fontName=BOLD, fontSize=14, leading=18, spaceBefore=12, spaceAfter=6, keepWithNext=1, textColor=colors.HexColor("#123a6b"))
s_h2 = ParagraphStyle("h2", fontName=BOLD, fontSize=11, leading=14, spaceBefore=6, spaceAfter=3)
s_cap = ParagraphStyle("cap", fontName=BODY, fontSize=8.5, leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#333333"), spaceAfter=10)
s_cell = ParagraphStyle("cell", fontName=BODY, fontSize=8.5, leading=11)
s_cellb = ParagraphStyle("cellb", parent=s_cell, fontName=BOLD)
s_code = ParagraphStyle("code", fontName=MONO, fontSize=8, leading=10.5, backColor=colors.HexColor("#f2f4f7"), borderPadding=5, spaceAfter=8)
s_cov = lambda size, bold=False, sp=4: ParagraphStyle("c", fontName=BOLD if bold else BODY, fontSize=size, leading=size * 1.3, alignment=TA_CENTER, spaceAfter=sp)


def P(t, st=s_body):
    return Paragraph(t, st)


def video_duration():
    r = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(VIDEO)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    h, mi, se = int(m[1]), int(m[2]), float(m[3])
    return h * 3600 + mi * 60 + se


def mmss(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


dur = video_duration()
timeline = {t["key"]: t for t in json.loads((ROOT / "build" / "timeline.json").read_text(encoding="utf-8")) if t["key"]}
tests_log = (ROOT / "evidence" / "salida_pruebas.txt").read_text(encoding="utf-8")
n_checks = re.search(r"OK: (\d+) comprobaciones", tests_log)[1]
n_checks_fmt = f"{int(n_checks):,}".replace(",", " ")


def fig(key, caption, n):
    t = timeline[key]
    ts = t["start"] + max(0.0, t["dur"] - 0.3)
    img = Image(str(ROOT / "evidence" / f"{key}.png"), width=13.2 * cm, height=13.2 * cm * 9 / 16)
    img.hAlign = "CENTER"
    return KeepTogether([img, P(f"<b>Figura {n}.</b> {caption} <i>(Fotograma extraído del MP4 en t = {mmss(ts)}.)</i>", s_cap)])


def table(rows, widths, head=True):
    data = [[Paragraph(str(c), s_cellb if (head and i == 0) else s_cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9aa4b2")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e3e9f2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(BODY, 8.5)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(2.2 * cm, 1.2 * cm, "Grupo 14 · Segment Tree · CS2023 – UTEC 2026-2")
    canvas.drawRightString(A4[0] - 2.2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def cover_footer(canvas, doc):
    pass


S = []
# ================================================================== A. Carátula
S += [Spacer(1, 2.2 * cm),
      P("Universidad de Ingeniería y Tecnología – UTEC", s_cov(16, True, 8)),
      P("CS2023 – Algoritmos y Estructuras de Datos", s_cov(14, False, 4)),
      P("Periodo 2026-2", s_cov(12, False, 40)),
      P("Proyecto Final 1", s_cov(24, True, 10)),
      P("Segment Tree: consultas de suma por rangos<br/>y actualizaciones puntuales", s_cov(16, False, 40)),
      P("Estructura asignada: <b>Segment Tree</b>", s_cov(12, False, 4)),
      P("Grupo 14", s_cov(12, True, 30)),
      P("Integrantes", s_cov(12, True, 6)),
      P("Ormachea Mamani Gabriel", s_cov(12, False, 2)),
      P("Palomino Meza Ricardo Jesus", s_cov(12, False, 2)),
      P("Sanchez Echevarria Andre Gianfranco", s_cov(12, False, 40)),
      P("Profesor: Wilder Nina Choquehuayta", s_cov(12, False, 4)),
      PageBreak()]

# ================================================================== B. Introducción
S += [P("B. Introducción", s_h1),
      P("El objetivo de este proyecto es explicar y demostrar visualmente un Segment Tree implementado desde cero en C++, mediante un video educativo cuya "
        "animación proviene de la ejecución real del código. Como caso práctico se usan las ventas por día de un negocio: cada posición del arreglo es "
        "un día y se necesita (1) consultar el total vendido en un intervalo de días y (2) corregir el importe de un día concreto, "
        "de forma repetida. Recorrer el intervalo en cada consulta cuesta O(n); el Segment Tree reduce consultas y correcciones a O(log n)."),
      P("Se usa el ejemplo reproducible del enunciado: arreglo <font name='%s'>[2, 1, 5, 3, 4, 7]</font>; <font name='%s'>suma(1, 4) = 13</font>; asignar 6 al índice 2; "
        "arreglo <font name='%s'>[2, 1, 6, 3, 4, 7]</font>; <font name='%s'>suma(1, 4) = 14</font>; y el caso borde <font name='%s'>suma(2, 2) = 6</font>. Los resultados los calcula el programa; no están codificados. "
        "Los índices empiezan en 0 y los días en 1: el índice <i>i</i> es el día <i>i</i>+1, de modo que el intervalo de índices [1, 4] corresponde a los días 2 a 5." % ((MONO,) * 5)),
      ]

# ================================================================== C. Estructura y TDA
S += [P("C. Descripción de la estructura y del TDA", s_h1),
      P("<b>TDA.</b> El tipo de dato abstracto es un arreglo de enteros con tres operaciones: <font name='%s'>size()</font>, "
        "<font name='%s'>sum(l, r)</font> (suma de <i>a</i>[l..r], rango inclusivo) y <font name='%s'>assign(i, v)</font> (<i>a</i>[i] ← v). "
        "La interfaz solo fija <i>qué</i> hace cada operación y sus errores; no indica cómo se almacenan los datos ni cuánto cuestan. "
        "En el código es la clase abstracta <font name='%s'>RangeSumArray</font>. Una implementación ingenua guarda un vector y recorre el intervalo "
        "(<i>sum</i> en O(n), <i>assign</i> en O(1))." % ((MONO,) * 4)),
      P("<b>Implementación con Segment Tree.</b> Es un árbol binario guardado en un <font name='%s'>std::vector&lt;long long&gt;</font>. "
        "Cada nodo representa un intervalo [l, r] y guarda la suma de <i>a</i>[l..r]. La raíz (posición 1) representa [0, n−1]; un nodo en la posición <i>i</i> con intervalo [l, r] "
        "y punto medio m = l + (r−l)/2 tiene como hijos a la posición 2<i>i</i> ([l, m]) y a la 2<i>i</i>+1 ([m+1, r]). "
        "Las <b>hojas</b> son intervalos de un elemento y guardan <i>a</i>[l]; cada <b>nodo interno</b> guarda la suma de sus dos hijos (invariante que verifican las pruebas). "
        "Con n = 6 se usan 2n−1 = 11 nodos (posiciones 1 a 13 del vector; se reservan 4n para cubrir cualquier n con esta numeración)." % MONO),
      fig("estructura_arbol", "Árbol de intervalos para n = 6 antes de construir las sumas (se muestra «?»). Cada nodo indica t[i] y su intervalo [l, r]; las hojas quedan sobre su posición del arreglo.", 1)]

# ================================================================== D. Implementación y demostración
S += [P("D. Implementación y demostración", s_h1),
      P("<b>Construcción.</b> Recursión post-orden: se construyen ambos hijos y el padre guarda su suma; cada nodo se calcula una sola vez. "
        "<b>Consulta.</b> Cada nodo visitado se clasifica frente a [l, r]: <i>nulo</i> (sin posiciones comunes; aporta 0), <i>total</i> (contenido en [l, r]; se suma su valor y no se baja) "
        "o <i>parcial</i> (se visitan ambos hijos). <b>Actualización.</b> Se baja por el único camino que contiene el índice, se escribe la hoja y, al volver, se recalcula cada antecesor como suma de sus hijos. "
        "<b>Errores.</b> Un arreglo vacío es válido (<font name='%s'>size() = 0</font>); consultarlo o actualizarlo, o usar índices fuera de [0, n−1], lanza <font name='%s'>std::out_of_range</font>; "
        "un rango con l &gt; r lanza <font name='%s'>std::invalid_argument</font>." % ((MONO,) * 3)),
      fig("construccion", "Construcción terminada: la raíz t[1] guarda 22, la suma de todo el arreglo. El panel muestra el vector t (posición:suma).", 2),
      fig("query_1", "Primera consulta suma(1, 4): verde = solapamiento total, ámbar = parcial, gris = nulo. Se combinan 1 + 5 + 7 = 13 tras visitar 9 nodos.", 3),
      fig("update_hoja", "Actualización assign(2, 6): camino descendente en azul, hoja modificada en rojo (5 → 6). Después se recalculan t[2] (8 → 9) y t[1] (22 → 23).", 4),
      fig("query_2", "Segunda consulta suma(1, 4) sobre el árbol actualizado: mismo recorrido, resultado 14 (el nodo [3,4] se reutiliza sin cambios).", 5),
      fig("edge_single", "Caso borde suma(2, 2): un intervalo de una sola posición devuelve 6, el valor actualizado, visitando 5 nodos.", 6),
      P("<b>Caso borde.</b> Además de <font name='%s'>suma(2, 2)</font>, el video muestra la consulta del intervalo completo <font name='%s'>suma(0, 5) = 23</font>, que visita solo la raíz, "
        "y las entradas inválidas (<font name='%s'>suma(4, 1)</font>, <font name='%s'>suma(0, 6)</font> y una consulta sobre un arreglo vacío) con los mensajes reales de las excepciones." % ((MONO,) * 4)),
      P("<b>Cómo los eventos reales de C++ impulsan la animación.</b> <font name='%s'>SegmentTree</font> recibe un <font name='%s'>Observer*</font> opcional y lo invoca en cada paso relevante "
        "(hoja construida, nodo combinado, nodo visitado con su solapamiento, nodo del camino de actualización, nodo recalculado). La estructura no sabe qué se hace con esas llamadas; "
        "<font name='%s'>TraceRecorder</font> las serializa en <font name='%s'>trace/trace_demo.json</font>. El animador en Python lee esa traza y solo decide posiciones, colores y transiciones: "
        "las sumas, los tipos de solapamiento, las contribuciones y los conteos que se muestran se leen de los eventos y no se recalculan. "
        "Antes de animar, <font name='%s'>trace_model.py</font> comprueba que los eventos sean coherentes (por ejemplo, que reconstruyan el vector <i>t</i> capturado en C++). "
        "Las pruebas usan <font name='%s'>observer = nullptr</font>, así que no generan trazas. El formato de los eventos está documentado en el README." % ((MONO,) * 6))]

# ================================================================== E. Herramientas
S += [P("E. Herramientas y reproducción", s_h1),
      P("<b>Lenguajes y bibliotecas realmente usados:</b> C++17 (solo biblioteca estándar; <font name='%s'>std::vector</font> como almacenamiento); Python 3.14.5 con Pillow 12.3.0 (dibujo de fotogramas), "
        "numpy 2.5.3 (audio), imageio-ffmpeg 0.6.0 (ffmpeg empaquetado, codificación H.264/AAC) y reportlab 5.0.1 (este informe); compilador <font name='%s'>zig c++</font> del paquete ziglang 0.16.0 "
        "(no había g++ instalado); voz en off con System.Speech de Windows (voz «Microsoft Helena Desktop», es-ES). No se usó Manim." % ((MONO,) * 2)),
      P("Comandos exactos, desde la carpeta <font name='%s'>Proyecto1_Grupo14</font>:" % MONO),
      Preformatted(
          "pip install -r requirements.txt\n"
          "python scripts/build.py\n"
          "build/tests.exe\n"
          "build/tests_ubsan.exe\n"
          "build/demo_trace.exe trace/trace_demo.json\n"
          "python animation/render_video.py --trace trace/trace_demo.json --out Video_Proyecto1_Grupo14.mp4\n"
          "python scripts/extract_evidence.py\n"
          "python report/build_report.py", s_code),
      P("<font name='%s'>scripts/build.py</font> busca g++, clang++ o <font name='%s'>python -m ziglang c++</font> y compila con "
        "<font name='%s'>-Wall -Wextra -Wpedantic -Wshadow -Wconversion</font>. El video se renderiza a 1920×1080, 20 fps, y su duración medida es %s (%.1f s)." % (MONO, MONO, MONO, mmss(dur), dur)),
      P("<b>Pruebas ejecutadas.</b> <font name='%s'>tests.cpp</font> ejecutó %s comprobaciones, todas superadas, también con UndefinedBehaviorSanitizer: ejemplo completo, consulta de todo el arreglo y de un solo elemento, "
        "arreglo de un elemento, tamaños no potencia de dos, negativos y ceros, actualizaciones repetidas, primer y último elemento, arreglo vacío y entradas inválidas, invariante «nodo = suma de hijos», "
        "300 casos aleatorios con semilla fija comparados con una suma directa (solo en pruebas) y verificación de los eventos exportados. "
        "<b>Limitación:</b> AddressSanitizer no pudo enlazarse con <font name='%s'>zig c++</font> en Windows, por lo que no se ejecutó." % (MONO, n_checks_fmt, MONO))]

# ================================================================== F. Complejidad
S += [P("F. Complejidad", s_h1),
      P("Sea <i>n</i> el número de elementos del arreglo y <i>h</i> = techo(log2 n) + 1 la altura (número de niveles) del árbol."),
      table([
          ["Operación", "Tiempo", "Justificación"],
          ["Construcción", "O(n)", "Hay 2n−1 nodos y cada uno se calcula una vez con trabajo constante (copiar una hoja o sumar dos hijos). "
                                     "Construir con n actualizaciones costaría n·O(log n) = O(n log n)."],
          ["sum(l, r)", "O(log n) en el peor caso", "Los nodos de un mismo nivel son disjuntos y consecutivos. Solo pueden ser <i>parciales</i> el que contiene la frontera izquierda (entre l−1 y l) y el que contiene la derecha (entre r y r+1): "
                                                      "a lo sumo 2 por nivel. Los nodos totales o nulos no se expanden. Cada parcial visita 2 hijos, luego hay ≤ 4 visitas por nivel y ≤ 4h = O(log n) en total."],
          ["assign(i, v)", "O(log n)", "Recorre un único camino raíz-hoja (≤ h nodos) y hace trabajo constante en cada nodo (bajar, y al volver, recalcular una suma)."],
          ["sum(0, n−1) (todo el arreglo)", "O(1)", "La raíz tiene solapamiento total y se devuelve t[1] sin bajar. En general, cualquier consulta que coincide con un nodo desde la raíz es O(1)."],
          ["Espacio", "O(n)", "2n−1 nodos usados; el vector reserva 4n posiciones (constante 4). El TDA no necesita almacenar el arreglo aparte."],
      ], [3.6 * cm, 3.4 * cm, 9.6 * cm]),
      Spacer(1, 6),
      P("En la demostración (n = 6, h = 4) la consulta suma(1, 4) visitó 9 nodos (cota 4h = 16), la actualización tocó 3 nodos y la del intervalo completo visitó 1."),
      P("<b>Coste de la estructura frente al de la visualización.</b> Las cotas anteriores son de la estructura. Registrar eventos añade trabajo constante por evento, es decir, O(log n) eventos por consulta o actualización y O(n) durante la construcción; "
        "cada captura del vector (<font name='%s'>snapshot</font>) cuesta O(n) y la demostración toma 2; y renderizar el video cuesta proporcional al número de fotogramas (unos 6 000 a 20 fps), "
        "no a n. Por tanto no se atribuye O(log n) al proceso completo de generar el video." % MONO),
      fig("complejidad_consulta", "Nodos visitados por nivel en suma(1, 4) (1, 2, 4 y 2): como máximo dos parciales por nivel.", 7)]

# ================================================================== G. Evidencias
S += [P("G. Evidencias", s_h1),
      P("Las figuras 1 a 7 son fotogramas extraídos del MP4 final con ffmpeg (<font name='%s'>scripts/extract_evidence.py</font>). "
        "Salida real de las pruebas (<font name='%s'>evidence/salida_pruebas.txt</font>):" % (MONO, MONO)),
      Preformatted(tests_log.strip().replace("→", "->"), s_code),
      fig("invalidas", "Entradas inválidas y arreglo vacío: los mensajes son los devueltos por las excepciones del código C++ (campo <i>message</i> de la traza).", 8),
      P("El video (<font name='%s'>Video_Proyecto1_Grupo14.mp4</font>, %s) se entrega dentro de la carpeta del proyecto. No se incluye un enlace externo porque no se ha publicado ningún archivo." % (MONO, mmss(dur)))]

# ================================================================== H. Conclusiones
S += [P("H. Conclusiones", s_h1),
      P("1. <b>Equilibrio entre consultas y actualizaciones.</b> Frente a la suma directa (consulta O(n), actualización O(1)), el Segment Tree ofrece ambas en O(log n) con espacio O(n). "
        "Conviene cuando se mezclan muchas consultas de intervalos con correcciones puntuales, como en el caso de las ventas diarias; si casi no hay consultas, la suma directa es más simple."),
      P("2. <b>La cota logarítmica de la consulta depende de la clasificación de nodos.</b> No basta con que el árbol tenga altura O(log n): la demostración usa que en cada nivel hay como máximo dos nodos parciales, "
        "y que los nodos con solapamiento total se resuelven sin bajar. Verlo en el ejemplo (9 nodos visitados, 3 sumas combinadas) hizo concreta esa idea."),
      P("3. <b>Separar la estructura del registro de eventos permitió una animación fiel.</b> Con un observador opcional, el mismo código sirve para las pruebas (sin trazas) y para exportar los eventos que mueven la animación; "
        "las cifras del video salen de la ejecución y se verifican contra copias del vector."),
      P("<b>Limitaciones.</b> Suma en <font name='%s'>long long</font> sin control de desbordamiento; sin lazy propagation ni actualizaciones de rango (fuera del alcance); voz sintética disponible solo en Windows; "
        "AddressSanitizer no se pudo ejecutar." % MONO)]

# ================================================================== I. Referencias
S += [P("I. Referencias", s_h1),
      P("[1] Universidad de Ingeniería y Tecnología (UTEC). <i>Proyecto Final 1, CS2023 – Algoritmos y Estructuras de Datos, 2026-2</i>. Enunciado (PDF) del profesor Wilder Nina Choquehuayta."),
      P("[2] Video de ejemplo de un tema distinto (Suffix Tree), recibido como archivo local «WhatsApp Video 2026-09-17 at 9.37.58 AM.mp4»; autoría desconocida. "
        "Solo se observó su estilo general (fondo oscuro, leyenda de colores, texto explicativo inferior); su contenido y código no se usaron."),
      P("[3] Software utilizado: Pillow 12.3.0, numpy 2.5.3, imageio-ffmpeg 0.6.0 (ffmpeg), reportlab 5.0.1 y ziglang 0.16.0 (<font name='%s'>zig c++</font>), instalados con pip; "
        "voz System.Speech de Windows." % MONO),
      P("El algoritmo del Segment Tree corresponde al conocimiento estándar del curso; durante el desarrollo no se consultó bibliografía adicional ni se copió código de terceros. "
        "Si el grupo empleó apuntes del curso o un texto de referencia, debe añadirlo aquí.")]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2.0 * cm, bottomMargin=2.0 * cm,
                        title="Informe Proyecto 1 - Grupo 14 - Segment Tree", author="Grupo 14")
doc.build(S, onFirstPage=cover_footer, onLaterPages=footer)
print("PDF escrito:", OUT)
