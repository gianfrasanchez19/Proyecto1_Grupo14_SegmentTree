// tests.cpp -- Pruebas con aserciones propias (siguen activas aunque se compile con -DNDEBUG).
// Se ejecutan sin observador de eventos salvo la prueba de la traza: no se generan archivos.
#include <cstdio>
#include <cstdlib>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

#include "segment_tree.hpp"
#include "trace_recorder.hpp"

using namespace segtree;

static int g_checks = 0;
#define CHECK(cond)                                                                    \
    do {                                                                               \
        ++g_checks;                                                                    \
        if (!(cond)) {                                                                 \
            std::fprintf(stderr, "FALLO %s:%d: %s\n", __FILE__, __LINE__, #cond);      \
            std::exit(1);                                                              \
        }                                                                              \
    } while (0)

#define CHECK_THROWS(expr, ExType)                                                     \
    do {                                                                               \
        ++g_checks;                                                                    \
        bool ok_ = false;                                                              \
        try { (void)(expr); } catch (const ExType&) { ok_ = true; } catch (...) {}     \
        if (!ok_) {                                                                    \
            std::fprintf(stderr, "FALLO %s:%d: %s no lanzo %s\n", __FILE__, __LINE__, #expr, #ExType); \
            std::exit(1);                                                              \
        }                                                                              \
    } while (0)

// Modelo de referencia: SOLO para pruebas (suma directa sobre un vector).
static value_t ref_sum(const std::vector<value_t>& a, index_t l, index_t r) {
    value_t s = 0;
    for (index_t i = l; i <= r; ++i) s += a[static_cast<std::size_t>(i)];
    return s;
}

static void test_ejemplo_del_enunciado() {
    SegmentTree t({2, 1, 5, 3, 4, 7});
    CHECK(t.size() == 6);
    CHECK(t.check_invariant());
    CHECK(t.sum(1, 4) == 13);
    t.assign(2, 6);  // reemplaza el 5
    CHECK(t.check_invariant());
    CHECK(t.sum(1, 4) == 14);
    CHECK(t.sum(2, 2) == 6);
    CHECK(t.sum(0, 5) == 23);
}

static void test_rango_completo_y_un_elemento() {
    std::vector<value_t> a = {2, 1, 5, 3, 4, 7};
    SegmentTree t(a);
    CHECK(t.sum(0, 5) == 22);
    for (index_t i = 0; i < 6; ++i) CHECK(t.sum(i, i) == a[static_cast<std::size_t>(i)]);
}

static void test_un_elemento() {
    SegmentTree t({42});
    CHECK(t.size() == 1);
    CHECK(t.sum(0, 0) == 42);
    t.assign(0, -7);
    CHECK(t.sum(0, 0) == -7);
    CHECK(t.check_invariant());
    CHECK_THROWS(t.sum(0, 1), std::out_of_range);
}

static void test_tamanos_no_potencia_de_dos() {
    for (std::size_t n : {3u, 5u, 6u, 7u, 9u, 10u, 11u, 13u, 100u, 1000u}) {
        std::vector<value_t> a(n);
        for (std::size_t i = 0; i < n; ++i) a[i] = static_cast<value_t>(i * 3 + 1);
        SegmentTree t(a);
        index_t last = static_cast<index_t>(n) - 1;
        CHECK(t.check_invariant());
        CHECK(t.sum(0, last) == ref_sum(a, 0, last));
        CHECK(t.sum(1, last - 1) == ref_sum(a, 1, last - 1));
    }
}

static void test_negativos_y_ceros() {
    std::vector<value_t> a = {-5, 0, 3, -2, 0, 0, 9, -9};
    SegmentTree t(a);
    CHECK(t.sum(0, 7) == -4);
    CHECK(t.sum(1, 1) == 0);
    CHECK(t.sum(3, 5) == -2);
    CHECK(t.sum(6, 7) == 0);
    t.assign(0, 0);
    t.assign(7, 0);
    // Ahora el arreglo es {0, 0, 3, -2, 0, 0, 9, 0}
    CHECK(t.sum(0, 7) == 10);
    CHECK(t.sum(0, 0) == 0);
    CHECK(t.sum(7, 7) == 0);
    CHECK(t.check_invariant());
}

static void test_actualizaciones_repetidas() {
    SegmentTree t({1, 2, 3, 4, 5});
    for (value_t v : {10, -3, 0, 10, 10, 99}) {
        t.assign(2, v);
        CHECK(t.sum(2, 2) == v);
        CHECK(t.sum(0, 4) == 1 + 2 + v + 4 + 5);
        CHECK(t.check_invariant());
    }
}

static void test_primero_y_ultimo() {
    SegmentTree t({2, 1, 5, 3, 4, 7});
    t.assign(0, 100);
    CHECK(t.sum(0, 0) == 100);
    CHECK(t.sum(0, 5) == 120);
    t.assign(5, -50);
    CHECK(t.sum(5, 5) == -50);
    CHECK(t.sum(0, 5) == 63);
    CHECK(t.check_invariant());
}

static void test_vacio_y_entradas_invalidas() {
    SegmentTree v(std::vector<value_t>{});          // construir vacio es valido
    CHECK(v.size() == 0);
    CHECK(v.empty());
    CHECK(v.check_invariant());
    CHECK_THROWS(v.sum(0, 0), std::out_of_range);   // consultar vacio: out_of_range
    CHECK_THROWS(v.assign(0, 1), std::out_of_range);

    SegmentTree t({2, 1, 5, 3, 4, 7});
    CHECK_THROWS(t.sum(4, 1), std::invalid_argument);   // l > r
    CHECK_THROWS(t.sum(-1, 2), std::out_of_range);      // l negativo
    CHECK_THROWS(t.sum(0, 6), std::out_of_range);       // r >= n
    CHECK_THROWS(t.sum(6, 6), std::out_of_range);
    CHECK_THROWS(t.sum(-3, -1), std::out_of_range);
    CHECK_THROWS(t.assign(-1, 0), std::out_of_range);
    CHECK_THROWS(t.assign(6, 0), std::out_of_range);
    // Una operacion rechazada no modifica la estructura.
    CHECK(t.sum(0, 5) == 22);
    CHECK(t.check_invariant());
}

// Prueba aleatoria reproducible (semilla fija) contra el modelo de referencia.
static void test_aleatoria() {
    std::mt19937_64 rng(20262);  // semilla fija
    for (int caso = 0; caso < 300; ++caso) {
        std::size_t n = 1 + rng() % 64;
        std::vector<value_t> a(n);
        for (auto& x : a) x = static_cast<value_t>(rng() % 2001) - 1000;
        SegmentTree t(a);
        for (int op = 0; op < 200; ++op) {
            if (rng() % 2) {
                index_t i = static_cast<index_t>(rng() % n);
                value_t v = static_cast<value_t>(rng() % 2001) - 1000;
                a[static_cast<std::size_t>(i)] = v;
                t.assign(i, v);
            } else {
                index_t l = static_cast<index_t>(rng() % n), r = static_cast<index_t>(rng() % n);
                if (l > r) std::swap(l, r);
                CHECK(t.sum(l, r) == ref_sum(a, l, r));
            }
        }
        CHECK(t.check_invariant());
    }
}

// El observador no altera resultados y los eventos concuerdan con la ejecucion.
static void test_eventos() {
    TraceRecorder rec;
    SegmentTree t({2, 1, 5, 3, 4, 7}, &rec);
    CHECK(t.sum(1, 4) == 13);
    std::string json = rec.to_json({2, 1, 5, 3, 4, 7});
    CHECK(json.find("\"type\":\"query_end\",\"l\":1,\"r\":4,\"result\":13,\"visited\":9") != std::string::npos);
    CHECK(json.find("\"nodes_used\":11") != std::string::npos);  // 2n-1 nodos para n = 6
}

int main() {
    test_ejemplo_del_enunciado();
    test_rango_completo_y_un_elemento();
    test_un_elemento();
    test_tamanos_no_potencia_de_dos();
    test_negativos_y_ceros();
    test_actualizaciones_repetidas();
    test_primero_y_ultimo();
    test_vacio_y_entradas_invalidas();
    test_aleatoria();
    test_eventos();
    std::printf("OK: %d comprobaciones superadas\n", g_checks);
    return 0;
}
