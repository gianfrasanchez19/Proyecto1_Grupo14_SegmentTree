"""Guion grafico: convierte la traza de C++ en una lista de pasos (estado visual + narracion).

Cada numero que aparece en pantalla o en la voz se toma de los eventos de la traza
(sumas, contribuciones, solapamientos, nodos visitados...). Este modulo no calcula sumas.
`narr` es el texto hablado; `caption` es el texto en pantalla (puede usar notacion O(...)).
"""
import copy
from dataclasses import dataclass

import trace_model as tm
from scene_draw import State, TXT, MUTED, PANEL_BG

GREEN, AMBER, BLUE = (62, 208, 124), (247, 182, 52), (92, 162, 255)
CORAL, PURPLE, CYAN, GRAY = (255, 108, 108), (184, 134, 255), (72, 204, 214), (128, 134, 146)
ACC_PT = ("pt", 1630, 345)
OV_COLOR = {"none": GRAY, "partial": AMBER, "total": GREEN}


@dataclass
class Step:
    state: State
    narr: str
    caption: str
    dur: float
    key: str


class TL:
    def __init__(self, tr):
        self.tr = tr
        self.st = State(n=len(tr.initial), nodes=dict(tr.nodes), arr=list(tr.initial))
        self.steps = []

    def step(self, narr=None, caption=None, dur=2.0, key=None, fly=None, focus=None):
        s = copy.deepcopy(self.st)
        s.fly, s.focus = fly or [], focus
        self.steps.append(Step(s, narr, caption if caption is not None else narr, dur, key))


def P(text, col=TXT, size=28, bold=False):
    return (text, col, size, bold)


def T(x, y, s, size=32, col=TXT, bold=False, anchor="la", mono=False):
    return ("text", x, y, s, size, col, bold, anchor, mono)


def R(x0, y0, x1, y1, fill=PANEL_BG, out=(70, 80, 100)):
    return ("rect", x0, y0, x1, y1, fill, out)


def nodo(l, r):
    return f"la hoja {l}" if l == r else f"el nodo de {l} a {r}"


def build_storyboard(tr):
    tl = TL(tr)
    st, n = tl.st, len(tr.initial)
    depth_of = tr.depth
    all_nodes = set(tr.nodes)
    sec = tr.sections

    # ------------------------------------------------------------------ 0. portada
    st.extras = [
        T(960, 250, "Segment Tree", 120, TXT, True, "ma"),
        T(960, 415, "Sumas por intervalos y actualizaciones puntuales", 46, MUTED, anchor="ma"),
        T(960, 560, "Grupo 14", 44, BLUE, True, "ma"),
        T(960, 630, "Ormachea Mamani Gabriel · Palomino Meza Ricardo Jesus", 34, TXT, anchor="ma"),
        T(960, 678, "Sanchez Echevarria Andre Gianfranco", 34, TXT, anchor="ma"),
        T(960, 780, "CS2023 – Algoritmos y Estructuras de Datos · UTEC · 2026-2", 30, MUTED, anchor="ma"),
    ]
    tl.step("Hola, somos el grupo catorce. Vamos a explicar el Segment Tree, una estructura para "
            "responder sumas de intervalos sin recorrer todo el arreglo.",
            caption="", dur=4, key="portada")

    # ------------------------------------------------------------------ 1. problema
    st.extras = []
    st.title, st.tag = "1 · El problema: ventas por intervalos", "Problema"
    st.show_array = st.show_days = True
    tl.step("Estas son las ventas de seis días. Los índices empiezan en cero: el día uno está en el índice cero.", dur=3, key="problema")
    for i in range(1, 5):
        st.arr_sty[i] = "inrange"
    st.panel = [P("Pregunta 1", MUTED, 24), P("¿Cuánto se vendió entre el día 2 y el día 5?", TXT, 30, True),
                P("Índices 1 a 4, rango inclusivo [l, r].", AMBER, 26)]
    st.extras = [R(100, 400, 1300, 830),
                 T(140, 430, "Suma directa (sin estructura):", 32, MUTED),
                 T(140, 490, "total = 0", 34, TXT, True, mono=True),
                 T(140, 540, "for i in l..r:  total += a[i]", 34, TXT, True, mono=True),
                 T(140, 640, "Una consulta recorre el intervalo: O(n).", 34, AMBER, True),
                 T(140, 700, "Con miles de consultas sobre miles de días,", 28, MUTED),
                 T(140, 740, "repetir ese recorrido cada vez es costoso.", 28, MUTED)]
    tl.step("Queremos el total entre el día dos y el día cinco: índices uno a cuatro, rango inclusivo. "
            "Sumarlos uno a uno cuesta O de n.",
            caption="Queremos el total entre el día 2 y el día 5: índices 1 a 4 (rango inclusivo). "
                    "Sumar directamente recorre el intervalo: O(n).", dur=3)
    st.arr_sty = {2: "leafmod"}
    st.panel = [P("Pregunta 2", MUTED, 24), P("Hay que corregir el importe de un día concreto.", TXT, 30, True),
                P("Ejemplo: cambiar el índice 2 (día 3).", CORAL, 26)]
    st.extras = [R(100, 400, 1300, 830),
                 T(140, 430, "Corrección de un día:", 32, MUTED),
                 T(140, 490, "a[2] = 6", 34, CORAL, True, mono=True),
                 T(140, 590, "Queremos que consultas y correcciones", 32, TXT),
                 T(140, 640, "se puedan mezclar sin recorrer el arreglo.", 32, TXT),
                 T(140, 720, "Solución: una estructura que guarde sumas parciales.", 30, GREEN, True)]
    tl.step("Además hay que corregir el importe de un día. Con muchas consultas, sumar desde cero cada vez es lento.", dur=3)

    # ------------------------------------------------------------------ 2. TDA
    st.extras = []
    st.title, st.tag = "2 · Qué es y qué TDA representa", "TDA"
    st.show_array, st.arr_sty, st.panel = False, {}, []
    st.extras = [
        R(80, 150, 930, 820), R(990, 150, 1840, 820),
        T(505, 175, "TDA: arreglo con sumas por rango", 34, BLUE, True, "ma"),
        T(1415, 175, "Implementación: Segment Tree", 34, GREEN, True, "ma"),
    ]
    tl.step(caption="", dur=0.6)
    st.extras += [
        T(120, 250, "size()", 32, TXT, True, mono=True), T(120, 292, "número de elementos", 26, MUTED),
        T(120, 370, "sum(l, r)", 32, TXT, True, mono=True), T(120, 412, "suma de a[l..r], rango inclusivo", 26, MUTED),
        T(120, 490, "assign(i, v)", 32, TXT, True, mono=True), T(120, 532, "a[i] = v (asignación puntual)", 26, MUTED),
        T(120, 640, "La interfaz define QUÉ se puede hacer,", 26, AMBER), T(120, 676, "no cómo se guarda ni cuánto cuesta.", 26, AMBER),
    ]
    tl.step("El tipo de dato abstracto es un arreglo con tres operaciones: tamaño, suma de un rango inclusivo y "
            "asignación en una posición. No dice cómo se guarda ni cuánto cuesta.",
            caption="TDA: arreglo con tres operaciones. La interfaz no dice cómo se guarda ni cuánto cuesta.", dur=3, key="tda")
    st.extras += [
        T(1030, 250, "Árbol binario guardado en un vector", 30, TXT, True),
        T(1030, 300, "t[1] = raíz;  hijos de t[i]: t[2i] y t[2i+1]", 28, TXT, mono=True),
        T(1030, 372, "Cada nodo guarda la suma de un intervalo", 28, MUTED),
        T(1030, 470, "Construcción", 28, MUTED), T(1500, 470, "O(n)", 32, GREEN, True, mono=True),
        T(1030, 530, "sum(l, r)", 28, MUTED, mono=True), T(1500, 530, "O(log n)", 32, GREEN, True, mono=True),
        T(1030, 590, "assign(i, v)", 28, MUTED, mono=True), T(1500, 590, "O(log n)", 32, GREEN, True, mono=True),
        T(1030, 700, "Alternativa simple: recorrer el arreglo", 26, MUTED), T(1030, 736, "sum O(n), assign O(1).", 26, MUTED),
    ]
    tl.step("El Segment Tree la implementa con un árbol binario en un vector: raíz en la posición uno, "
            "hijos de i en 2i y 2i más uno. Cada nodo guarda la suma de un intervalo.",
            caption="Segment Tree: árbol binario en un vector. Raíz t[1]; hijos de t[i]: t[2i] y t[2i+1]. "
                    "Cada nodo guarda la suma de un intervalo.", dur=3)

    # ------------------------------------------------------------------ 3. arreglo <-> arbol
    st.extras = []
    st.title, st.tag = "3 · Relación entre el arreglo y el árbol", "Estructura"
    st.show_array, st.show_days = True, False
    st.vis = {1}
    st.sums = {i: None for i in all_nodes}
    st.panel = [P("Cada nodo muestra", MUTED, 24), P("t[i]  [l, r]", TXT, 30, True), P("y la suma de a[l..r]", TXT, 26)]
    tl.step(f"La raíz representa todo el arreglo, del cero al {n - 1}.", dur=2.5, focus=1, key="estructura_raiz")
    st.vis |= {i for i in all_nodes if depth_of(i) <= 1}
    st.panel = [P("Hijos de t[i]:", MUTED, 24), P("t[2i]  mitad izquierda", TXT, 28), P("t[2i+1]  mitad derecha", TXT, 28),
                P("Ejemplo: t[1] → t[2] y t[3]", AMBER, 26)]
    tl.step("Cada nodo se divide por la mitad: sus hijos cubren la mitad izquierda y la derecha.", dur=2.5)
    st.vis = set(all_nodes)
    leaves = sorted((tr.nodes[i][0], i) for i in all_nodes if tr.nodes[i][0] == tr.nodes[i][1])
    st.panel = [P(f"Elementos: n = {n}", TXT, 30, True), P(f"Nodos usados: {tr.nodes_used}", TXT, 30, True),
                P("Las hojas son los intervalos de un solo elemento.", MUTED, 26)]
    tl.step(f"Así llegamos a las hojas. El árbol usa {tr.nodes_used} nodos para {n} elementos; n no tiene que ser potencia de dos.", dur=3, key="estructura_arbol")
    leaf_i, leaf_node = leaves[2]
    st.arr_sty[leaf_i], st.sty[leaf_node] = "built", "built"
    st.panel = [P(f"Índice {leaf_i}  ↔  hoja t[{leaf_node}]", CYAN, 32, True), P("Cada hoja corresponde a una posición del arreglo.", MUTED, 26)]
    tl.step(f"La hoja del índice {leaf_i} vive en la posición {leaf_node} del vector.",
            fly=[(str(tr.initial[leaf_i]), ("cell", leaf_i), leaf_node, CYAN)], dur=2.5, focus=leaf_node)
    st.arr_sty, st.sty = {}, {}

    # ------------------------------------------------------------------ 4. construccion
    st.title, st.tag = "4 · Construcción desde las hojas", "Construcción"
    sums = {}
    st.panel = [P("Regla:", MUTED, 24), P("t[i] = t[2i] + t[2i+1]", TXT, 30, True), P("Cada nodo se calcula una sola vez.", MUTED, 26)]
    tl.step("Construimos de abajo hacia arriba: primero las hojas, y cada padre suma a sus dos hijos.", dur=3)
    first_leaf = first_comb = True
    n_comb = 0
    for e in tr.build_events:
        if e["type"] == "build_leaf":
            i, node = e["l"], e["node"]
            sums[node] = e["value"]
            st.sums[node], st.sty[node], st.arr_sty[i] = e["value"], "built", "built"
            txt = f"Hoja {i}: copiamos el valor {e['value']} del arreglo."
            st.panel = [P("Regla:", MUTED, 24), P("t[i] = t[2i] + t[2i+1]", TXT, 30, True),
                        P(f"t[{node}] = a[{i}] = {e['value']}", CYAN, 30, True)]
            tl.step(None, caption=txt, fly=[(str(e["value"]), ("cell", i), node, CYAN)], focus=node, dur=1.5)
        elif e["type"] == "build_combine":
            node, l, r = e["node"], e["l"], e["r"]
            n_comb += 1
            sums[node] = e["sum"]
            st.sums[node], st.sty[node] = e["sum"], "built"
            st.panel = [P("Regla:", MUTED, 24), P("t[i] = t[2i] + t[2i+1]", TXT, 30, True),
                        P(f"t[{node}] = {e['left_sum']} + {e['right_sum']} = {e['sum']}", CYAN, 30, True)]
            txt = (f"El padre guarda la suma de sus hijos: {e['left_sum']} más {e['right_sum']} es {e['sum']}."
                   if first_comb else f"{e['left_sum']} más {e['right_sum']} es {e['sum']}.")
            first_comb = False
            tl.step(txt, fly=[(str(e["left_sum"]), 2 * node, node, CYAN), (str(e["right_sum"]), 2 * node + 1, node, CYAN)],
                    focus=node, dur=1.6)
    st.sty, st.arr_sty = {}, {}
    used_ids = max(tr.nodes)
    vec = "  ".join(f"{i}:{sums[i]}" if i in sums else f"{i}:·" for i in range(1, used_ids + 1))
    st.panel = [P("Vector t (posición:suma)", MUTED, 24), P(vec, TXT, 26, False),
                P(f"Raíz t[1] = {sums[1]}: suma total.", GREEN, 28, True)]
    tl.step(f"La raíz guarda la suma total: {sums[1]}. Cada nodo se calculó una vez: {len(leaves)} hojas y {n_comb} combinaciones. "
            f"Construir cuesta O de n.",
            caption=f"Raíz = {sums[1]}. Cada nodo se calculó una vez: {len(leaves)} hojas + {n_comb} combinaciones → O(n).",
            dur=4, key="construccion")

    # ------------------------------------------------------------------ helpers de consulta
    def run_query(label, tag_title, intro, quiet=False, final_extra=""):
        begin, visits, end = tm.query_info(tr, label)
        ql, qr = begin["l"], begin["r"]
        st.title, st.tag = tag_title, "Consulta"
        st.sty, st.arr_sty = {}, {}
        for i in range(ql, qr + 1):
            st.arr_sty[i] = "inrange"
        st.legend = [("total", "Total: se usa la suma"), ("partial", "Parcial: se baja a los hijos"), ("none", "Nulo: se descarta")]
        contribs = []

        def panel(run):
            expr = " + ".join(str(c) for c in contribs) if contribs else "—"
            st.panel = [P("Consulta", MUTED, 24), P(f"sum({ql}, {qr})", TXT, 44, True), P(f"Días {ql + 1} a {qr + 1}", MUTED, 26),
                        P("Acumulado", MUTED, 24), P(expr, GREEN, 32, True), P(f"= {run}", GREEN, 32, True)]
        panel(0)
        tl.step(intro[0], caption=intro[1] if len(intro) > 1 else None, dur=3.5 if not quiet else 2.5, focus=1)
        seen = set()
        for v in visits:
            node, l, r, ov = v["node"], v["l"], v["r"], v["overlap"]
            st.sty[node] = ov
            fly = []
            if ov == "total":
                contribs.append(v["contribution"])
                for i in range(l, r + 1):
                    st.arr_sty[i] = "total"
                fly = [(f"+{v['contribution']}", node, ACC_PT, GREEN)]
            panel(v["running_total"])
            long_ = ov not in seen and not quiet
            seen.add(ov)
            if ov == "partial":
                txt = (f"{nodo(l, r).capitalize()}: solapamiento parcial. Comparte posiciones pero no está contenido; bajamos a los hijos."
                       if long_ else f"{nodo(l, r).capitalize()}: parcial, bajamos.")
            elif ov == "none":
                txt = (f"{nodo(l, r).capitalize()}: sin solapamiento. Se descarta."
                       if long_ else f"{nodo(l, r).capitalize()}: nulo, se descarta.")
            else:
                txt = (f"{nodo(l, r).capitalize()}: solapamiento total. Usamos su suma, {v['contribution']}, sin bajar más."
                       if long_ else f"{nodo(l, r).capitalize()}: total, sumamos {v['contribution']}.")
            if quiet:
                tl.step(None, caption=txt, fly=fly, focus=node, dur=1.7)
            else:
                tl.step(txt, fly=fly, focus=node, dur=1.8)
        n_tot = sum(1 for v in visits if v["overlap"] == "total")
        tl.step(f"Resultado: {end['result']}. Visitamos {end['visited']} {'nodo' if end['visited'] == 1 else 'nodos'} y combinamos "
                f"{n_tot} {'suma ya calculada' if n_tot == 1 else 'sumas ya calculadas'}." + final_extra,
                dur=3.0, key=label)
        return end

    # ------------------------------------------------------------------ 5. consulta 1
    end1 = run_query("query_1", "5 · Primera consulta de rango",
                     ("Primera consulta: suma de 1 a 4. Cada nodo se clasifica frente al intervalo como solapamiento total, parcial o nulo. "
                      "La leyenda está a la derecha.",
                      "Consulta sum(1, 4): cada nodo se clasifica como solapamiento total, parcial o nulo."))

    # ------------------------------------------------------------------ 6. actualizacion
    upd = sec["update"]
    ub = [e for e in upd if e["type"] == "update_begin"][0]
    ul = [e for e in upd if e["type"] == "update_leaf"][0]
    ue = [e for e in upd if e["type"] == "update_end"][0]
    idx, newv, oldv = ub["index"], ub["value"], ul["old"]
    st.title, st.tag = "6 · Actualización puntual", "Actualización"
    st.sty, st.arr_sty = {}, {idx: "leafmod"}
    st.legend = [("path", "Camino descendente"), ("leafmod", "Hoja modificada"), ("recalc", "Antecesor recalculado")]
    route = []

    def upanel(extra=None):
        st.panel = [P("Actualización", MUTED, 24), P(f"assign({idx}, {newv})", TXT, 44, True), P(f"Día {idx + 1}: {oldv} → {newv}", CORAL, 28)]
        if route:
            st.panel += [P("Ruta", MUTED, 24), P(" → ".join(f"t[{x}]" for x in route), BLUE, 28, True)]
        if extra:
            st.panel += [P(extra, PURPLE, 28, True)]
    upanel()
    tl.step(f"Corregimos el día {idx + 1}: asignamos {newv} al índice {idx}, en lugar de {oldv}. Bajamos hasta esa hoja.", dur=3.5, key="update_inicio")
    for e in upd:
        if e["type"] == "update_descend":
            st.sty[e["node"]] = "path"
            route.append(e["node"])
            upanel()
            tl.step(f"Bajamos por {nodo(e['l'], e['r'])}.", focus=e["node"], dur=2.0)
        elif e["type"] == "update_leaf":
            st.sty[e["node"]] = "leafmod"
            st.sums[e["node"]] = e["new"]
            st.arr[e["index"]] = e["new"]
            upanel(f"t[{e['node']}]: {e['old']} → {e['new']}")
            tl.step(f"La hoja {e['index']} cambia de {e['old']} a {e['new']}.",
                    fly=[(str(e["new"]), e["node"], ("cell", e["index"]), CORAL)], focus=e["node"], dur=3, key="update_hoja")
        elif e["type"] == "update_recalc":
            node = e["node"]
            st.sty[node] = "recalc"
            st.sums[node] = e["new_sum"]
            upanel(f"t[{node}]: {e['old_sum']} → {e['new_sum']}")
            tl.step(f"Recalculamos {nodo(e['l'], e['r'])}: de {e['old_sum']} a {e['new_sum']}.",
                    fly=[(str(st.sums[2 * node]), 2 * node, node, PURPLE), (str(st.sums[2 * node + 1]), 2 * node + 1, node, PURPLE)],
                    focus=node, dur=3)
    tl.step(f"Solo tocamos {ue['nodes_touched']} nodos: un camino de la raíz a la hoja. La actualización cuesta O de log n.",
            caption=f"Solo se tocaron {ue['nodes_touched']} nodos (un camino raíz-hoja): actualización en O(log n).", dur=4, key="update_fin")

    # ------------------------------------------------------------------ 7. consulta 2
    st.legend = []
    run_query("query_2", "7 · Segunda consulta: comprobar el resultado",
              (f"Repetimos la consulta de {tm.query_info(tr, 'query_2')[0]['l']} a {tm.query_info(tr, 'query_2')[0]['r']} en el árbol actualizado.",
               "Repetimos sum(1, 4) sobre el árbol actualizado."), quiet=True,
              final_extra=" El nodo de 3 a 4 no cambió y se reutilizó.")

    # ------------------------------------------------------------------ 8. casos borde
    st.tag = "Caso borde"
    run_query("edge_single", "8 · Caso borde: un solo elemento",
              ("Caso borde: un solo elemento, suma de 2 a 2.",
               "Caso borde: sum(2, 2), un intervalo de una sola posición."))
    fb, fv, fe = tm.query_info(tr, "full_range")
    st.sty, st.arr_sty = {}, {}
    run_query("full_range", "8 · Otro extremo: todo el arreglo",
              (f"Ahora todo el arreglo, de {fb['l']} a {fb['r']}: la raíz ya tiene la suma.",
               f"sum({fb['l']}, {fb['r']}): la raíz cubre todo el intervalo."), quiet=True,
              final_extra=" Es O de uno.")
    # entradas invalidas
    errs = [e for e in sec["invalid"] + sec["empty"] if e["type"] == "error"]
    st.title, st.tag = "8 · Entradas inválidas y arreglo vacío", "Caso borde"
    st.show_array, st.vis, st.panel, st.legend, st.sty = False, set(), [], [], {}
    ex = [R(80, 150, 1840, 820)]
    y = 190
    for e in errs:
        ex += [T(120, y, e["op"], 32, AMBER, True, mono=True), T(120, y + 46, f"{e['kind']}: {e['message']}", 28, TXT, mono=True)]
        y += 130
    ex += [T(120, y + 10, "La construcción con arreglo vacío es válida; consultarlo lanza una excepción.", 28, MUTED)]
    st.extras = ex
    tl.step("Las entradas inválidas, como l mayor que r, un rango fuera de límites o un arreglo vacío, lanzan una excepción "
            "con mensaje claro y no modifican los datos.",
            caption="Las entradas inválidas lanzan excepciones (mensajes reales de la ejecución en C++). La estructura no se modifica.",
            dur=4, key="invalidas")

    # ------------------------------------------------------------------ 9. complejidad
    _, v2, e2 = tm.query_info(tr, "query_2")
    per_level = {}
    for v in v2:
        per_level[depth_of(v["node"])] = per_level.get(depth_of(v["node"]), 0) + 1
    h = tr.height
    st.title, st.tag = "9 · Complejidad", "Complejidad"
    st.extras = []
    st.show_array, st.vis = True, set(all_nodes)
    st.arr_sty = {}
    st.sty = {v["node"]: v["overlap"] for v in v2}
    st.legend = [("total", "Total"), ("partial", "Parcial (máx. 2 por nivel)"), ("none", "Nulo")]
    st.panel = [P("Nodos visitados por nivel", MUTED, 24)] + [P(f"nivel {d}: {per_level.get(d, 0)} " + ("nodo" if per_level.get(d, 0) == 1 else "nodos"), TXT, 28, True) for d in range(h)] + \
               [P(f"Altura: {h} niveles", MUTED, 26)]
    st.sums = {i: tr.snapshots["after_update"][i] for i in all_nodes}
    tl.step(f"En una consulta hay como máximo dos nodos parciales por nivel: los que contienen un extremo. Los demás no se expanden. "
            f"Son a lo sumo cuatro visitas por nivel, y hay {h} niveles: O de log n en el peor caso.",
            caption=f"Consulta: máx. 2 nodos parciales por nivel → ≤ 4 visitas por nivel × {h} niveles = O(log n). Aquí: {e2['visited']} nodos.",
            dur=5, key="complejidad_consulta")
    st.legend, st.arr_sty = [], {}
    st.show_array, st.vis = False, set()
    st.sty = {}
    st.panel = []
    st.extras = [
        R(80, 150, 1840, 820),
        T(120, 175, "Operación", 30, MUTED, True), T(760, 175, "Tiempo", 30, MUTED, True), T(1060, 175, "Por qué", 30, MUTED, True),
        ("line", 100, 225, 1820, 225, (70, 80, 100), 2),
        T(120, 250, "Construcción", 32, TXT, True), T(760, 250, "O(n)", 32, GREEN, True, mono=True),
        T(1060, 254, "Cada nodo se calcula una vez: 2n−1 nodos", 26, TXT),
        T(120, 340, "Consulta sum(l, r)", 32, TXT, True), T(760, 340, "O(log n)", 32, GREEN, True, mono=True),
        T(1060, 344, "≤ 4 visitas por nivel, log n niveles", 26, TXT),
        T(120, 430, "Actualización assign", 32, TXT, True), T(760, 430, "O(log n)", 32, GREEN, True, mono=True),
        T(1060, 434, "Un camino raíz-hoja, trabajo constante por nodo", 26, TXT),
        T(120, 520, "Consulta de todo el arreglo", 32, TXT, True), T(760, 520, "O(1)", 32, GREEN, True, mono=True),
        T(1060, 524, "La raíz ya guarda la suma", 26, TXT),
        T(120, 610, "Espacio", 32, TXT, True), T(760, 610, "O(n)", 32, GREEN, True, mono=True),
        T(1060, 614, f"{tr.nodes_used} nodos usados (2n−1); vector de 4n posiciones", 26, TXT),
        T(120, 720, "n = número de elementos del arreglo.  Aparte: exportar la traza y renderizar el video son costes de visualización.", 24, MUTED),
    ]
    tl.step("La construcción es O de n: cada nodo se calcula una vez, dos n menos uno nodos; con n actualizaciones sería O de n log n. "
            "La actualización recorre un solo camino: O de log n. El intervalo completo es O de uno. El espacio es O de n.",
            caption="", dur=6, key="complejidad_tabla")
    st.extras += [T(120, 770, "Exportar eventos, guardar capturas del vector (O(n) cada una) y renderizar NO forman parte de estas cotas.", 24, AMBER)]
    tl.step("Exportar eventos, guardar capturas y renderizar son costes de la visualización, no de la estructura.", caption="", dur=3)

    # ------------------------------------------------------------------ 10. conclusiones
    st.title, st.tag = "10 · Conclusiones", "Conclusiones"
    st.vis, st.show_array, st.panel, st.legend = set(), False, [], []
    st.extras = [
        R(80, 150, 930, 820), R(990, 150, 1840, 820),
        T(505, 175, "Suma directa", 36, MUTED, True, "ma"), T(1415, 175, "Segment Tree", 36, GREEN, True, "ma"),
        T(120, 260, "sum(l, r):  O(n)", 32, TXT, mono=True), T(120, 330, "assign(i, v):  O(1)", 32, TXT, mono=True),
        T(120, 400, "Espacio extra: ninguno", 30, MUTED), T(120, 520, "Bien si casi no hay consultas.", 28, MUTED),
        T(1030, 260, "sum(l, r):  O(log n)", 32, TXT, mono=True), T(1030, 330, "assign(i, v):  O(log n)", 32, TXT, mono=True),
        T(1030, 400, "Espacio: O(n)", 30, MUTED), T(1030, 520, "Conviene con muchas consultas", 28, GREEN),
        T(1030, 560, "y actualizaciones mezcladas.", 28, GREEN),
        T(1030, 680, "Límites: sumas en long long sin control", 26, MUTED), T(1030, 716, "de desbordamiento; sin lazy propagation.", 26, MUTED),
    ]
    tl.step("Conclusiones. El Segment Tree ofrece consultas y actualizaciones en O de log n, frente a O de n y O de uno de la suma directa: "
            "conviene cuando se mezclan ambas. Y todo lo mostrado salió de la implementación real en C++, no de una simulación. Gracias.",
            caption="El Segment Tree equilibra consultas y actualizaciones en O(log n). Todo lo mostrado salió de la ejecución real en C++.",
            dur=8, key="conclusiones")
    return tl.steps
