# Lista de Tareas: Implementación de las Tres Mejoras Metodológicas de la Tesis

Este checklist detalla los pasos para ejecutar las tres mejoras metodológicas aprobadas:

- `[x]` **Mejora 1: Imputación Fraccionaria de Tiempo (GTFS)**
    - `[x]` Descargar o estructurar los datos GTFS de colectivos, subtes y trenes.
    - `[x]` Calcular las velocidades teóricas promedio y tiempos por kilómetro y modo usando GTFS.
    - `[x]` Desarrollar la función de imputación fraccionaria en Python y aplicarla a los viajes intra-horarios en lugar de la constante de 0.5 h.
    - `[x]` Validar la mejora en el modelo de regresión OLS ($R^2$ y significancia).

- `[x]` **Mejora 2: Reconstrucción Semanal Longitudinal de Tarjetas**
    - `[x]` Diseñar el algoritmo de encadenamiento longitudinal de viajes de la tarjeta a lo largo del dataset histórico semanal.
    - `[x]` Implementar ejecución paralela en Python aprovechando los 32 hilos y 128GB de RAM.
    - `[x]` Identificar el patrón del hexágono "hogar/pernocte" y resolver los viajes "huérfanos" del retorno vespertino.
    - `[x]` Reconstruir el dataset consolidado de viajes e integrarlo en la base de DuckDB de la tesis.

- `[x]` **Mejora 3: Dualidad Espacial (H3 Multiescala + Voronoi)**
    - `[x]` **Enfoque A: Análisis Multiescala H3**:
        - `[x]` Modificar el pipeline de grafos y correlaciones para ejecutarse en resoluciones H3 7, 8 y 9.
        - `[x]` Generar tablas comparativas de coeficientes de Pearson/Spearman entre resoluciones (Análisis de Sensibilidad de MAUP).
    - `[x]` **Enfoque B: Agregación por Polígonos de Voronoi**:
        - `[x]` Obtener paradas densas y calcular los polígonos de Voronoi ponderados.
        - `[x]` Asignar coordenadas origen/destino de viajes a los polígonos de Voronoi.
        - `[x]` Construir el grafo físico en base a estas zonas y calcular centralidades (Closeness y Betweenness).
        - `[x]` Ejecutar el análisis de correlación con Tarifa Social a escala de Voronoi.

- `[x]` **Recompilación y Verificación Final**
    - `[x]` Recompilar la tesis completa en PDF (`compile_thesis.py`).
    - `[x]` Recompilar las diapositivas de la presentación (`compile_presentation.py`).
    - `[x]` Actualizar el reporte de avances `walkthrough.md`.
