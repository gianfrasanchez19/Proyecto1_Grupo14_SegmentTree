"""Lectura y verificacion de la traza JSON producida por cpp/demo_trace.cpp.

IMPORTANTE: este modulo NO implementa el Segment Tree. Solo reproduce los valores que la
traza ya contiene (hojas, sumas, contribuciones) y comprueba que sean coherentes entre si y
con las capturas (`snapshot`) del vector real de C++.
"""
import json
from dataclasses import dataclass, field


@dataclass
class Trace:
    initial: list
    nodes: dict = field(default_factory=dict)       # id -> (l, r)  (estructura del arbol)
    sections: dict = field(default_factory=dict)    # etiqueta de `note` -> lista de eventos
    build_events: list = field(default_factory=list)
    snapshots: dict = field(default_factory=dict)   # etiqueta -> lista (vector t)
    nodes_used: int = 0

    def depth(self, node):
        return node.bit_length() - 1   # raiz=1 -> 0; hijos 2,3 -> 1; ...

    @property
    def height(self):
        return max(self.depth(i) for i in self.nodes) + 1


def load(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["format"] == "segment-tree-trace" and data["version"] == 1
    tr = Trace(initial=data["initial"])
    label = "build"
    tr.sections[label] = []
    for ev in data["events"]:
        if ev["type"] == "note":
            label = ev["label"]
            tr.sections.setdefault(label, [])
            continue
        if ev["type"] == "snapshot":
            tr.snapshots[ev["label"]] = ev["tree"]
        tr.sections[label].append(ev)
    tr.build_events = [e for e in tr.sections["build"] if e["type"].startswith("build_")]
    for e in tr.build_events:
        if e["type"] in ("build_leaf", "build_combine"):
            tr.nodes[e["node"]] = (e["l"], e["r"])
        if e["type"] == "build_end":
            tr.nodes_used = e["nodes_used"]
    verify(tr)
    return tr


def verify(tr):
    """Comprobaciones de coherencia entre eventos y capturas reales del vector."""
    assert len(tr.nodes) == tr.nodes_used, "nodos de la traza != nodes_used"
    sums = {}
    for e in tr.build_events:
        if e["type"] == "build_leaf":
            sums[e["node"]] = e["value"]
            assert tr.nodes[e["node"]][0] == tr.nodes[e["node"]][1]
        elif e["type"] == "build_combine":
            assert sums[2 * e["node"]] == e["left_sum"] and sums[2 * e["node"] + 1] == e["right_sum"]
            assert e["left_sum"] + e["right_sum"] == e["sum"]
            sums[e["node"]] = e["sum"]
    leaves = sorted((lr[0], sums[n]) for n, lr in tr.nodes.items() if lr[0] == lr[1])
    assert [v for _, v in leaves] == tr.initial, "las hojas no coinciden con el arreglo inicial"
    check_snapshot(tr, sums, "after_build")
    # Actualizacion: aplicar los cambios que la traza declara y comparar con la captura posterior.
    for e in tr.sections["update"]:
        if e["type"] == "update_leaf":
            assert sums[e["node"]] == e["old"]
            sums[e["node"]] = e["new"]
        elif e["type"] == "update_recalc":
            assert sums[e["node"]] == e["old_sum"]
            sums[e["node"]] = e["new_sum"]
    check_snapshot(tr, sums, "after_update")
    # Consultas: las contribuciones registradas deben sumar el resultado registrado.
    for lab, evs in tr.sections.items():
        if lab.startswith("query") or lab in ("edge_single", "full_range"):
            total = sum(e["contribution"] for e in evs if e["type"] == "query_visit")
            end = [e for e in evs if e["type"] == "query_end"][0]
            assert total == end["result"], f"{lab}: contribuciones != resultado"
            assert end["visited"] == sum(1 for e in evs if e["type"] == "query_visit")


def check_snapshot(tr, sums, label):
    snap = tr.snapshots[label]
    for i, v in enumerate(snap):
        assert v == sums.get(i, 0), f"{label}: t[{i}] = {v} pero la traza reconstruye {sums.get(i, 0)}"


def section(tr, label):
    return tr.sections[label]


def query_info(tr, label):
    evs = tr.sections[label]
    begin = [e for e in evs if e["type"] == "query_begin"][0]
    end = [e for e in evs if e["type"] == "query_end"][0]
    visits = [e for e in evs if e["type"] == "query_visit"]
    return begin, visits, end
