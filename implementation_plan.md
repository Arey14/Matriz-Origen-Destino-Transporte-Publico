# Plan de Implementación: Análisis de Vulnerabilidad y Centralidad de Transporte en el AMBA

Este plan detalla la metodología, los scripts y los mapas que implementaremos para estudiar las zonas con transporte más postergado y vulnerable en el AMBA, combinando análisis de datos socio-espaciales (SQL) y teoría de redes (grafos).

---

## Metodología Propuesta

### Enfoque 1: Índice de Vulnerabilidad Socio-Espacial (SQL + Plotly H3)
Este enfoque directo combina la vulnerabilidad social (usuarios que dependen del subsidio estatal) con la fricción del transporte (IFI).

1.  **Métricas por Hexágono H3 de Origen**:
    *   **Proporción de Tarifa Social**: $\frac{\text{Viajes con Tarifa Social}}{\text{Viajes Totales}}$
    *   **Mediana del IFI**: Fricción de transbordos por cada 10 km.
    *   **Mediana de Velocidad**: $\text{Mediana}(\frac{\text{distancia}}{\text{duracion\_horas}})$.
2.  **Cálculo del Índice**:
    *   Normalizaremos la Proporción de Tarifa Social y la Mediana del IFI a una escala de $[0, 1]$.
    *   Calcularemos el **Índice de Vulnerabilidad Socio-Espacial (IVSE)** como el producto de ambas métricas normalizadas:
        $$\text{IVSE} = \text{Tarifa Social Normalizada} \times \text{IFI Normalizado}$$
    *   Esto resalta las zonas con alta vulnerabilidad económica que además enfrentan alta ineficiencia de viaje.
3.  **Visualización**:
    *   Crearemos la **Figura 14**: Un mapa interactivo H3 (`figura14_vulnerabilidad_sql.html`) coloreado por el IVSE.

---

### Enfoque 2: Análisis de Centralidad Estructural (Grafos con NetworkX)
Este enfoque modela los viajes del AMBA como una red dirigida donde los nodos son hexágonos H3 y los enlaces son flujos agregados de viajes.

1.  **Preparación del Entorno**:
    *   Instalaremos `networkx` en el entorno virtual `tesis` para el procesamiento del grafo.
2.  **Construcción del Grafo**:
    *   **Nodos**: Hexágonos H3 de resolución 8.
    *   **Enlaces**: Dirigidos de $O \to D$.
    *   **Peso de Costo ($w_{ij}$)**: Tiempo promedio de viaje (duración en horas) entre hexágonos.
3.  **Cálculo de Centralidades**:
    *   **Centralidad de Cercanía Ponderada (Weighted Closeness Centrality)**:
        Identifica zonas estructuralmente aisladas. Una cercanía baja indica que viajar desde/hacia ese hexágono toma mucho tiempo.
    *   **Centralidad de Intermediación Ponderada (Weighted Betweenness Centrality)**:
        Identifica zonas que actúan como "puentes" críticos del transporte.
4.  **Visualizaciones**:
    *   Crearemos la **Figura 15**: Mapa H3 de Cercanía Estructural (`figura15_cercania_red.html`).
    *   Crearemos la **Figura 16**: Mapa H3 de Intermediación/Puentes de Red (`figura16_intermediacion_red.html`).
5.  **Análisis de Correlación Cruzada**:
    *   Analizaremos estadísticamente la correlación entre la centralidad estructural (aislamiento) y el porcentaje de Tarifa Social para responder la pregunta de tesis: **¿El aislamiento físico en la red de transporte coincide con la vulnerabilidad socioeconómica?**

---

## Archivos a Modificar / Crear

### [NEW] [analisis_vulnerabilidad_red.py](file:///home/augusto/Downloads/Compressed/Tesis/Matriz-Origen-Destino-Transporte-Publico/analisis_vulnerabilidad_red.py)
Un script de Python dedicado para realizar ambos análisis (SQL y grafos) usando DuckDB y NetworkX. Guardará las estadísticas detalladas y los tres nuevos mapas interactivos en la carpeta del proyecto.

### [MODIFY] [EDA-duck.ipynb](file:///home/augusto/Downloads/Compressed/Tesis/Matriz-Origen-Destino-Transporte-Publico/EDA-duck.ipynb)
Una vez validado el script, integraremos las funciones en celdas separadas en el cuaderno interactivo para que queden incorporadas en tu flujo de trabajo.

---

## Plan de Verificación

1.  **Validación de Librerías**: Confirmar que la instalación de `networkx` sea correcta.
2.  **Ejecución del Script**: Ejecutar `analisis_vulnerabilidad_red.py` en el entorno de la tesis y comprobar que:
    *   No haya errores de memoria al construir el grafo con hexágonos.
    *   Los archivos `figura14_vulnerabilidad_sql.html`, `figura15_cercania_red.html` y `figura16_intermediacion_red.html` se generen correctamente.
3.  **Verificación de Mapas**: Abrir y validar los mapas HTML.
