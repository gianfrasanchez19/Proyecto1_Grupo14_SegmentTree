// segment_tree.hpp -- Segment Tree de sumas con actualizacion puntual por asignacion.
//
// Convenciones (todo el proyecto):
//   * Indices desde 0 y rangos INCLUSIVOS [l, r].
//   * Suma en long long (sin proteccion contra desbordamiento: se documenta como limitacion).
//   * Sin lazy propagation ni actualizaciones de rango (fuera del alcance).
//
// Este archivo contiene SOLO la logica de la estructura. El registro de eventos para la
// animacion vive en trace_recorder.hpp y se conecta mediante la interfaz Observer.
#pragma once

#include <cstddef>
#include <stdexcept>
#include <string>
#include <vector>

namespace segtree {

using value_t = long long;       // tipo de los elementos y de las sumas
using index_t = std::ptrdiff_t;  // con signo: permite detectar indices negativos

// ---------------------------------------------------------------------------
// TDA: arreglo con consultas de suma por rangos y asignacion puntual.
// Es la INTERFAZ abstracta; no dice como se guarda ni cuanto cuesta cada operacion.
// Implementaciones posibles: recorrido directo O(n)/O(1) o Segment Tree O(log n)/O(log n).
// ---------------------------------------------------------------------------
class RangeSumArray {
public:
    virtual ~RangeSumArray() = default;
    virtual std::size_t size() const = 0;
    // Suma de a[l..r] (inclusivo). Errores: ver SegmentTree::sum.
    virtual value_t sum(index_t l, index_t r) const = 0;
    // a[i] = v. Errores: ver SegmentTree::assign.
    virtual void assign(index_t i, value_t v) = 0;
};

// Tipo de solapamiento entre el intervalo de un nodo y el intervalo consultado.
enum class Overlap { None, Partial, Total };

// ---------------------------------------------------------------------------
// Observador opcional. La estructura solo llama a estos metodos; no sabe que se hace con
// ellos. Con observer == nullptr el unico coste extra es una comparacion por evento.
// Los nodos se identifican por su posicion `node` en el vector (raiz = 1, hijos 2i y 2i+1).
// ---------------------------------------------------------------------------
class Observer {
public:
    virtual ~Observer() = default;
    virtual void on_build_begin(std::size_t /*n*/) {}
    virtual void on_build_leaf(std::size_t /*node*/, index_t /*l*/, index_t /*r*/, value_t /*value*/) {}
    virtual void on_build_combine(std::size_t /*node*/, index_t /*l*/, index_t /*r*/,
                                  value_t /*left_sum*/, value_t /*right_sum*/, value_t /*sum*/) {}
    virtual void on_build_end(std::size_t /*n*/, std::size_t /*nodes_used*/) {}

    virtual void on_query_begin(index_t /*l*/, index_t /*r*/) {}
    virtual void on_query_visit(std::size_t /*node*/, index_t /*nl*/, index_t /*nr*/, Overlap /*ov*/,
                                value_t /*contribution*/, value_t /*running_total*/) {}
    virtual void on_query_end(index_t /*l*/, index_t /*r*/, value_t /*result*/, std::size_t /*visited*/) {}

    virtual void on_update_begin(index_t /*i*/, value_t /*v*/) {}
    virtual void on_update_descend(std::size_t /*node*/, index_t /*nl*/, index_t /*nr*/) {}
    virtual void on_update_leaf(std::size_t /*node*/, index_t /*i*/, value_t /*old_v*/, value_t /*new_v*/) {}
    virtual void on_update_recalc(std::size_t /*node*/, index_t /*nl*/, index_t /*nr*/,
                                  value_t /*old_sum*/, value_t /*new_sum*/) {}
    virtual void on_update_end(index_t /*i*/, value_t /*v*/, std::size_t /*touched*/) {}
};

class SegmentTree final : public RangeSumArray {
public:
    // Construccion directa desde un arreglo: O(n).
    // Arreglo vacio: PERMITIDO, produce una estructura vacia (size()==0).
    explicit SegmentTree(const std::vector<value_t>& a, Observer* obs = nullptr)
        : n_(a.size()), obs_(obs) {
        if (obs_) obs_->on_build_begin(n_);
        std::size_t used = 0;
        if (n_ > 0) {
            // Con numeracion recursiva (hijos 2i y 2i+1) el mayor indice usado es < 4n.
            // Asi el vector ocupa 4n posiciones = O(n), aunque solo se usan 2n-1 nodos.
            t_.assign(4 * n_, 0);
            build(1, 0, static_cast<index_t>(n_) - 1, a, used);
        }
        if (obs_) obs_->on_build_end(n_, used);
    }

    std::size_t size() const override { return n_; }
    bool empty() const { return n_ == 0; }

    // Suma de a[l..r], rango inclusivo. Peor caso O(log n).
    // Errores (documentados y probados):
    //   * std::out_of_range     si la estructura esta vacia, o l < 0, o r >= n.
    //   * std::invalid_argument si l > r.
    value_t sum(index_t l, index_t r) const override {
        check_range(l, r);
        if (obs_) obs_->on_query_begin(l, r);
        value_t acc = 0;
        std::size_t visited = 0;
        query(1, 0, static_cast<index_t>(n_) - 1, l, r, acc, visited);
        if (obs_) obs_->on_query_end(l, r, acc, visited);
        return acc;
    }

    // a[i] = v (asignacion, no incremento). O(log n).
    // Errores: std::out_of_range si la estructura esta vacia o i no esta en [0, n-1].
    void assign(index_t i, value_t v) override {
        if (i < 0 || static_cast<std::size_t>(i) >= n_)
            throw std::out_of_range("indice fuera de limites: " + std::to_string(i) +
                                    " (n = " + std::to_string(n_) + ")");
        if (obs_) obs_->on_update_begin(i, v);
        std::size_t touched = 0;
        update(1, 0, static_cast<index_t>(n_) - 1, i, v, touched);
        if (obs_) obs_->on_update_end(i, v, touched);
    }

    // ----- Utilidades de inspeccion (usadas por pruebas y por la exportacion de trazas) -----
    // Contenido crudo del vector (posicion 0 sin usar). No forma parte del TDA.
    const std::vector<value_t>& raw() const { return t_; }

    // Invariante: cada nodo interno guarda la suma de sus dos hijos. O(n).
    bool check_invariant() const {
        if (n_ == 0) return t_.empty();
        return check_node(1, 0, static_cast<index_t>(n_) - 1);
    }

    void set_observer(Observer* obs) { obs_ = obs; }

private:
    std::size_t n_;
    std::vector<value_t> t_;  // t_[1] = raiz; hijos de i: 2i y 2i+1. t_[i] = suma de a[l..r] del nodo
    Observer* obs_;

    void check_range(index_t l, index_t r) const {
        if (n_ == 0) throw std::out_of_range("consulta sobre estructura vacia");
        if (l < 0 || r < 0 || static_cast<std::size_t>(l) >= n_ || static_cast<std::size_t>(r) >= n_)
            throw std::out_of_range("rango fuera de limites: [" + std::to_string(l) + ", " +
                                    std::to_string(r) + "] con n = " + std::to_string(n_));
        if (l > r)
            throw std::invalid_argument("rango invalido: l > r ([" + std::to_string(l) + ", " +
                                        std::to_string(r) + "])");
    }

    // Cada nodo se calcula una sola vez -> n hojas + (n-1) combinaciones = O(n).
    void build(std::size_t node, index_t l, index_t r, const std::vector<value_t>& a, std::size_t& used) {
        ++used;
        if (l == r) {
            t_[node] = a[static_cast<std::size_t>(l)];
            if (obs_) obs_->on_build_leaf(node, l, r, t_[node]);
            return;
        }
        index_t m = l + (r - l) / 2;
        build(2 * node, l, m, a, used);
        build(2 * node + 1, m + 1, r, a, used);
        t_[node] = t_[2 * node] + t_[2 * node + 1];  // invariante: suma de los hijos
        if (obs_) obs_->on_build_combine(node, l, r, t_[2 * node], t_[2 * node + 1], t_[node]);
    }

    // Clasificacion del nodo [nl, nr] respecto de la consulta [ql, qr].
    //   None    -> no comparten posiciones: se descarta (aporta 0).
    //   Total   -> [nl, nr] contenido en [ql, qr]: se usa t_[node] completo (no se baja mas).
    //   Partial -> comparten algo pero no esta contenido: se consultan ambos hijos.
    static Overlap classify(index_t nl, index_t nr, index_t ql, index_t qr) {
        if (nr < ql || nl > qr) return Overlap::None;
        if (ql <= nl && nr <= qr) return Overlap::Total;
        return Overlap::Partial;
    }

    void query(std::size_t node, index_t nl, index_t nr, index_t ql, index_t qr,
               value_t& acc, std::size_t& visited) const {
        ++visited;
        Overlap ov = classify(nl, nr, ql, qr);
        if (ov == Overlap::Total) acc += t_[node];
        if (obs_) obs_->on_query_visit(node, nl, nr, ov, ov == Overlap::Total ? t_[node] : 0, acc);
        if (ov != Overlap::Partial) return;
        index_t m = nl + (nr - nl) / 2;
        query(2 * node, nl, m, ql, qr, acc, visited);
        query(2 * node + 1, m + 1, nr, ql, qr, acc, visited);
    }

    void update(std::size_t node, index_t nl, index_t nr, index_t i, value_t v, std::size_t& touched) {
        ++touched;
        if (obs_) obs_->on_update_descend(node, nl, nr);
        if (nl == nr) {
            value_t old_v = t_[node];
            t_[node] = v;
            if (obs_) obs_->on_update_leaf(node, i, old_v, v);
            return;
        }
        index_t m = nl + (nr - nl) / 2;
        if (i <= m) update(2 * node, nl, m, i, v, touched);
        else update(2 * node + 1, m + 1, nr, i, v, touched);
        // Al volver de la recursion se recalculan solo los antecesores de la hoja.
        value_t old_sum = t_[node];
        t_[node] = t_[2 * node] + t_[2 * node + 1];
        if (obs_) obs_->on_update_recalc(node, nl, nr, old_sum, t_[node]);
    }

    bool check_node(std::size_t node, index_t l, index_t r) const {
        if (l == r) return true;
        index_t m = l + (r - l) / 2;
        return t_[node] == t_[2 * node] + t_[2 * node + 1] &&
               check_node(2 * node, l, m) && check_node(2 * node + 1, m + 1, r);
    }
};

}  // namespace segtree
