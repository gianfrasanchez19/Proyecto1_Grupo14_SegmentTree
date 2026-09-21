# Guion de exposición – Grupo 14 – Segment Tree

Este reparto es **solo para la exposición** (quién explica qué); no indica quién programó cada componente.
Duración total ≈ 5:00 (la del video). Los tiempos salen de `build/timeline.json` del render real (puede variar ±1 s si se cambia la voz o el texto).

**Cómo exponer.** Proyecten el video y hablen ustedes sobre cada tramo, con la voz sintética silenciada (o déjenla y solo comenten lo esencial).
Cada persona tiene ~1:40 y termina siempre mostrando un resultado concreto para pasarle la palabra a la siguiente.

| Tramo | Persona | Minutos | Duración | Qué se muestra |
|---|---|---|---|---|
| 1 | Ormachea Mamani Gabriel | 0:00 – 1:37 | 1:37 | Portada, problema de ventas, TDA vs. implementación, arreglo ↔ árbol, construcción bottom-up |
| 2 | Palomino Meza Ricardo Jesus | 1:37 – 3:25 | 1:48 | Primera consulta `sum(1,4)`, actualización `assign(2,6)`, segunda consulta `sum(1,4)` |
| 3 | Sanchez Echevarria Andre Gianfranco | 3:25 – 5:00 | 1:35 | Caso borde `sum(2,2)`, rango completo, entradas inválidas, complejidad, conclusiones |

---

## Tramo 1 – Ormachea Mamani Gabriel (0:00 – 1:37)

* **0:00 Presentación** (portada). Grupo 14, estructura asignada: Segment Tree. Idea en una frase: responder sumas de intervalos sin recorrerlos y aceptar correcciones.
* **0:08 Problema** (arreglo de ventas). Cada posición es un día. **Índices desde 0, días desde 1**: el día 2 al día 5 son los índices 1 a 4. Sumar a mano cuesta O(n) por consulta.
* **0:26 TDA** (dos tarjetas). El TDA es la *interfaz*: `size()`, `sum(l, r)`, `assign(i, v)`. El Segment Tree es *una implementación* (árbol en un `std::vector`, raíz `t[1]`, hijos `2i` y `2i+1`). Otra implementación válida sería recorrer el vector.
* **0:44 Estructura** (árbol vacío de sumas). Raíz = `[0,5]`; cada nodo se parte por la mitad; hojas = un elemento; 11 nodos para 6 elementos; la hoja del índice 2 está en `t[5]`.
* **1:01 Construcción** (hojas → raíz). Las hojas copian el arreglo; cada padre = suma de sus hijos. Raíz = 22. Cada nodo se calcula una vez → O(n).
* **Pasa la palabra:** «Ya tenemos el árbol con 22 en la raíz; ahora lo consultamos.»

## Tramo 2 – Palomino Meza Ricardo Jesus (1:37 – 3:25)

* **1:37 Primera consulta `sum(1,4)`** (colores). Explicar la leyenda: **verde = total** (el nodo cabe entero en la consulta: se usa su suma y no se baja), **ámbar = parcial** (se baja a los hijos), **gris = nulo** (no comparte posiciones: se descarta). Seguir la traza: `[0,5]` parcial → `[0,2]` parcial → `[0,1]` parcial → hoja 0 nula → hoja 1 total (+1) → hoja 2 total (+5) → `[3,5]` parcial → `[3,4]` total (+7) → hoja 5 nula. Resultado 1+5+7 = **13**; 9 nodos visitados.
* **2:29 Actualización `assign(2,6)`** (camino azul, hoja roja, antecesores morados). Se baja por `t[1] → t[2] → t[5]`, la hoja pasa de 5 a 6 y **solo** se recalculan sus antecesores: `t[2]` (8 → 9) y `t[1]` (22 → 23). Solo 3 nodos tocados → O(log n). Decir explícitamente que `t[3]` no se toca.
* **2:58 Segunda consulta** (mismo recorrido). Resultado **14** = 1 + 6 + 7; el nodo `[3,4]` (7) se reutilizó sin cambios.
* **Pasa la palabra:** «Ahora los casos límite y por qué todo esto es O(log n).»

## Tramo 3 – Sanchez Echevarria Andre Gianfranco (3:25 – 5:00)

* **3:25 Caso borde `sum(2,2)`** (un solo elemento). Solo baja hasta la hoja `t[5]`; resultado **6**, el valor ya actualizado. 5 nodos visitados.
* **4:03 Rango completo `sum(0,5)`.** La raíz ya cubre todo: **23** con 1 nodo visitado → O(1).
* **4:09 Entradas inválidas** (mensajes reales de C++). `sum(4,1)` (l > r, `invalid_argument`), `sum(0,6)` (fuera de límites, `out_of_range`), consulta sobre arreglo vacío (`out_of_range`). Construir un arreglo vacío sí es válido.
* **4:17 Complejidad de la consulta.** Por nivel hay a lo sumo **2 nodos parciales** (los que contienen las fronteras `l-1|l` y `r|r+1`); los demás son totales o nulos y no se expanden; cada parcial visita 2 hijos → ≤ 4 visitas por nivel × log n niveles.
* **4:28 Tabla.** Construcción O(n); consulta O(log n); actualización O(log n); rango completo O(1); espacio O(n) (2n−1 nodos en un vector de 4n). Aparte: exportar la traza, guardar capturas del vector (O(n) cada una) y renderizar **no** son costo de la estructura.
* **4:47 Conclusiones.** (1) Consultas y actualizaciones en O(log n), frente a O(n) / O(1) de la suma directa: conviene cuando se mezclan ambas. (2) Todo lo mostrado salió de la ejecución real en C++ (eventos JSON), no de una simulación.

---

## Preguntas de preparación (con respuesta breve)

**1. ¿Por qué construir el árbol cuesta O(n) y no O(n log n)?**
Porque cada uno de los 2n−1 nodos se calcula una sola vez con trabajo constante (copiar una hoja o sumar dos hijos). Si empezáramos con ceros y aplicáramos n actualizaciones, cada una cuesta O(log n) y el total sería O(n log n).

**2. ¿Qué significan solapamiento total, parcial y nulo?**
Sea `[nl, nr]` el intervalo del nodo y `[l, r]` la consulta. *Nulo*: `nr < l` o `nl > r` (no comparten posiciones) → aporta 0. *Total*: `l ≤ nl` y `nr ≤ r` (el nodo está contenido) → se suma `t[nodo]` y no se baja. *Parcial*: comparten algo pero no está contenido → se consultan los dos hijos.

**3. ¿Por qué la consulta es O(log n) en el peor caso y no solo «porque el árbol es de altura log n»?**
Porque hay que acotar cuántos nodos se visitan por nivel. En un nivel los nodos son disjuntos y consecutivos; solo pueden ser parciales los que contienen la frontera izquierda o la derecha de la consulta: como mucho 2. Cada parcial visita 2 hijos, así que hay ≤ 4 visitas por nivel y O(log n) niveles.

**4. ¿Qué se recalcula al actualizar y por qué?**
La hoja del índice y sus antecesores (un único camino a la raíz), porque son los únicos nodos cuyo intervalo contiene ese índice; el resto conserva su suma. En el ejemplo: `t[5]` (5→6), `t[2]` (8→9), `t[1]` (22→23).

**5. ¿Cuándo una consulta es O(1)?**
Cuando el intervalo consultado es exactamente el intervalo de un nodo desde el inicio, típicamente todo el arreglo: la raíz tiene solapamiento total y devuelve `t[1]` sin bajar (en el video `sum(0,5) = 23`, 1 nodo visitado).

**6. ¿Qué ventaja tiene frente a sumar directamente el arreglo?**
Suma directa: consulta O(n), actualización O(1). Segment Tree: ambas O(log n). Si hay muchas consultas mezcladas con correcciones, el árbol gana; si casi no hay consultas, la suma directa es más simple y no usa espacio extra.

**7. ¿Cuál es la diferencia entre el TDA y el Segment Tree?**
El TDA (`size`, `sum`, `assign`) dice *qué* se puede hacer; el Segment Tree dice *cómo* (árbol en vector) y da las complejidades. Se podría cambiar la implementación sin cambiar quien usa la interfaz.

**8. ¿Cómo se guarda el árbol en un vector y cuánto espacio usa?**
Raíz en `t[1]`, hijos de `t[i]` en `t[2i]` y `t[2i+1]`. Se usan 2n−1 nodos y se reservan 4n posiciones (cota segura para esta numeración) → O(n).

**9. ¿Cómo sabemos que la animación no está inventada?**
El programa C++ emite eventos JSON (`trace/trace_demo.json`); el animador lee sumas, solapamientos y contribuciones de esos eventos y no reimplementa el algoritmo. Además verifica que los eventos reconstruyan el vector copiado por C++ (`snapshot`).

**10. ¿Qué pasa con entradas inválidas?**
`l > r` → `std::invalid_argument`; índices negativos o ≥ n → `std::out_of_range`; consultar/actualizar un arreglo vacío → `std::out_of_range`. Construir un arreglo vacío es válido. Una operación rechazada no modifica la estructura.

**11. ¿Qué limitaciones tiene su implementación?**
Suma en `long long` sin control de desbordamiento; solo sumas con asignación puntual (sin lazy propagation ni actualización de rangos); solo se pudo usar UBSan (ASan no enlazó en el entorno de desarrollo).

**12. ¿Qué costo tiene generar la traza y el video?**
Cada evento es O(1), así que una consulta añade O(log n) eventos; cada captura del vector (`snapshot`) cuesta O(n); el video cuesta proporcional al número de fotogramas (unos 6 000). Nada de eso forma parte de las cotas de la estructura.
