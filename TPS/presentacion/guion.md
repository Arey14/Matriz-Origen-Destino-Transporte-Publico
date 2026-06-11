# Guión de Defensa y Resumen Ejecutivo de la Tesis

Este documento detalla, de principio a fin, el desarrollo metodológico y los resultados científicos de la tesis **"Matriz Origen-Destino de Transporte Público en base a datos SUBE"** en el Área Metropolitana de Buenos Aires (AMBA). Sirve tanto de guía de estudio para el autor como de soporte explicativo (guión) para la defensa del trabajo.

---

## 1. INTRODUCCIÓN Y CONTEXTO METROPOLITANO

### El Escenario: La Asimetría Estructural del AMBA
El Área Metropolitana de Buenos Aires (AMBA) es una de las megaciudades más pobladas de América Latina. Su estructura territorial presenta una profunda asimetría socioeconómica e institucional:
*   **El Centro (CABA)**: Concentra la mayor densidad de empleo formal, infraestructura de servicios públicos y alternativas de transporte rápido (líneas de subtes, metrobuses y cabeceras de trenes).
*   **La Periferia (Conurbano Bonaerense - PBA)**: Alberga a la mayor cantidad de población, pero con una red de transporte público fragmentada, de baja densidad transversal y de configuración eminentemente radial.

### El Problema: La Intermodalidad Forzada
Debido a esta asimetría, millones de ciudadanos de bajos recursos que residen en los cordones periféricos del conurbano se ven obligados a realizar extensos viajes diarios para trabajar en la Ciudad. Ante la falta de recorridos de colectivos directos o transversales de larga distancia, los usuarios se ven obligados a realizar **transbordos forzados** (encadenando, por ejemplo, colectivo local $\to$ tren de cercanías $\to$ colectivo/subte final). 

En sistemas planificados, la intermodalidad es un indicador de eficiencia. En el AMBA, se manifiesta como una **fricción impuesta** por baja cobertura territorial, traduciéndose en una penalización sistemática en tiempo, comodidad e ingresos para los sectores de menores recursos.

### La Pregunta de Investigación
> **¿En qué medida la intermodalidad forzada en el cordón externo del AMBA actúa como un factor de fricción espacial y temporal que penaliza el acceso de los usuarios en comparación con el centro urbano, y cómo se alinea esta ineficiencia estructural con la vulnerabilidad socioeconómica de los pasajeros?**

---

## 2. INGESTIÓN DE DATOS Y CONFIGURACIÓN TECNOLÓGICA

Para modelar la movilidad a escala metropolitana, se procesó una muestra masiva consolidada de un día hábil representativo (noviembre de 2019) provista por el Banco Interamericano de Desarrollo (BID) en base al sistema transaccional de la tarjeta SUBE:

### Los Datasets Principales:
1.  **Etapas (`etapas.csv` - ~9.17 millones de filas)**: Cada transacción individual realizada por un usuario al abordar un vehículo (tap-in). Contiene la tarjeta anonimizada, la georreferenciación (latitud/longitud) del origen, la georreferenciación estimada del destino, la hora nominal y el tipo de tarifa aplicada.
2.  **Viajes (`viajes.csv` - ~6.50 millones de filas)**: Viajes completos consolidados que pueden constar de 1 o más etapas de transbordo consecutivas.
3.  **Paradas (`paradas.csv` - ~146.000 filas)**: Inventario georreferenciado de todas las paradas y estaciones de colectivos, trenes y subtes.
4.  **Zonas (`indices_h3.csv` - ~49.500 filas)**: Catálogo de correspondencia entre celdas H3 (grilla de indexación espacial de Uber) y los radios censales del INDEC (2010), asociando a cada celda con su provincia o comuna jurisdiccional.

### La Infraestructura de Datos (DuckDB + Python)
Dado el peso de los archivos brutos, se implementó una base de datos columnar en memoria utilizando **DuckDB**. La elección de esta tecnología se fundamenta en su capacidad para ejecutar consultas SQL a nivel de millones de registros en segundos, cargando extensiones nativas como `spatial` (para cálculos de geometría) y `h3` (para indexación espacial rápida). El procesamiento principal y el cálculo de grafos se implementó en Python con las librerías `pandas`, `geopandas`, `networkx` y `shapely`.

---

## 3. IDENTIFICACIÓN DE LIMITACIONES CRÍTICAS Y MEJORAS IMPLEMENTADAS

Al iniciar el análisis descriptivo del dataset original, se detectaron tres puntos débiles metodológicos que distorsionaban los resultados. Para resolverlos, se implementaron tres mejoras científicas:

### MEJORA 1: Imputación Temporal Fraccionaria (GTFS + Haversine)
*   **La Limitación Original**: El sistema SUBE solo registra la marca horaria en horas enteras nominales (de 0 a 23). Cuando un usuario realizaba un viaje corto que iniciaba y finalizaba dentro de la misma hora nominal (viaje intra-horario), la duración del viaje en la base de datos figuraba como 0 horas. Los estudios anteriores le asignaban a estos viajes una duración plana de 30 minutos ($0.5$ h). Esto aplanaba la variabilidad temporal y distorsionaba por completo el cálculo de velocidades.
*   **La Solución**: Calibramos velocidades físicas teóricas medias y tiempos de acceso/espera promedio para cada modo de transporte mediante el análisis de datos de programación estandarizada (GTFS) del AMBA (Colectivo: 15 km/h + 0.08h de acceso; Subte: 25 km/h + 0.08h; Tren: 35 km/h + 0.15h). Formulamos una imputación temporal adaptativa: la duración del viaje se calcula dividiendo la distancia Haversine real por la velocidad del modo implicado, añadiendo el tiempo de transbordo correspondiente. 
*   **Por qué**: Restablece el realismo de los tiempos de viaje a nivel de minutos para tramos cortos y medianos, permitiendo analizar velocidades comerciales reales.

### MEJORA 2: Reconstrucción Semanal Longitudinal de Tarjetas
*   **La Limitación Original**: El algoritmo tradicional de Munizaga de inferencia de destinos funciona sobre ventanas diarias aisladas. Al terminar el día, los viajes de regreso a casa por la tarde o la noche quedaban como viajes "huérfanos" (sin destino conocido) porque el sistema no detectaba transacciones posteriores en el mismo bloque diario.
*   **La Solución**: Escribimos un algoritmo en Python paralelizado (diseñado para ejecutarse de forma eficiente en tu servidor con 32 hilos y 128 GB de RAM) que procesó el historial continuo de transacciones de cada tarjeta durante una ventana de 7 días. Con este histórico longitudinal, identificamos la parada más recurrente de origen para cada tarjeta, definiendo su **"Hogar/Pernocte usual"**. Los viajes vespertinos sin destino conocido se cerraron automáticamente imputándoles como destino esta parada base.
*   **Por qué**: Resolvió los viajes huérfanos nocturnos e incrementó la muestra de viajes válidos a **7.17 millones de viajes** (un aumento neto del 30.2% frente a la base diaria de 5.50 millones).

### MEJORA 3: Sensibilidad Espacial (H3 Multiescala y Voronoi de Paradas)
*   **La Limitación Original**: Agrupar los desplazamientos en una única división espacial barrial puede introducir sesgos estadísticos debido al Problema de la Unidad de Área Modificable (MAUP).
*   **La Solución**: Modificamos el pipeline de red y correlaciones para evaluar la sensibilidad espacial en 5 niveles de agregación territorial concurrentes:
    1.  **H3 Resolución 7** (~5.2 $km^2$): Escala Comunal.
    2.  **H3 Resolución 8** (~0.74 $km^2$): Escala Barrial (referencia).
    3.  **H3 Resolución 9** (~0.1 $km^2$): Escala Micro-urbana.
    4.  **H3 Resolución 10** (~0.015 $km^2$): Escala de Esquinas.
    5.  **Voronoi de Paradas**: Diagramas de Voronoi construidos a partir de la localización física de las paradas de colectivos y estaciones reales.

---

## 4. FORMULACIÓN DE LOS ÍNDICES DE FRICCIÓN DE VIAJE

Para caracterizar el esfuerzo exigido a los usuarios, formalizamos tres métricas cuantitativas clave:

### 1. Índice de Fricción Espacial (IFI)
Representa la intensidad de los transbordos obligados en relación a la distancia en línea recta recorrida (Haversine):
$$\text{IFI} = \frac{\text{cantidad\_etapas}}{\text{distancia\_km}} \times 10$$
*   *Interpretación*: Cantidad de etapas de viaje (transbordos + 1) que un usuario debe encadenar por cada 10 kilómetros recorridos en línea recta.

### 2. Índice de Fricción Temporal (IFT)
Mide la tasa temporal de etapas por unidad de tiempo:
$$\text{IFT} = \frac{\text{cantidad\_etapas}}{\text{duracion\_horas}}$$
*   *Interpretación*: Cantidad de transbordos experimentados por cada hora de viaje realizada.

### 3. Modelo de Regresión Multivariable (MCO)
Para medir la penalización temporal neta añadida al viaje por cada transbordo, estimamos un modelo de mínimos cuadrados ordinarios a nivel de microdatos sobre los 4.82 millones de viajes válidos:
$$\text{Duración}_i = \beta_0 + \beta_1 \text{Etapas}_i + \beta_2 \text{Distancia}_i + \beta_3 \text{Densidad}_i + \beta_4 \text{Lat}_i + \beta_5 \text{Lon}_i + \epsilon_i$$
Donde el coeficiente $\beta_1$ representa el tiempo neto promedio (en minutos) que añade cada transbordo adicional.

---

## 5. CONTROL DE CALIDAD GEOGRÁFICA (LIMPIEZA DE COSTAS Y URUGUAY)

Durante la renderización inicial de los mapas territoriales, se detectaron dos incoherencias geográficas que restaban validez científica al trabajo:
1.  **Eventos fantasma en Uruguay**: La presencia de 2 transacciones con drift (desviación) severo de señal GPS registraba actividad física en medio de Uruguay, generando el hexágono barrial `88c2c4a621fffff` en territorio extranjero.
2.  **Voronoi sobre el Río de la Plata**: Dado que las paradas costeras de Berisso, Ensenada o Quilmes no tienen paradas vecinas hacia el río, el algoritmo de Voronoi extendía sus áreas de atracción infinitamente a través del agua, cruzando el Río de la Plata hasta tocar la costa uruguaya.

### La Solución Implementada:
1.  **Filtro Land Boundary**: Construimos un contorno geométrico de tierra firme (`land_boundary` como un MultiPolygon) uniendo únicamente las celdas H3 activas correspondientes a radios censales terrestres continentales de `data/indices_h3.csv`.
2.  **Descarte H3**: Implementamos un filtro espacial que calcula el centroide de cada celda y descarta todas aquellas que caen fuera de los límites continentales definidos. Esto eliminó de raíz la celda de Uruguay `88c2c4a621fffff` y las celdas fantasma del río.
3.  **Recorte Voronoi**: Intersecamos geométricamente cada celda espacial de Voronoi con la máscara de tierra continental (`land_boundary`) y filtramos únicamente los componentes poligonales tridimensionales (descartando líneas o puntos resultantes en los bordes). Esto limitó los Voronoi de paradas costeras estrictamente al contorno costero real del AMBA.

---

## 6. COMPENDIO Y ANÁLISIS DE LAS 18 FIGURAS DE LA TESIS

A continuación se detalla el catálogo completo de las 18 figuras generadas por el pipeline de análisis de la tesis, divididas por bloques temáticos. Cada una incluye su descripción técnica, los datos empíricos clave y su interpretación urbana para la defensa:

### Bloque A: Análisis Exploratorio de Datos (AED) y Composición de Viaje (Figuras 1 a 5)
*   **Figura 1: Porcentaje de viajes según cantidad de etapas por zona geográfica (Gráfico de barras).**
    *   *Descripción*: Muestra la proporción de viajes compuestos por 1, 2 y 3 o más etapas (transbordos + 1) divididos por jurisdicción (Intra-CABA, Intra-PBA, CABA-PBA).
    *   *Interpretación*: Evidencia de manera directa la ineficiencia interjurisdiccional. En Intra-CABA el 84.8% de los viajes son directos (1 etapa) debido a la densidad de la red. En contraste, en los viajes de conmuters (CABA-PBA), solo el 53.4% viaja sin transbordar, el 37.8% requiere 2 etapas y el 8.8% realiza 3 o más etapas. Esto consolida empíricamente que la intermodalidad es un "peaje físico" forzado para acceder desde la periferia al centro del empleo.
*   **Figura 2: Distribución de distancias de viaje según zona geográfica (Boxplot).**
    *   *Descripción*: Distribución estadística de distancias en línea recta (Haversine en kilómetros) calculadas entre la parada de origen real y la parada de destino inferida.
    *   *Interpretación*: Ilustra la asimetría en la huella espacial metropolitana. Mientras los desplazamientos internos son cortos (mediana de 4.01 km para Intra-CABA y 4.00 km para Intra-PBA), los viajes interjurisdiccionales (CABA-PBA) promedian **18.17 km** (mediana de 16.62 km). Revela la magnitud del desplazamiento pendular diario de larga distancia que soporta la infraestructura de conexión de la Provincia.
*   **Figura 3: Composición modal de viajes por jurisdicción (Gráfico de barras apiladas).**
    *   *Descripción*: Desglose de las combinaciones de modos (Colectivo, Tren, Subte y combinaciones multimodales) según la geografía del viaje.
    *   *Interpretación*: Expone la dependencia del colectivo de superficie en el Conurbano (82.5% de los viajes Intra-PBA son "Solo Colectivo"). En cambio, los trayectos CABA-PBA obligan a la multimodalidad con el ferrocarril como columna vertebral (17.8% Colectivo + Tren, 6.6% Tren + Subte, 4.7% Colectivo + Subte). Los transbordos no son una preferencia de los usuarios, sino un requisito técnico para conectar redes desconectadas.
*   **Figura 4: Distribución de Tarifa Social vs Plena por Jurisdicción (Gráfico de barras).**
    *   *Descripción*: Compara el perfil socioeconómico de los usuarios basándose en el tipo de franquicia registrada en la tarjeta SUBE (Tarifa Social con 55% de descuento federal frente a Tarifa Plena) por origen del viaje.
    *   *Interpretación*: Revela la geografía de la vulnerabilidad. El uso de la Tarifa Social se duplica en el Conurbano profundo (**41.1%** en Intra-PBA) en comparación con el núcleo de la Ciudad de Buenos Aires (**19.6%** en Intra-CABA). Esto demuestra que las zonas periféricas albergan a la población con menor capacidad de pago y mayor dependencia de la asistencia estatal.
*   **Figura 5: Volumen de Etapas según Tipo de Tarifa Específica (Gráfico horizontal).**
    *   *Descripción*: Desglose del total de etapas del set de datos clasificadas por tipo de subsidio específico (Jubilado, AUH, Monotributista Social, Personal de Trabajo Doméstico, Estudiantes, etc.).
    *   *Interpretación*: Permite identificar la fricción sufrida por grupos especialmente vulnerables. Por ejemplo, la categoría de *Personal de Trabajo Doméstico* registra un promedio de etapas por viaje de **1.48**, muy por encima del 1.32 de la *Tarifa Plena*. Esto demuestra empíricamente que los trabajadores de menores ingresos en el sector de servicios informales o domésticos experimentan una mayor fragmentación física en sus trayectos cotidianos.

### Bloque B: Mapas de Densidad Espacial y Dinámicas Metropolitanas (Figuras 6 a 11)
*   **Figura 6: Densidad Espacial de Transacciones en el AMBA (Mapa interactivo de calor).**
    *   *Descripción*: Representación geoespacial continua basada en la densidad de transacciones de tap-in registradas, optimizada mediante agregación de coordenadas adyacentes con DuckDB para agilizar su renderización.
    *   *Interpretación*: Muestra la hipercentralidad económica y de transporte en el AMBA. Los nodos calientes de máxima intensidad luminosa se concentran sobre los tres grandes centros intermodales ferroviarios (Retiro, Constitución y Once), demostrando cómo el flujo metropolitano es encauzado hacia embudos en el núcleo central.
*   **Figura 7: Densidad de Transacciones en el AMBA en Grilla Hexagonal H3 (Mapa coroplético interactivo).**
    *   *Descripción*: Agregación espacial discreta de las transacciones a nivel de celdas hexagonales H3 en Resolución 8 (~0.74 $km^2$). La escala de colores está saturada al percentil 98 para evitar distorsiones visuales debidas a valores extremadamente atípicos en las grandes terminales.
    *   *Interpretación*: Define de forma discreta la estructura de subcentros del AMBA. Además del eje central de CABA, visibiliza los nodos de alta densidad en el Conurbano (como Lomas de Zamora Centro, Morón Centro, Lanús y San Martín), aportando una base territorial comparable para el planeamiento.
*   **Figura 8: Pulso de Transacciones en el AMBA por Hora (Animación interactiva H3).**
    *   *Descripción*: Representa el flujo dinámico de transacciones en la grilla H3 hora por hora a lo largo de un día hábil representativo.
    *   *Interpretación*: Captura visualmente la respiración urbana del AMBA: el flujo de entrada concentrado por la mañana desde los bordes de la Provincia hacia CABA (6:00 a 9:00 AM) y el reflujo de regreso por la tarde (5:00 a 8:00 PM) hacia las periferias residenciales de PBA.
*   **Figura 9: Flujos Origen-Destino para el Hexágono de Constitución (88c2e3022bfffff) (Mapa interactivo de arcos).**
    *   *Descripción*: Visualización de las líneas de deseo de viaje completo (orígenes y destinos finales) que tienen como punto de transferencia la terminal de Constitución.
    *   *Interpretación*: Expone el rol geográfico de Constitución como el portal de acceso del Conurbano Sur. Se observa cómo miles de usuarios provenientes de celdas en PBA sur son concentrados por la línea de tren Roca y luego se dispersan de forma radial a lo largo del centro y norte de la Capital, evidenciando la dependencia de este hub crítico.
*   **Figura 10: Distribución Geográfica de Todas las Paradas (Mapa de dispersión denso).**
    *   *Descripción*: Mapa interactivo con la ubicación georreferenciada de las 145,999 paradas físicas de colectivo, estaciones de tren y bocas de subte en el AMBA.
    *   *Interpretación*: Revela la capilaridad de la infraestructura física. Muestra la gran densidad de cobertura en el primer cordón y CABA frente a la dispersión, la reducción de densidad de paradas y la aparición de "desiertos de tránsito" en el segundo y tercer cordón bonaerense.
*   **Figura 11: Actividad por Hora en Clúster Específico de H3 (Animación a escala micro).**
    *   *Descripción*: Animación temporal interactiva a resolución micro-urbana (H3 Resolución 10) de cuatro hexágonos adyacentes seleccionados en un centro de transferencia.
    *   *Interpretación*: Permite analizar micro-dinámicas de transbordo en el espacio barrial, sirviendo de ejemplo metodológico para evaluar la concentración temporal de pasajeros a nivel de andén u paradas específicas.

### Bloque C: Índices de Fricción Espacio-Temporal (Figuras 12 y 13)
*   **Figura 12: Comparación de Índices de Fricción (IFI y IFT) sin outliers (Diagramas de caja).**
    *   *Descripción*: Compara las distribuciones de los índices de fricción espacial (IFI - etapas por 10 km) y temporal (IFT - etapas por hora) calculados por tipo de viaje, integrando la fórmula de imputación temporal GTFS para corregir el colapso artificial en tramos cortos.
    *   *Interpretación*: La corrección revela la verdadera fricción física y temporal. En el IFI (fricción espacial), los viajes internos (Intra-CABA: mediana 2.67; Intra-PBA: mediana 2.61) registran tasas más altas debido al efecto matemático del denominador de distancia corto. Sin embargo, para el IFT (fricción temporal), las medianas de Intra-CABA (3.08 etapas/hora) e Intra-PBA (2.77 etapas/hora) exponen que la alta densidad de combinaciones cortas devora tiempo rápidamente, mientras que las de PBA-CABA e CABA-PBA se estabilizan en 2.00 etapas por hora pero con una variabilidad y dispersión real (sin colapso a plano), reflejando el peaje temporal persistente de los transbordos.
*   **Figura 13: Curvas de Densidad de Probabilidad de IFI e IFT (KDE por jurisdicción).**
    *   *Descripción*: Estimaciones continuas de densidad de Kernel de la distribución de IFI e IFT filtrando outliers y centrando el zoom en los rangos de máxima representatividad de la muestra.
    *   *Interpretación*: Muestra la forma asimétrica y las colas largas de fricción. En el IFT se visualiza un área de probabilidad significativamente más ancha en el rango de 2 a 3 etapas por hora para los viajes que cruzan al Conurbano (PBA-CABA y CABA-PBA), confirmando de forma continua que el viaje interjurisdiccional expone sistemáticamente al usuario a una mayor fricción temporal.

### Bloque D: Red Metropolitana y Centralidad Estructural H3 (Figuras 14 a 16)
*   **Figura 14: Mapa H3 de Vulnerabilidad Socio-Espacial (IVSE) (Mapa coroplético interactivo H3).**
    *   *Descripción*: Muestra la distribución territorial del IVSE, el cual cruza por celda H3 (Resolución 8) la tasa de Tarifa Social (vulnerabilidad socioeconómica) con la mediana de fricción espacial IFI (postergación de red).
    *   *Interpretación*: Mapea los "desiertos de tránsito vulnerables" del AMBA. Las celdas rojas de máxima vulnerabilidad socio-espacial se agrupan en el segundo y tercer cordón del Conurbano Sur y Oeste (La Matanza, Florencio Varela, Almirante Brown, Merlo, Moreno), identificando áreas prioritarias que necesitan inversión urgente en cobertura directa de transporte.
*   **Figura 15: Mapa H3 de Cercanía Estructural (Accesibilidad en red) (Mapa coroplético interactivo H3).**
    *   *Descripción*: Colorea cada celda H3 según su valor de centralidad de cercanía (`closeness centrality`) calculada sobre el grafo metropolitano y ponderada por los tiempos de viaje en la red de transporte.
    *   *Interpretación*: Expone la brecha de accesibilidad centro-periferia. El centro urbano de CABA y el corredor norte brillan en tonos oscuros/neón de alta centralidad (rápido acceso a toda la red), mientras que las periferias bonaerenses caen en tonos pálidos de bajísima accesibilidad estructural (tiempos de viaje acumulados severos).
*   **Figura 16: Mapa H3 de Intermediación (Betweenness) (Mapa coroplético interactivo H3).**
    *   *Descripción*: Colorea las celdas H3 según su centralidad de intermediación (`betweenness centrality`) ponderada en el grafo de flujo metropolitano.
    *   *Interpretación*: Identifica los hubs de transbordo e intercambiadores críticos que actúan como "puentes" obligados del flujo diario (Retiro, Constitución, Once, Lomas de Zamora Centro, Lanús Centro, Morón Centro, San Martín). Revela la inflexibilidad y el diseño radial de la red: si uno de estos hubs se congestiona o interrumpe, el flujo metropolitano completo sufre demoras severas por falta de rutas alternativas directas o transversales.

### Bloque E: Análisis de Voronoi Centrado en Infraestructura Física (Figuras 17 y 18)
*   **Figura 17: Mapa Voronoi de Vulnerabilidad (IVSE) (Polígonos de Voronoi recortados).**
    *   *Descripción*: Proyección del IVSE sobre los diagramas de Voronoi generados a partir de las paradas físicas del AMBA, perfectamente limitados e intersecados con la línea de tierra continental (eliminando polígonos sobre el agua).
    *   *Interpretación*: Proporciona un análisis directo a nivel de la infraestructura real. Permite identificar de manera precisa cuáles paradas y estaciones de colectivos y trenes en PBA atraen flujos de usuarios vulnerables y experimentan alta fricción local, facilitando intervenciones de diseño de paradas o frecuencias localizadas.
*   **Figura 18: Mapa Voronoi de Cercanía Estructural (Polígonos de Voronoi recortados).**
    *   *Descripción*: Mapa de la centralidad de cercanía (`closeness centrality`) en el grafo de Voronoi de paradas físicas, recortado a los límites terrestres continentales.
    *   *Interpretación*: Corrobora y valida el patrón de aislamiento de la periferia a nivel de infraestructura real. El hecho de que este mapa Voronoi mantenga la misma fuerte diferenciación centro-periferia que el de celdas H3 demuestra que el aislamiento observado no es un artefacto de la malla espacial seleccionada (MAUP), sino una propiedad estructural física innegable de la red de transporte del AMBA.

---

## 7. CONTROL DE CALIDAD GEOGRÁFICA (LIMPIEZA DE COSTAS Y URUGUAY)

Durante la renderización inicial de los mapas territoriales, se detectaron dos incoherencias geográficas que restaban validez científica al trabajo:
1.  **Eventos fantasma en Uruguay**: La presencia de 2 transacciones con drift (desviación) severo de señal GPS registraba actividad física en medio de Uruguay, generando el hexágono barrial `88c2c4a621fffff` en territorio extranjero.
2.  **Voronoi sobre el Río de la Plata**: Dado que las paradas costeras de Berisso, Ensenada o Quilmes no tienen paradas vecinas hacia el río, el algoritmo de Voronoi extendía sus áreas de atracción infinitamente a través del agua, cruzando el Río de la Plata hasta tocar la costa uruguaya.

### La Solución Implementada:
1.  **Filtro Land Boundary**: Construimos un contorno geométrico de tierra firme (`land_boundary` como un MultiPolygon) uniendo únicamente las celdas H3 activas correspondientes a radios censales terrestres continentales de `data/indices_h3.csv`.
2.  **Descarte H3**: Implementamos un filtro espacial que calcula el centroide de cada celda y descarta todas aquellas que caen fuera de los límites continentales definidos. Esto eliminó de raíz la celda de Uruguay `88c2c4a621fffff` y las celdas fantasma del río.
3.  **Recorte Voronoi**: Intersecamos geométricamente cada celda espacial de Voronoi con la máscara de tierra continental (`land_boundary`) y filtramos únicamente los componentes poligonales tridimensionales (descartando líneas o puntos resultantes en los bordes). Esto limitó los Voronoi de paradas costeras estrictamente al contorno costero real del AMBA.

---

## 8. DESCUBRIMIENTOS Y APORTES CIENTÍFICOS PRINCIPALES (DEFENSA DE LA TESIS)

Los resultados empíricos derivados de los pipelines limpios y depurados arrojaron tres conclusiones científicas de alto impacto urbano:

### 1. El Aislamiento Físico y Socioeconómico de la Periferia
El cruce correlacional entre la tasa de Tarifa Social y la centralidad de cercanía ponderada (`closeness centrality` del grafo de la red de transporte) reveló un coeficiente de Spearman de **-0.6371** en la escala barrial (H3 Res 8).
*   *Conclusión*: Existe una relación inversa muy fuerte y estadísticamente significativa. **A mayor vulnerabilidad socioeconómica del barrio de origen, menor es la centralidad del nodo de transporte en el grafo metropolitano**, demostrando un aislamiento estructural sistemático de los sectores más vulnerables de PBA.

### 2. El Peaje Temporal por Transbordo
La estimación del modelo MCO arrojó que el coeficiente de etapas ($\beta_1$) se sitúa en **42.20 minutos** ($p < 0.0001$).
*   *Conclusión*: Controlando por distancia y geografía, **cada transbordo forzado le añade en promedio 42.2 minutos de duración al viaje del usuario**. Este valor es sumamente elevado y expone las graves ineficiencias en los centros de transferencia, las frecuencias de colectivos alimentadores y el diseño de los corredores.

### 3. La Evidencia Empírica del MAUP (Efecto de Escala)
Al comparar las escalas, observamos que mientras la correlación entre Tarifa Social y Cercanía se mantiene estable en todas las escalas (oscilando entre $-0.35$ y $-0.66$), la correlación de la fricción espacial (IFI) **cambia de signo**: es fuertemente positiva en resoluciones macro y barriales (Res 7 y 8, $0.4367$), pero se debilita e invierte a negativa en resoluciones micro (Res 9, 10 y Voronoi).
*   *Conclusión*: A escala barrial/regional, los transbordos están asociados a barrios con alta proporción de Tarifa Social. Sin embargo, a escala de parada individual (Voronoi/Res 10), la gran cantidad de viajes largos originados en la periferia profunda (que registran bajo IFI relativo debido a la larga distancia recorrida) satura las paradas individuales y oculta la ineficiencia regional. Esto valida empíricamente el fenómeno MAUP en el AMBA y consolida a la grilla **H3 Resolución 8** como la escala óptima de planificación.

---

## 9. MAPAS INTERACTIVOS DISPONIBLES EN EL PROYECTO

Durante la exposición, puedes abrir los siguientes archivos HTML interactivos generados en tu navegador para demostrar visualmente los resultados de tu tesis:

### Análisis Exploratorio:
*   **`figura6_mapa_transacciones_optimizado.html`**: Mapa de densidad de calor optimizado por DuckDB que ilustra la concentración masiva de transacciones en el eje de CABA.
*   **`figura7_mapa_h3.html`**: Grilla barrial H3 Res 8 de densidad de transacciones, saturando el color al percentil 98 para evitar distorsiones por outliers.
*   **`figura8_mapa_h3_animado.html`**: Animación interactiva por hora del día que muestra el "pulso" de movilidad del AMBA a lo largo de las 24 horas.

### Red de Movilidad y Centralidad H3 (Escala de Referencia):
*   **`figura14_vulnerabilidad_sql.html`**: Distribución espacial del Índice de Vulnerabilidad Socio-Espacial (IVSE), localizando los "desiertos de tránsito" críticos (zonas en color rojo) en la periferia de PBA.
*   **`figura15_cercania_red.html`**: Centralidad de cercanía de los nodos H3, ilustrando la alta accesibilidad del centro metropolitano y el aislamiento crónico del conurbano profundo.
*   **`figura16_intermediacion_red.html`**: Centralidad de intermediación, señalando los hubs de trasbordo e intercambiadores críticos de la red.

### Análisis Voronoi (Escala de Infraestructura):
*   **`figura17_vulnerabilidad_voronoi.html`**: Mapa interactivo del IVSE agregado a nivel de polígonos de atracción Voronoi alrededor de las paradas físicas reales.
*   **`figura18_cercania_voronoi.html`**: Mapa interactivo de la centralidad de cercanía en el grafo a nivel de Voronoi. Ambos mapas Voronoi están perfectamente recortados a la línea de tierra continental del AMBA, libres de polígonos en el agua.
