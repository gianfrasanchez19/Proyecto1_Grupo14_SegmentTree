// demo_trace.cpp -- Ejecuta la demostracion del proyecto sobre el SegmentTree real y exporta
// la traza JSON. Uso: demo_trace [ruta_salida.json]
// Sin argumentos ejecuta la demostracion sin registrar eventos (observer = nullptr).
#include <fstream>
#include <iostream>
#include <vector>

#include "segment_tree.hpp"
#include "trace_recorder.hpp"

using namespace segtree;

int main(int argc, char** argv) {
    const bool tracing = argc > 1;
    const std::vector<value_t> ventas = {2, 1, 5, 3, 4, 7};  // ventas de los dias 1..6 (indices 0..5)
    TraceRecorder rec;
    Observer* obs = tracing ? &rec : nullptr;
    SegmentTree t(ventas, obs);
    if (tracing) rec.snapshot("after_build", t);

    auto q = [&](index_t l, index_t r) {
        value_t v = t.sum(l, r);
        std::cout << "sum(" << l << "," << r << ") = " << v << "\n";
    };

    rec.note("query_1");     q(1, 4);
    rec.note("update");      t.assign(2, 6); std::cout << "assign(2, 6)\n";
    if (tracing) rec.snapshot("after_update", t);
    rec.note("query_2");     q(1, 4);
    rec.note("edge_single"); q(2, 2);
    rec.note("full_range");  q(0, 5);

    // Entradas invalidas: la excepcion la lanza la estructura; aqui solo se registra el mensaje.
    rec.note("invalid");
    try { t.sum(4, 1); } catch (const std::exception& e) {
        rec.note_error("sum(4,1)", "invalid_argument", e.what());
        std::cout << "sum(4,1) -> " << e.what() << "\n";
    }
    try { t.sum(0, 6); } catch (const std::exception& e) {
        rec.note_error("sum(0,6)", "out_of_range", e.what());
        std::cout << "sum(0,6) -> " << e.what() << "\n";
    }
    // Arreglo vacio: la construccion es valida, las consultas no.
    rec.note("empty");
    SegmentTree vacio({}, obs);
    try { vacio.sum(0, 0); } catch (const std::exception& e) {
        rec.note_error("sum(0,0) sobre arreglo vacio", "out_of_range", e.what());
        std::cout << "vacio.sum(0,0) -> " << e.what() << "\n";
    }

    if (tracing) {
        std::ofstream f(argv[1], std::ios::binary);
        if (!f) { std::cerr << "no se pudo escribir " << argv[1] << "\n"; return 1; }
        f << rec.to_json(ventas);
        std::cout << "traza: " << rec.event_count() << " eventos -> " << argv[1] << "\n";
    }
    return 0;
}
