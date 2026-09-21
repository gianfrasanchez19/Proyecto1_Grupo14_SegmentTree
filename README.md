# Proyecto Final 1 – Segment Tree (Grupo 14)

Universidad de Ingeniería y Tecnología – UTEC · CS2023 – Algoritmos y Estructuras de Datos · 2026-2
Profesor: Wilder Nina Choquehuayta · Integrantes: Ormachea Mamani Gabriel, Palomino Meza Ricardo Jesus, Sanchez Echevarria Andre Gianfranco.

Video educativo (~5 min) sobre un **Segment Tree de sumas** implementado desde cero en C++, con una animación
generada a partir de los eventos que emite la ejecución real del código.

## 1. Organización de los archivos

```
Proyecto1_Grupo14/
├── cpp/
│   ├── segment_tree.hpp     Estructura (TDA RangeSumArray + SegmentTree + interfaz Observer). Sin nada de animación.
│   ├── trace_recorder.hpp   Observer que serializa los eventos a JSON (registro de eventos, separado de la estructura).
│   ├── demo_trace.cpp       Ejecuta el ejemplo del enunciado y exporta la traza.
│   └── tests.cpp            Pruebas con aserciones (sin observador: no generan trazas).
├── animation/
│   ├── trace_model.py       Lee la traza y comprueba su coherencia (NO implementa el árbol).
│   ├── storyboard.py        Convierte eventos en pasos de animación + texto/voz.
│   ├── scene_draw.py        Dibuja cada fotograma (Pillow): posiciones, colores, transiciones.
│   ├── render_video.py      Voz + fotogramas + ffmpeg -> MP4.
│   └── tts.ps1              Voz en off con System.Speech de Windows (voz «Microsoft Helena Desktop», es-ES).
├── scripts/
│   ├── build.py             Compila pruebas y demo con advertencias (g++, clang++ o `zig c++`).
│   └── extract_evidence.py  Extrae del MP4 los fotogramas usados como evidencias.
├── report/build_report.py   Fuente editable del informe (reportlab) -> Informe_Proyecto1_Grupo14.pdf
├── trace/trace_demo.json    Traza de la demostración, generada por el ejecutable de C++.
├── evidence/                Capturas extraídas del MP4 y salida real de las pruebas.
├── Video_Proyecto1_Grupo14.mp4
├── Informe_Proyecto1_Grupo14.pdf
├── Guion_Exposicion_Grupo14.md
├── requirements.txt · Makefile (alternativa con g++) · .gitignore
```

## 2. Requisitos

| Componente | Uso | Versión con la que se ejecutó |
|---|---|---|
| Compilador C++17 (g++/clang++) **o** paquete pip `ziglang` | compilar | `zig c++` de ziglang 0.16.0 (no había g++ instalado) |
| Python 3 | animación, informe | 3.14.5 |
| Pillow, numpy, imageio-ffmpeg, reportlab | fotogramas, audio, ffmpeg empaquetado, PDF | ver `pip list` (instaladas con `pip install -r requirements.txt`) |
| Windows con voz «Microsoft Helena Desktop» | voz en off | Windows 11; en otros sistemas el video se genera sin voz (solo texto) |

No se usó Manim (no estaba instalado ni sus dependencias, LaTeX/Cairo). El enunciado permite otra herramienta siempre que la
animación provenga de la ejecución real; aquí se dibuja con Pillow y se codifica con ffmpeg.

## 3. Cómo reproducir todo (desde la carpeta `Proyecto1_Grupo14`)

```bash
pip install -r requirements.txt
python scripts/build.py                                  # compila tests y demo con -Wall -Wextra -Wpedantic -Wshadow -Wconversion
build/tests.exe                                          # pruebas (en Linux/macOS: build/tests)
build/tests_ubsan.exe                                    # las mismas con UndefinedBehaviorSanitizer
build/demo_trace.exe                                     # demo SIN traza (imprime resultados)
build/demo_trace.exe trace/trace_demo.json               # demo + traza JSON
python animation/render_video.py --trace trace/trace_demo.json --out Video_Proyecto1_Grupo14.mp4
python scripts/extract_evidence.py                       # fotogramas del MP4 -> evidence/
python report/build_report.py                            # informe PDF
```

Con g++ también sirve `make test` y `make trace`. Con `--no-video` el renderizador solo valida la traza y calcula
duraciones; con `--frames DIR` (junto a `--no-video`) guarda una imagen por paso para revisarlos.

## 4. Explicación del código

**Interfaz vs. implementación.** `RangeSumArray` es el TDA: `size()`, `sum(l, r)` y `assign(i, v)`. No dice cómo se guardan los datos ni
cuánto cuesta cada operación (una implementación posible es recorrer un vector: `sum` O(n), `assign` O(1)). `SegmentTree` es *una* implementación.

**Representación.** Árbol binario en `std::vector<long long> t_`. La raíz es `t_[1]` y representa `[0, n-1]`; el nodo `i` con intervalo `[l, r]`
y punto medio `m = l + (r-l)/2` tiene hijos `2i` → `[l, m]` y `2i+1` → `[m+1, r]`. Una hoja guarda `a[l]`; un nodo interno guarda la suma de sus dos hijos
(**invariante**, comprobada por `check_invariant()`). Se usan `2n-1` nodos y se reservan `4n` posiciones (cota segura para esta numeración) → espacio O(n).

**Operaciones** (índices desde 0, rangos inclusivos):
* Construcción `SegmentTree(a)`: recursión post-orden; cada nodo se calcula una vez (`n` hojas + `n-1` combinaciones) → O(n).
* `sum(l, r)`: cada nodo visitado se clasifica frente a `[l, r]`: **nulo** (sin posiciones comunes, aporta 0), **total** (contenido: se usa `t_[i]`, no se baja) o **parcial** (se consultan los dos hijos).
* `assign(i, v)`: baja por el único camino que contiene `i`, escribe la hoja y, al volver, recalcula cada antecesor como suma de sus hijos.

**Errores (documentados y probados).** Arreglo vacío: construir es válido (`size()==0`); `sum`/`assign` sobre él lanzan `std::out_of_range`.
`l < 0` o `r >= n` (o `i` fuera de `[0, n-1]`) → `std::out_of_range`; `l > r` → `std::invalid_argument`. Una operación rechazada no modifica la estructura.
Las sumas usan `long long` sin detección de desbordamiento (limitación conocida).

**Caso práctico.** Cada posición son las ventas de un día: el índice `i` corresponde al **día `i+1`**. Consultar `sum(1, 4)` es «del día 2 al día 5»; `assign(2, 6)` corrige el día 3.

## 5. Cómo se conecta C++ con la animación

```
segment_tree.hpp ──(llama a Observer)──> trace_recorder.hpp ──> trace/trace_demo.json ──> animation/*.py ──> MP4
   lógica pura                            solo serializa            eventos reales          solo dibuja
```

`SegmentTree` recibe un `Observer*` opcional y lo invoca en cada paso relevante (hoja construida, nodo combinado, nodo visitado con su solapamiento, nodo del camino
de actualización, nodo recalculado…). Con `nullptr` (todas las pruebas) no se registra nada. `TraceRecorder` implementa `Observer` y escribe JSON.
El animador **no repite el algoritmo**: las sumas, los tipos de solapamiento, las contribuciones y los conteos que aparecen en pantalla y en la voz se leen de los eventos.
Solo calcula posiciones, colores y transiciones. Además `trace_model.py` verifica que los eventos sean coherentes entre sí y con las capturas (`snapshot`) del vector real de C++
(por ejemplo, reconstruye `t[i]` aplicando los eventos y lo compara con la copia del vector tomada en C++).

### Formato de la traza (`version: 1`)

Objeto `{"format":"segment-tree-trace","version":1,"initial":[...],"events":[...]}`. Cada evento es un objeto con `type`:

| `type` | Campos | Significado |
|---|---|---|
| `build_begin` / `build_end` | `n` / `n`, `nodes_used` | inicio y fin de la construcción |
| `build_leaf` | `node`, `l`, `r`, `value` | hoja `t[node]` = `a[l]` |
| `build_combine` | `node`, `l`, `r`, `left_sum`, `right_sum`, `sum` | nodo interno = suma de hijos |
| `query_begin` / `query_end` | `l`,`r` / `l`,`r`,`result`,`visited` | consulta y su resultado |
| `query_visit` | `node`, `l`, `r`, `overlap` (`none`/`partial`/`total`), `contribution`, `running_total` | nodo visitado; `l`,`r` son los del **nodo** |
| `update_begin` / `update_end` | `index`,`value` / `index`,`value`,`nodes_touched` | asignación |
| `update_descend` | `node`, `l`, `r` | nodo del camino hacia la hoja |
| `update_leaf` | `node`, `index`, `old`, `new` | hoja modificada |
| `update_recalc` | `node`, `l`, `r`, `old_sum`, `new_sum` | antecesor recalculado (al volver) |
| `error` | `op`, `kind`, `message` | operación rechazada (`message` = `what()` de la excepción) |
| `snapshot` | `label`, `tree` | copia del vector `t_` (coste O(n), solo visualización) |
| `note` | `label` | marca de escena (`query_1`, `update`, `query_2`, `edge_single`, `full_range`, `invalid`, `empty`) |

## 6. Pruebas ejecutadas (resultados reales, ver `evidence/salida_pruebas.txt`)

`cpp/tests.cpp` (30 589 comprobaciones, todas superadas, también con UBSan): ejemplo completo del enunciado (13, 14, 6, 23); consulta de todo el arreglo;
consulta de un solo elemento; arreglo de un elemento; tamaños no potencia de dos (3, 5, 6, 7, 9, 10, 11, 13, 100, 1000); negativos y ceros; actualizaciones repetidas;
primer y último elemento; arreglo vacío y entradas inválidas (excepciones); 300 casos aleatorios con semilla fija contra una suma directa que existe **solo en las pruebas**;
invariante «nodo = suma de hijos»; y que los eventos exportados contengan los valores esperados (`result:13`, `visited:9`, `nodes_used:11`).
Compilación con `-Wall -Wextra -Wpedantic -Wshadow -Wconversion`: sin advertencias en el código del proyecto.

## 7. Limitaciones reales

* **AddressSanitizer no se pudo usar**: `zig c++` en Windows falla al enlazar (`__asan_shadow_memory_dynamic_address`). Solo se ejecutó UBSan. Con g++ el `Makefile` incluye `-fsanitize=address,undefined` (`make test`), pero **no se ejecutó** aquí.
* La voz en off es sintética (SAPI de Windows); suena robótica y solo existe en Windows. En otros sistemas el video sale sin voz.
* Se usó Pillow en lugar de Manim: el estilo visual es propio y más simple (sin curvas ni LaTeX).
* Sin protección contra desbordamiento de `long long`; sin lazy propagation ni actualizaciones de rango (fuera del alcance).
* La rúbrica de Gradescope no se recibió: no se revisó contra ella, solo contra el enunciado.
* El enlace del video no existe: el MP4 (unos 8 MB) se entrega dentro de la carpeta; si Gradescope lo rechazara por tamaño, deberán subirlo ustedes y poner el enlace real en el informe.
* El video `WhatsApp Video 2026-09-17 …mp4` que se adjuntó es de un Suffix Tree; no se usó en este proyecto.
