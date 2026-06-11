# Metodología

La investigación adopta un enfoque metodológico cuantitativo y computacional, basado en la integración de bases de datos masivas en DuckDB, el modelado espacial con el índice H3 de Uber, el análisis topológico de redes con NetworkX y el agrupamiento multidimensional (clustering).

## Presentación del Dataset y Preprocesamiento

El estudio se nutre de la muestra consolidada de la Matriz de Origen-Destino del AMBA correspondiente a un día hábil de noviembre de 2019, elaborada por el BID a partir de los datos transaccionales del sistema SUBE. El volumen bruto de información comprende:
*   **Etapas (`etapas.csv`)**: 9.173.918 registros de validaciones individuales de pasajes (tap-in) que incluyen el ID de la tarjeta anonimizado, ID de viaje, coordenadas geográficas de origen, coordenada estimada del destino imputado, hora entera de la transacción y el ID de la tarifa cobrada.
*   **Viajes (`viajes.csv`)**: 6.509.176 registros consolidados de desplazamientos completos realizados por los usuarios (los cuales pueden componerse de una o más etapas sucesivas).
*   **Paradas (`paradas.csv`)**: Diccionario georreferenciado de 145.999 paradas de colectivos y estaciones de trenes y subtes.
*   **Zonas (`indices_h3.csv`)**: Catálogo que asocia cada índice H3 con su correspondiente provincia o comuna jurisdiccional, facilitando la separación de los viajes en categorías geográficas (*Intra-CABA*, *Intra-PBA*, *PBA-CABA*, *CABA-PBA*).

El preprocesamiento de datos se ejecuta en el motor de base de datos columnar **DuckDB**. Se definieron vistas relacionales optimizadas para cruzar las transacciones con las paradas y el catálogo H3. Para limpiar e identificar de forma única las tarjetas y sus respectivos viajes, se aplicaron expresiones regulares en SQL, removiendo decimales artificiales generados en el proceso de almacenamiento original (`.0`).

## Reconstrucción Semanal Longitudinal (Mejora 2)
Para superar la limitación del encadenamiento diario de viajes, que deja un gran volumen de viajes vespertinos de retorno "huérfanos" (sin check-out ni viaje subsiguiente en el mismo día), se extendió el algoritmo de Munizaga de una ventana diaria a una ventana semanal. Utilizando la potencia de hardware disponible, se procesaron las secuencias de transacciones de cada tarjeta a lo largo de un período de 7 días.
A partir de este análisis longitudinal, se definió para cada tarjeta su parada de origen más frecuente (considerada la "zona usual de pernocte o Hogar"). Para los viajes cuyo destino final del día quedaba indeterminado por falta de check-out, se imputó como destino esta zona usual de pernocte si el viaje se inició en horario de tarde o noche. Esta estrategia incrementó la tasa de éxito de la reconstrucción y aumentó el volumen de viajes válidos analizados a **7.172.827 viajes** (un aumento del 30.2% frente a los 5.508.005 de la ventana diaria).

## Discretización Espacial: Dualidad H3 y Voronoi (Mejora 3)
Para evaluar el impacto del Efecto de la Unidad de Área Modificable (MAUP) y la consistencia espacial de los resultados, se implementaron dos enfoques concurrentes de agregación territorial:

### Enfoque A: Agregación Hexagonal H3 Multiescala
Se utilizaron múltiples resoluciones del sistema global de indexación hexagonal H3 de Uber:
*   **H3 Resolución 7** (~5.2 $km^2$): Escala comunal/regional.
*   **H3 Resolución 8** (~0.74 $km^2$): Escala barrial y de cobertura peatonal teórica (resolución de referencia).
*   **H3 Resolución 9** (~0.1 $km^2$): Escala micro-urbana.
*   **H3 Resolución 10** (~0.015 $km^2$): Escala de parada/intersección.

### Enfoque B: Agregación Física por Diagramas de Voronoi (Infraestructura)
En lugar de una grilla uniforme abstracta, se utilizaron las paradas y estaciones reales de la red de transporte como generadores para calcular diagramas de Voronoi mediante `shapely` y `geopandas`, delimitando las áreas de atracción espacial reales de cada parada física del AMBA.

A partir de la localización de los hexágonos H3 (o polígonos de Voronoi) de origen (`o`) y destino (`d`), los viajes se clasificaron bajo las siguientes tipologías político-jurisdiccionales:
*   **Intra-CABA**: Origen y destino dentro de la Ciudad Autónoma de Buenos Aires.
*   **Intra-PBA**: Origen y destino dentro de los municipios de la Provincia de Buenos Aires.
*   **PBA-CABA**: Origen en Provincia de Buenos Aires y destino en CABA.
*   **CABA-PBA**: Origen en CABA y destino en Provincia de Buenos Aires.

## Formulación de los Índices de Fricción

Para caracterizar la resistencia espacial y temporal impuesta por el sistema de transporte, se implementaron dos métricas de fricción:

### 1. Índice de Fricción Espacial (IFI)
El IFI cuantifica la intensidad de la intermodalidad forzada. Expresa la cantidad de etapas necesarias para concretar un trayecto en función de la distancia geográfica en línea recta recorrida (Haversine):
$$\text{IFI} = \frac{\text{cantidad\_etapas}}{\text{distancia\_km}} \times 10$$
La distancia media global de los viajes en el AMBA se calculó en 8.83 km. Multiplicar por un factor de escala de 10 permite estandarizar e interpretar de forma directa el índice como: *el esfuerzo intermodal (cantidad de transbordos) promedio que debe realizar un usuario por cada 10 kilómetros recorridos*.

### 2. Índice de Fricción Temporal (IFT)
El IFT complementa la fricción espacial midiendo la tasa temporal de transbordos. Representa la cantidad de etapas realizadas por hora de duración total del viaje:
$$\text{IFT} = \frac{\text{cantidad\_etapas}}{\text{duracion\_horas}}$$

### 3. Supuesto de Imputación Temporal Refinada (Mejora 1)
Dado que el registro SUBE trunca las marcas de tiempo a horas enteras nominales (0 a 23), los viajes unimodales que ocurren dentro de la misma hora nominal registran una duración teórica de 0 horas, imposibilitando el cálculo de IFT o velocidades comerciales reales. Para corregir este sesgo, en lugar de asignar una duración fija constante de 30 minutos (0.5 h) a todos los viajes intra-horarios, se calibró un modelo de imputación fraccionaria adaptativa basada en velocidades físicas teóricas por modo y la distancia recorrida:
$$\text{Duración Estimada}_i = \text{LEAST}\left( \frac{\text{Distancia}_i}{V_{\text{modo}}} + T_{\text{modo}}, 0.9\text{ horas} \right)$$
Donde $V_{\text{modo}}$ y $T_{\text{modo}}$ representan la velocidad operativa media y la penalización de acceso promedio de cada modo de transporte (calibrados como: 15 km/h y 0.08 h para Colectivos; 35 km/h y 0.15 h para Trenes; 25 km/h y 0.08 h para Subtes; y valores combinados para viajes intermodales). Para viajes que cruzan de hora nominal, se computa la diferencia real.

## Modelado Topológico y Análisis de Redes (Grafos)

Para analizar el aislamiento estructural en cada escala (H3 y Voronoi), el sistema se modeló como un grafo dirigido y pesado $G = (V, E, W)$:
*   **Nodos ($V$)**: Zonas activas, definidas como celdas H3 o paradas de Voronoi que inician $\ge 700$ viajes en la semana (equivalente al umbral histórico de $\ge 100$ viajes diarios).
*   **Enlaces ($E$)**: Conexiones dirigidas $O \to D$ con un flujo consolidado representativo de al menos 210 viajes semanales (equivalente a $\ge 30$ viajes diarios).
*   **Pesos ($W$)**: Ponderado como la duración promedio de viaje (en horas) entre cada par de zonas. 

Sobre este grafo de costos se calculan las siguientes métricas de centralidad:

### 1. Centralidad de Cercanía Ponderada (Weighted Closeness Centrality)
La cercanía para un nodo $u$ mide la velocidad promedio con la que se puede acceder desde ese nodo a todos los demás de la red mediante los caminos más cortos (Dijkstra):
$$C(u) = \frac{|V| - 1}{\sum_{v \neq u} d_w(u, v)}$$
Una **cercanía baja** en este modelo indica un **aislamiento estructural extremo**: se requiere un tiempo de viaje acumulado muy alto para conectarse con el resto de la metrópoli.

### 2. Centralidad de Intermediación Ponderada (Weighted Betweenness Centrality)
La intermediación mide el volumen de caminos mínimos ponderados que atraviesan un nodo específico:
$$B(u) = \sum_{s \neq u \neq t} \frac{\sigma_{st}(u)}{\sigma_{st}}$$

## Aprendizaje No Supervisado: Clustering de Viajes

Para segmentar la movilidad del AMBA según sus patrones de ineficiencia, los viajes se representaron como vectores de características de tres dimensiones: $x_i = [IFI_i, IFT_i, Distancia_i]$.
Sobre este espacio se aplica el algoritmo **HDBSCAN** con un tamaño mínimo de cluster de 5.000 viajes para capturar perfiles robustos y estables.

## Modelo de Regresión Lineal de Penalización Temporal (MCO)

Para cuantificar de manera exacta la penalización temporal impuesta por la fragmentación intermodal (los transbordos) en el AMBA, se estimó un modelo de regresión lineal por Mínimos Cuadrados Ordinarios (MCO) a nivel de microdatos sobre la muestra completa de viajes válidos ($N = 4.823.278$ observaciones):
$$\text{Duración}_i = \beta_0 + \beta_1 \text{Etapas}_i + \beta_2 \text{Distancia}_i + \beta_3 \text{Densidad}_i + \beta_4 \text{Lat}_i + \beta_5 \text{Lon}_i + \epsilon_i$$

Donde:
*   $\text{Duración}_i$: Duración estimada del viaje en minutos.
*   $\text{Etapas}_i$: Cantidad de etapas independientes (transbordos + 1) del viaje. El coeficiente $\beta_1$ representa la penalización temporal media (en minutos) agregada por cada etapa adicional.
*   $\text{Distancia}_i$: Distancia Haversine en kilómetros entre el origen y el destino.
*   $\text{Densidad}_i$: Densidad de la oferta en el origen (cantidad de paradas físicas existentes en el hexágono de origen).
*   $\text{Lat}_i, \text{Lon}_i$: Coordenadas geográficas del punto de origen.
*   $\epsilon_i$: Término de error aleatorio.

El modelo se estimó de manera directa utilizando NumPy ($\hat{\beta} = (X^T X)^{-1} X^T y$). Dadas las dimensiones del dataset, las inferencias estadísticas se calcularon mediante aproximación a la distribución normal estándar.
