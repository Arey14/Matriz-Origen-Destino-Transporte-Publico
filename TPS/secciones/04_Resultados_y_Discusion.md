# Resultados y Discusión

El análisis empírico de la movilidad y la fricción en el transporte público del AMBA se estructura integrando las estadísticas del Análisis Exploratorio de Datos (AED), el comportamiento continuo de los índices IFI e IFT, la modelación de redes con NetworkX y el cruce correlacional con la Tarifa Social.

## Análisis Exploratorio de Datos (AED) y Composición Modal

El procesamiento de los datos transaccionales descriptivos de la muestra oficial reveló patrones altamente asimétricos entre jurisdicciones que sientan las bases de la hipótesis del transbordo obligado:

### 1. Relación Geografía - Intermodalidad
Al segmentar los viajes según su tipología geográfica, emergió una marcada diferencia estructural en el nivel de transbordos. Mientras el 80.2% de los viajes internos en la Ciudad de Buenos Aires (Intra-CABA) se resuelven de forma directa en una sola etapa, en la movilidad interjurisdiccional (CABA-PBA) el escenario se invierte de forma drástica: solo el 41.3% de los usuarios logra desplazarse sin realizar transbordos, mientras que el 44.4% requiere 2 etapas y un 14.3% realiza 3 o más etapas en su trayecto. Los viajes internos en el conurbano (Intra-PBA) presentan una tasa de transbordo intermedia, donde el 70.1% viaja en 1 etapa y el 25.0% realiza 2 etapas.

![Figura 1: Porcentaje de viajes según cantidad de etapas por zona geográfica.](figura1_intermodalidad.png)

### 2. Asimetría en Distancias de Viaje
La distancia lineal promedio de un viaje en el AMBA se calculó en 8.83 km (con una mediana global de 5.68 km). Sin embargo, al desglosar por jurisdicción, los desplazamientos internos registran medias notablemente inferiores: 4.92 km en Intra-CABA y 6.53 km en Intra-PBA. En contraste, la red que vincula la periferia bonaerense con el núcleo urbano central (CABA-PBA) soporta viajes masivos que promedian 18.80 km (con una mediana de 17.34 km), representando desplazamientos pendulares de muy larga distancia.

![Figura 2: Distribución de distancias de viaje según zona geográfica.](figura2_distancias.png)

### 3. Composición Modal y Dependencia
La composición de modos de transporte revela que la movilidad interna del conurbano (Intra-PBA) presenta una dependencia casi monopólica del colectivo de superficie, el cual concentra el 82.5% de los viajes. Por el contrario, los viajes de conmuters (CABA-PBA) exigen combinaciones multimodales donde el ferrocarril actúa como el troncal de larga distancia: un 22.5% combina colectivo y tren, un 7.9% combina tren y subte, y un 4.4% requiere combinar colectivo, tren y subte. Esto confirma que la intermodalidad en la periferia es una necesidad impuesta para acceder a la red ferroviaria centralizada.

![Figura 3: Composición modal de viajes por jurisdicción.](figura3_modos.png)

## Distribución Continua de IFI e IFT por Jurisdicciones

Para evaluar de forma continua las penalizaciones espaciales y temporales impuestas al usuario, analizamos los histogramas y densidades acumuladas del IFI e IFT:

### Índice de Fricción Espacial (IFI)
El análisis estadístico sobre los 5.508.005 viajes válidos demuestra que los viajes internos (Intra-CABA, mediana = 2.48 etapas por 10 km; e Intra-PBA, mediana = 2.47) sufren una fricción espacial de **más del doble** que los interjurisdiccionales (PBA-CABA y CABA-PBA, medianas de ~1.01). Este fenómeno se asocia al efecto de escala de la distancia: dado que los viajes de conmuters recorren distancias muy largas, la tasa de transbordos por cada 10 km es baja en términos relativos. No obstante, en tramos cortos de la periferia (Intra-PBA), la falta de cobertura directa penaliza severamente el viaje, obligando a múltiples transbordos para tramos de pocas cuadras.

### Índice de Fricción Temporal (IFT)
Para el IFT, aunque la mediana de todas las jurisdicciones es idéntica (2.0 etapas por hora de viaje), el comportamiento en los percentiles superiores revela el impacto del transbordo en el tiempo de viaje. El tercer cuartil (P75) de IFT para los viajes interjurisdiccionales (**PBA-CABA** y **CABA-PBA**) es de **3.0 etapas/hora**, mientras que para los viajes internos (**Intra-CABA** e **Intra-PBA**) se mantiene en **2.0**. Esto demuestra que un segmento representativo de los conmuters experimenta una alta tasa de transbordos por hora de viaje, incrementando la fricción temporal en sus traslados diarios.

![Figura 12: Distribución de IFI e IFT mediante diagramas de caja sin outliers.](figura12_boxplot_ifi_ift.png)

![Figura 13: Curvas de densidad de probabilidad estimadas por Kernel (KD## Modelación del Grafo y Centralidades Ponderadas

La red de movilidad consolidada para el AMBA en su grilla de referencia H3 de Resolución 8 cuenta con **534 nodos (hexágonos activos)** y **2.292 enlaces de flujo estables** (con $\ge 700$ viajes semanales de origen y $\ge 210$ viajes por enlace, correspondientes a los umbrales diarios escalados a la ventana semanal). Los resultados revelan una profunda polarización espacial en términos de accesibilidad estructural:

*   **Cercanía Estructural (Accesibilidad)**: Al ponderar el grafo por tiempo de viaje (costo), las celdas H3 correspondientes a la Capital Federal y al primer cordón norte del Conurbano registran la mayor centralidad de cercanía (`closeness centrality`). Esto indica que es espacial y temporalmente rápido acceder a cualquier punto de la metrópolis desde el centro. En marcado contraste, el segundo y tercer cordón (especialmente en el sur y oeste del Conurbano) presentan cercanías estructurales extremadamente bajas, evidenciando un aislamiento físico crónico (mayores tiempos acumulados de viaje).
*   **Intermediación (Hubs y Puentes)**: La intermediación ponderada (`betweenness centrality`) se concentra de forma masiva en las grandes cabeceras e intercambiadores centrales de CABA (Retiro, Constitución, Once) y en centros de trasbordo clave de la Provincia (Lanús, Lomas de Zamora, Morón, San Martín). Esto resalta el carácter radial de la red: el flujo metropolitano está obligado a pasar por unos pocos nodos "embudo" altamente congestionados para concretar los viajes cotidianos, dejando a la periferia sin rutas alternativas o directas.

## Índice de Vulnerabilidad Socio-Espacial (IVSE)

Al mapear el IVSE —calculado cruzando la tasa de Tarifa Social y la mediana de fricción espacial IFI por hexágono— se identifican geográficamente los "desiertos de tránsito vulnerables". 

Las zonas rojas críticas del IVSE se concentran intensamente en el segundo y tercer cordón del Conurbano Bonaerense (ej. sectores de La Matanza, Florencio Varela, Almirante Brown, Merlo y Moreno). En estas áreas, los usuarios enfrentan una doble marginación: residen en hogares de bajos ingresos que dependen de subsidios sociales y, simultáneamente, sufren la peor fricción de transporte, realizando trayectos largos y muy fragmentados (múltiples etapas para distancias cortas de conexión barrial).

## Análisis de Correlación Cruzada (Validación de Hipótesis)

Para validar científicamente la hipótesis de que la postergación física de la red castiga de forma sistemática a los sectores de menores recursos, se analizaron las correlaciones estadísticas de Pearson y Spearman entre la Tarifa Social por hexágono y las métricas estructurales a la resolución de referencia (H3 Res 8):

*   **Tarifa Social vs. Cercanía Estructural (`closeness`)**: Coeficiente de Spearman de **-0.6371** (con un coeficiente de Pearson de **-0.6129**). Esta correlación negativa muy fuerte es estadísticamente significativa y confirma que **a mayor proporción de población vulnerable en una zona, menor es la centralidad de cercanía de su nodo de transporte**, demostrando un aislamiento estructural sistemático de los sectores más desfavorecidos.
*   **Tarifa Social vs. Fricción Espacial (IFI)**: Coeficiente de Spearman de **0.4367** (Pearson de **0.4074**). La correlación positiva demuestra que **los sectores vulnerables experimentan una mayor fragmentación espacial en sus trayectos**, viéndose obligados a realizar más transbordos por unidad de distancia para completar sus viajes.
*   **Tarifa Social vs. Velocidad Promedio del Viaje**: Coeficiente de Spearman de **-0.5203** (Pearson de **-0.4475**). Confirma que los viajes originados en zonas vulnerables sufren de una menor velocidad comercial, producto de tiempos de espera acumulados en andenes y congestión en transportes locales de superficie.

La robustez de estas correlaciones se ve fuertemente incrementada al aplicar la reconstrucción semanal y la imputación temporal refinada, demostrando que la corrección de sesgos metodológicos revela patrones estructurales de inequidad urbana que antes quedaban subestimados por el ruido de los microdatos.

## Modelado de Regresión de Penalización Temporal (MCO)

Para cuantificar con precisión el impacto neto que los transbordos (medidos a través de la cantidad de etapas) ejercen sobre el tiempo total de traslado de los usuarios en la región metropolitana, se estimó el modelo de regresión multivariable a nivel de microdatos individuales. Los resultados de la regresión por Mínimos Cuadrados Ordinarios (MCO) sobre los 4.823.278 viajes válidos se resumen en la siguiente tabla:

| Variable Independiente | Coeficiente ($\beta$) | Error Estándar | Estadístico $t$ | $p$-value |
| :--- | :---: | :---: | :---: | :---: |
| **Intercepto ($\beta_0$)** | `-297.2490` | `15.9821` | `-18.599` | `< 0.0001` |
| **Cantidad de Etapas ($\beta_1$)** | **`42.1997`** | `0.0476` | **`886.061`** | **`< 0.0001`** |
| **Distancia (km) ($\beta_2$)** | `0.6191` | `0.0031` | `203.006` | `< 0.0001` |
| **Densidad Oferta Origen ($\beta_3$)** | `0.1716` | `0.0042` | `40.409` | `< 0.0001` |
| **Latitud Origen ($\beta_4$)** | `-2.6064` | `0.2507` | `-10.396` | `< 0.0001` |
| **Longitud Origen ($\beta_5$)** | `-3.1693` | `0.1649` | `-19.224` | `< 0.0001` |

*Nota: $R^2 = 0.1956$ ($F$-statistic sumamente alto, $p < 0.0001$). Coeficientes redondeados a 4 decimales.*

### Discusión del Modelo y Penalización Temporal Neto

El análisis de los coeficientes estimados revela dinámicas cruciales sobre la fricción de movilidad en el AMBA:

1.  **La Magnitud de la Penalización por Transbordo ($\beta_1$)**:
    El coeficiente de la **Cantidad de Etapas es de 42.20 minutos** (con un error estándar ínfimo de 0.048 minutos y un estadístico $t$ de 886.1). Esto significa que, **controlando por la distancia física del trayecto, la densidad de paradas en el origen y la localización geográfica, cada transbordo adicional penaliza al usuario agregando en promedio 42.2 minutos a la duración de su viaje**.
2.  **El Efecto de la Distancia y Controles Geográficos**:
    Cada kilómetro adicional de distancia lineal en el mapa aporta **0.62 minutos** de viaje promedio (equivalente a una velocidad comercial en viaje continuo de ~97 km/h, coherente con el modo ferroviario interurbano troncalizado). Las coordenadas geográficas son altamente significativas y muestran las asimetrías de congestión y velocidad de los diferentes corredores de la metrópoli.

Este modelo de regresión valida estadísticamente que la intermodalidad forzada actúa como el principal vector de fricción temporal en la movilidad urbana del AMBA, penalizando desproporcionadamente a los habitantes de la periferia que dependen de múltiples combinaciones de transporte público.

## Sensibilidad Multiescala y Agregación de Voronoi (MAUP)

El análisis multiescala comparativo entre las grillas H3 (resoluciones 7, 8, 9, 10) y la agregación centrada en paradas físicas mediante diagramas de Voronoi de paradas ilustra el impacto del Efecto de la Unidad de Área Modificable (MAUP) sobre los indicadores de equidad en transporte:

| Escala de Análisis | Nodos Activos ($V$) | Enlaces Estables ($E$) | Spearman $r$ (TS vs Cercanía) | Spearman $r$ (TS vs IFI) | Spearman $r$ (TS vs Speed) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **H3 Res 7** (Comunal) | `475` | `4628` | `-0.6505` | `0.2982` | `-0.2940` |
| **H3 Res 8** (Barrial) | `534` | `2292` | `-0.6371` | `0.4367` | `-0.5203` |
| **H3 Res 9** (Micro-urbano) | `264` | `1391` | `-0.6661` | `-0.1313` | `-0.0483` |
| **H3 Res 10** (Esquinas) | `243` | `1277` | `-0.4916` | `-0.3721` | `0.2541` |
| **Voronoi Paradas** (Infraestructura) | `234` | `1202` | `-0.3509` | `-0.5151` | `0.4199` |

### Discusión del Efecto de Escala
Los resultados comparativos demuestran comportamientos divergentes según la escala geográfica:
1.  **Estabilidad de la Cercanía (Accesibilidad macro)**: La correlación negativa entre la Tarifa Social y la centralidad de cercanía se mantiene robusta y altamente significativa en todas las escalas territoriales (oscilando entre $-0.3509$ y $-0.6661$). Esto confirma que el aislamiento de los sectores vulnerables es una propiedad estructural robusta e independiente del método de discretización espacial.
2.  **Sensibilidad del IFI (Fricción local)**: La correlación con la fricción espacial (IFI) es fuertemente positiva en resoluciones macro y barriales (Res 7 y 8), pero se debilita y revierte a valores negativos en escalas de micro-grilla (Res 9, Res 10) y Voronoi de paradas. Esto revela que el IFI, al ser una métrica de escala local (etapas/distancia), sufre una gran dispersión individual cuando las zonas son sumamente pequeñas (donde trayectos muy largos de la periferia a nivel de parada tienen un IFI bajo, ocultando el patrón geográfico regional). La grilla H3 de Resolución 8 emerge así como el compromiso ideal de agregación territorial para modelar la equidad espacial de los transbordos.

## Perfiles de Fricción Identificados por Clustering

La aplicación del algoritmo HDBSCAN sobre el espacio $[IFI, IFT, Distancia]$ agrupó los viajes en tres perfiles representativos que reflejan la desigualdad en la fricción de movilidad:

1.  **Perfil de Larga Distancia Eficiente (Clúster 1)**: Viajes con distancias largas, bajo IFI y bajo IFT. Corresponden a trayectos directos utilizando el tren como modo troncal de alta velocidad.
2.  **Perfil de Intermodalidad Forzada (Clúster 2)**: Viajes con distancias cortas/medias, alto IFI y alto IFT. Concentra los traslados ineficientes de colectivos barriales conectando con trenes en la periferia. Este clúster presenta una alta concentración de orígenes en los municipios vulnerables de PBA.
3.  **Perfil de Ineficiencia Temporal por Congestión (Clúster 3)**: Desplazamientos cortos con duraciones de viaje extremadamente largas y velocidades comerciales muy bajas. Refleja los problemas de fricción por tráfico en colectivos urbanos sin vías exclusivas.
