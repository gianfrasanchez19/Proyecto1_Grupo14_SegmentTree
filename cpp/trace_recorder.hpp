// trace_recorder.hpp -- Observer que serializa los eventos de SegmentTree a JSON.
// Es independiente de la estructura: solo conoce la interfaz Observer.
// Formato documentado en README.md (seccion "Formato de la traza").
#pragma once

#include <string>
#include <vector>

#include "segment_tree.hpp"

namespace segtree {

class TraceRecorder final : public Observer {
public:
    void on_build_begin(std::size_t n) override {
        ev("build_begin", "\"n\":" + num(n));
    }
    void on_build_leaf(std::size_t node, index_t l, index_t r, value_t v) override {
        ev("build_leaf", node_fields(node, l, r) + ",\"value\":" + num(v));
    }
    void on_build_combine(std::size_t node, index_t l, index_t r, value_t ls, value_t rs, value_t s) override {
        ev("build_combine", node_fields(node, l, r) + ",\"left_sum\":" + num(ls) +
                                ",\"right_sum\":" + num(rs) + ",\"sum\":" + num(s));
    }
    void on_build_end(std::size_t n, std::size_t nodes) override {
        ev("build_end", "\"n\":" + num(n) + ",\"nodes_used\":" + num(nodes));
    }
    void on_query_begin(index_t l, index_t r) override {
        ev("query_begin", "\"l\":" + num(l) + ",\"r\":" + num(r));
    }
    void on_query_visit(std::size_t node, index_t nl, index_t nr, Overlap ov, value_t c, value_t run) override {
        ev("query_visit", node_fields(node, nl, nr) + ",\"overlap\":\"" + name(ov) +
                              "\",\"contribution\":" + num(c) + ",\"running_total\":" + num(run));
    }
    void on_query_end(index_t l, index_t r, value_t res, std::size_t visited) override {
        ev("query_end", "\"l\":" + num(l) + ",\"r\":" + num(r) + ",\"result\":" + num(res) +
                            ",\"visited\":" + num(visited));
    }
    void on_update_begin(index_t i, value_t v) override {
        ev("update_begin", "\"index\":" + num(i) + ",\"value\":" + num(v));
    }
    void on_update_descend(std::size_t node, index_t nl, index_t nr) override {
        ev("update_descend", node_fields(node, nl, nr));
    }
    void on_update_leaf(std::size_t node, index_t i, value_t old_v, value_t new_v) override {
        ev("update_leaf", "\"node\":" + num(node) + ",\"index\":" + num(i) + ",\"old\":" + num(old_v) +
                              ",\"new\":" + num(new_v));
    }
    void on_update_recalc(std::size_t node, index_t nl, index_t nr, value_t o, value_t n) override {
        ev("update_recalc", node_fields(node, nl, nr) + ",\"old_sum\":" + num(o) + ",\"new_sum\":" + num(n));
    }
    void on_update_end(index_t i, value_t v, std::size_t touched) override {
        ev("update_end", "\"index\":" + num(i) + ",\"value\":" + num(v) + ",\"nodes_touched\":" + num(touched));
    }

    // Evento fuera de la estructura: una operacion fue rechazada (el mensaje es e.what()).
    void note_error(const std::string& op, const std::string& kind, const std::string& msg) {
        ev("error", "\"op\":\"" + esc(op) + "\",\"kind\":\"" + esc(kind) + "\",\"message\":\"" + esc(msg) + "\"");
    }
    // Copia del vector de la estructura. Cuesta O(n) por captura: coste de VISUALIZACION,
    // no de la estructura. Sirve para que el animador verifique su estado reproducido.
    void snapshot(const std::string& label, const SegmentTree& t) {
        std::string s = "\"label\":\"" + esc(label) + "\",\"tree\":[";
        const auto& raw = t.raw();
        for (std::size_t i = 0; i < raw.size(); ++i) s += (i ? "," : "") + num(raw[i]);
        ev("snapshot", s + "]");
    }
    // Marca de escena para que el animador agrupe eventos (solo metadatos).
    void note(const std::string& label) { ev("note", "\"label\":\"" + esc(label) + "\""); }

    std::string to_json(const std::vector<value_t>& initial) const {
        std::string out = "{\n  \"format\": \"segment-tree-trace\",\n  \"version\": 1,\n  \"initial\": [";
        for (std::size_t i = 0; i < initial.size(); ++i) out += (i ? ", " : "") + num(initial[i]);
        out += "],\n  \"events\": [\n";
        for (std::size_t i = 0; i < events_.size(); ++i)
            out += "    " + events_[i] + (i + 1 < events_.size() ? ",\n" : "\n");
        return out + "  ]\n}\n";
    }
    std::size_t event_count() const { return events_.size(); }

private:
    std::vector<std::string> events_;

    template <class T> static std::string num(T x) { return std::to_string(x); }
    static std::string node_fields(std::size_t node, index_t l, index_t r) {
        return "\"node\":" + num(node) + ",\"l\":" + num(l) + ",\"r\":" + num(r);
    }
    static const char* name(Overlap o) {
        return o == Overlap::None ? "none" : o == Overlap::Partial ? "partial" : "total";
    }
    static std::string esc(const std::string& s) {
        std::string o;
        for (char c : s) { if (c == '"' || c == '\\') o += '\\'; o += c; }
        return o;
    }
    void ev(const std::string& type, const std::string& fields) {
        events_.push_back("{\"type\":\"" + type + "\"," + fields + "}");
    }
};

}  // namespace segtree
