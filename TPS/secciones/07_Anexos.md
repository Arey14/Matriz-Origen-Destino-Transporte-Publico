# Anexos

## Código Fuente y Repositorio del Proyecto

El código desarrollado para este análisis, incluyendo el cuaderno de Jupyter `EDA-duck.ipynb` y el script de redes `analisis_vulnerabilidad_red.py`, se encuentra alojado en el repositorio público del proyecto. 

*   **Enlace al Repositorio**: 

* `https://github.com/facundo-augusto-rey/Tesis-Matriz-OD-Transporte-AMBA`

## Resumen Técnico del Procesamiento

El flujo de trabajo automatizado en Python para el Enfoque 2 (Grafo y Centralidad) realiza los siguientes pasos computacionales:
1.  Establece una conexión en memoria con DuckDB.
2.  Carga los archivos CSV de viajes, etapas y paradas como vistas relacionales.
3.  Crea la vista unificada `viajes_geo`, calculando la distancia Haversine y clasificando los viajes por jurisdicción e intermodalidad.
4.  Filtra y extrae los enlaces que representan trayectos consolidados con un volumen superior a 30 viajes diarios.
5.  Construye el grafo dirigido en NetworkX, utilizando la duración del viaje como peso de fricción.
6.  Computa de manera ponderada las métricas de cercanía y intermediación en el grafo de tránsito.
7.  Cruza las métricas del grafo con el ratio de Tarifa Social y calcula las matrices de correlación de Pearson y Spearman.

## Tablas de Datos Adicionales

### Flujos y Conexiones de Red Consolidadas (Top 10 Enlaces de Mayor Duración de Viaje por Jurisdicción)

A continuación se presentan los 10 enlaces estables de la red de transporte público del AMBA (filtrados con un volumen de al menos **200 viajes semanales** para capturar tanto corredores de volumen masivo como conexiones secundarias estables de menor frecuencia, excluyendo bucles locales de origen/destino idéntico) que registran las **mayores duraciones medias de viaje, ordenados de mayor a menor**, incluyendo la distancia media calculada (Haversine) y el modo principal de transporte observado.

#### 1. Enlaces Intra-CABA (Internos de la Ciudad de Buenos Aires)

\scriptsize

| Referencia Origen | Referencia Destino | Volumen (Viajes) | Duración Media (Horas) | Distancia Media (km) | Modo de Transporte |
| :--- | :--- | :---: | :---: | :---: | :--- |
| Belgrano C (Comuna 13) | Retiro (Comuna 1) | 247 | 0.94 | 7.82 | Tren + Subte |
| Liniers (Comuna 9) | Once - 30 de Diciembre (Comuna 3) | 316 | 0.92 | 11.42 | Tren + Subte |
| Congreso de Tucumán (Comuna 13) | Constitución (Comuna 1) | 261 | 0.80 | 10.91 | Solo Subte |
| Retiro (Comuna 1) | Plaza Constitución (Comuna 1) | 234 | 0.79 | 4.24 | Tren + Subte |
| Sin nombre (Comuna 15) | Lacroze (Chacarita, Comuna 15) | 244 | 0.75 | 0.17 | Solo Colectivo |
| Constitución (Comuna 1) | Juramento (Comuna 13) | 428 | 0.73 | 10.00 | Solo Subte |
| Malabia - Osvaldo Pugliese (Comuna 15) | Constitución (Comuna 1) | 215 | 0.71 | 6.22 | Solo Subte |
| Lavalle (Comuna 1) | Plaza Constitución (Comuna 1) | 291 | 0.65 | 3.04 | Tren + Subte |
| Leandro N. Alem (Comuna 1) | Lacroze (Chacarita, Comuna 15) | 736 | 0.62 | 8.01 | Tren + Subte |
| Devoto (Comuna 11) | Retiro (Comuna 1) | 563 | 0.59 | 12.87 | Solo Tren |

\normalsize

#### 2. Enlaces Intra-PBA (Internos del Conurbano Bonaerense)

\scriptsize

| Referencia Origen | Referencia Destino | Volumen (Viajes) | Duración Media (Horas) | Distancia Media (km) | Modo de Transporte |
| :--- | :--- | :---: | :---: | :---: | :--- |
| Lomas de Zamora Centro | Sin nombre (Almirante Brown) | 285 | 1.03 | 11.13 | Col + Tren |
| Sin nombre (La Matanza) | Sin nombre (Morón) | 357 | 1.02 | 13.35 | Solo Colectivo |
| Morón Centro | Sin nombre (Merlo) | 332 | 1.01 | 10.08 | Col + Tren |
| Morón Centro | Sin nombre (Moreno) | 245 | 1.00 | 15.69 | Col + Tren |
| Glew (Almirante Brown) | Darío Santillán y Maximiliano Kosteki (Avellaneda) | 216 | 0.94 | 25.21 | Solo Tren |
| Sin nombre (Morón Centro) | Sin nombre (La Matanza) | 255 | 0.93 | 13.35 | Solo Colectivo |
| Sin nombre (La Matanza) | Sin nombre (Morón Centro) | 311 | 0.92 | 11.36 | Solo Colectivo |
| La Plata Centro | Berazategui Centro | 583 | 0.92 | 28.34 | Solo Tren |
| Quilmes Centro | La Plata Centro | 681 | 0.91 | 34.75 | Col + Tren |
| Berazategui Centro | La Plata Centro | 631 | 0.91 | 28.34 | Solo Tren |

\normalsize

#### 3. Enlaces PBA-CABA (Entrada a la Ciudad desde el Conurbano)

\scriptsize

| Referencia Origen | Referencia Destino | Volumen (Viajes) | Duración Media (Horas) | Distancia Media (km) | Modo de Transporte |
| :--- | :--- | :---: | :---: | :---: | :--- |
| La Plata Centro | Constitución (Comuna 1) | 581 | 1.45 | 50.03 | Tren + Subte |
| Paso del Rey (Moreno) | Once - 30 de Diciembre (Comuna 3) | 241 | 1.37 | 33.02 | Tren + Subte |
| Alejandro Korn (San Vicente) | Constitución (Comuna 1) | 345 | 1.34 | 39.25 | Tren + Subte |
| Alejandro Korn (San Vicente) | Sin nombre (Comuna 1) | 216 | 1.33 | 39.20 | Col + Tren |
| José C. Paz Centro | Palermo (Comuna 14) | 282 | 1.29 | 30.51 | Tren + Subte |
| Moreno Centro | Once - 30 de Diciembre (Comuna 3) | 533 | 1.29 | 35.40 | Tren + Subte |
| Moreno Centro | Sin nombre (Comuna 3) | 359 | 1.28 | 35.41 | Col + Tren |
| Ezeiza Centro | Sin nombre (Comuna 1) | 428 | 1.23 | 28.34 | Col + Tren |
| Merlo Centro | Sin nombre (Comuna 3) | 353 | 1.17 | 30.10 | Col + Tren |
| Tigre Centro | Retiro (Comuna 1) | 472 | 1.17 | 26.64 | Tren + Subte |

\normalsize

*Nota: Al filtrar por un volumen de al menos 200 viajes semanales y excluir bucles locales de origen/destino idéntico, emergen con fuerza los trayectos que combinan colectivos y trenes (Col + Tren) o trenes y subtes (Tren + Subte). Los viajes interjurisdiccionales (PBA-CABA) de conmuters desde el oeste (Moreno, Merlo) y el sur (Glew, Varela, La Plata) registran duraciones medias elevadas que superan con holgura la hora de viaje neto, demostrando el impacto del transbordo forzado en la fricción temporal metropolitana. Asimismo, el cálculo de la distancia Haversine media permite contrastar la extensión física de los enlaces frente a la escala de fricción temporal, confirmando que las ineficiencias de transbordo dominan la experiencia de viaje.*
