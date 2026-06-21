# Matriz Origen-Destino de Transporte Público y Análisis de Fricción, Vulnerabilidad y Redes (RMBA)

Este repositorio contiene los datos, códigos y metodologías del estudio de la **Matriz de Origen-Destino (OD)** para la **Región Metropolitana de Buenos Aires (RMBA)** en base a transacciones SUBE representativas de un día miércoles de noviembre de 2019. Asimismo, incorpora análisis avanzados desarrollados para profundizar el estudio del transporte en el AMBA a través de índices de fricción, modelos de vulnerabilidad socio-espacial, teoría de redes multiescala y regresión econométrica.

---

## 📄 Informes y Reportes del Proyecto

- **[Informe Metodológico Original (PDF)](file:///home/augusto/Desktop/Matriz-Origen-Destino-Transporte-Publico/informe/Matriz%20OD%20de%20Transporte%20Publico%20en%20base%20a%20datos%20SUBE.pdf)**: Detalle del desarrollo de la Matriz OD, imputación de destinos y procesamiento espacial en bases de datos.
- **[Informe de Fricción e Intermodalidad en el AMBA (PDF)](file:///home/augusto/Desktop/Matriz-Origen-Destino-Transporte-Publico/resultados/Fricción%20e%20Intermodalidad%20en%20el%20AMBA.pdf)**: Reporte que amplía la investigación analizando la fricción espacial y temporal, vulnerabilidad de red y regresiones multivariables.
- **[Análisis de Distribución de Fricción (Markdown)](file:///home/augusto/Desktop/Matriz-Origen-Destino-Transporte-Publico/documentos/analisis_ifi_ift.md)**: Reporte estadístico pormenorizado de los índices IFI e IFT por jurisdicción de viaje.

---

## 📂 Estructura del Repositorio

El repositorio está organizado de la siguiente manera:

```text
├── CODE_OF_CONDUCT.md
├── LICENSE.md
├── README.md
├── TPS/
│   └── (Scripts y utilidades adicionales)
├── data/                                      # Insumos y bases de datos iniciales
│   ├── paradas.csv                            # Paradas georreferenciadas con ID y celda H3
│   ├── lineas_ramales.csv                     # Definición de líneas y ramales de transporte público
│   ├── indices_h3.csv                         # Celdas H3 con información socio-jurisdiccional
│   └── transacciones.csv                      # Microdatos anonimizados de transacciones SUBE
├── documentos/                                # Documentación de los nuevos análisis
│   └── analisis_ifi_ift.md                    # Reporte del análisis de distribución de IFI e IFT
├── informe/                                   # Informe original
│   └── Matriz OD de Transporte Publico en base a datos SUBE.pdf
├── notebooks/                                 # Notebooks interactivos de Jupyter
│   ├── EDA.ipynb                              # Análisis exploratorio original
│   └── EDA-duck.ipynb                         # Análisis exploratorio optimizado (DuckDB) con red de vulnerabilidad
├── queries/                                   # Scripts SQL para construir la Matriz OD (PostgreSQL)
│   ├── 1_crear_tablas_principales.sql         # Inicialización de tablas y copia de CSVs
│   ├── 2_construir_etapas.sql                 # Construcción de etapas de viajes por tarjeta
│   ├── 3_imputar_destinos.sql                 # Imputación espacial de destinos ausentes
│   └── 4_construir_tablas_viajes_tarjetas.sql # Consolidación de viajes y agregaciones por tarjeta
├── resultados/                                # Salidas de datos y reportes de la investigación
│   ├── Fricción e Intermodalidad en el AMBA.pdf
│   ├── etapas.csv                             # Estructura del dataset final de etapas
│   ├── viajes.csv                             # Estructura del dataset final de viajes consolidado
│   ├── tarjetas.csv                           # Estructura del dataset de tarjetas agregadas
│   ├── metricas_vulnerabilidad_red.csv        # Métricas de vulnerabilidad e índices de red por celda H3
│   ├── metricas_vulnerabilidad_voronoi.csv    # Métricas de vulnerabilidad e índices a nivel de paradas (Voronoi)
│   ├── comparacion_escalas_h3.csv             # Tabla comparativa de correlaciones entre escalas (H3 7-10 y Voronoi)
│   ├── regresion_ols.csv                      # Resultados del modelado lineal multivariable por OLS
│   ├── estadisticas_IFI.csv                   # Estadísticas descriptivas del Índice de Fricción Espacial
│   ├── estadisticas_IFT.csv                   # Estadísticas descriptivas del Índice de Fricción Temporal
│   ├── distribucion_boxplot_ifi_ift.png       # Boxplot de comparación de fricción
│   ├── distribucion_densidad_ifi_ift.png      # Curva de densidad continua de IFI e IFT
│   └── visualizaciones/                       # Visualizaciones y mapas interactivos en HTML
│       ├── figura1_intermodalidad.png ...
│       ├── figura14_vulnerabilidad_sql.html   # Mapa interactivo de IVSE en H3 Res 8
│       ├── figura15_cercania_red.html         # Mapa interactivo de Cercanía en H3 Res 8
│       ├── figura16_intermediacion_red.html   # Mapa interactivo de Intermediación en H3 Res 8
│       ├── figura17_vulnerabilidad_voronoi.html # Mapa interactivo de IVSE en polígonos de Voronoi
│       └── figura18_cercania_voronoi.html     # Mapa interactivo de Cercanía en polígonos de Voronoi
└── scripts/                                   # Códigos en Python para el procesamiento avanzado
    ├── analizar_distribucion.py               # Generación de estadísticas y figuras de IFI/IFT
    ├── analisis_vulnerabilidad_red.py         # Análisis de redes multiescala, Voronoi y regresión OLS
    └── integrate_vulnerability.py             # Integración del análisis en el notebook de Jupyter
```

---

## 🛠️ Insumos y Procesamiento Base (Matriz OD)

Los datos de transacciones SUBE provienen de un pedido de acceso a la información pública (*expediente EX - 2020 - 32945006 - DNAIP#AAIP*). 
- **Privacidad y Seguridad**: Para proteger los datos personales, se enmascaró el identificador de la tarjeta y los números de internos de los colectivos. La información espacial se truncó a tres decimales (margen de error de ~100m) y la temporal se agrupó a nivel de hora (sin minutos).
- **Herramientas de Procesamiento**: La matriz base se computa utilizando **PostgreSQL + PostGIS** junto con la infraestructura de celdas hexagonales de **Uber H3**, empleando los bindings de [h3-pg](https://github.com/bytesandbrains/h3-pg).
- Los scripts localizados en `queries/` toman `transacciones.csv`, `paradas.csv` y `lineas_ramales.csv` como insumos primarios para estructurar las etapas de viaje, imputar coordenadas de destino y consolidar las tablas de viajes.

---

## 📈 Metodologías de los Nuevos Análisis

### 1. Índices de Fricción del Viaje
Para cuantificar la complejidad e intermodalidad del transporte en la RMBA, se definieron dos índices aplicados a los viajes:

- **Índice de Fricción Espacial (IFI)**: Representa el número de transbordos por cada 10 km de viaje lineal.
  $$\text{IFI} = \frac{\text{cantidad de etapas}}{\text{distancia en km}} \times 10$$
- **Índice de Fricción Temporal (IFT)**: Mide el número de transbordos por unidad de hora de viaje.
  $$\text{IFT} = \frac{\text{cantidad de etapas}}{\text{duración en horas}}$$

Los viajes son clasificados según su recorrido jurisdiccional en: **Intra-CABA**, **Intra-PBA**, **PBA-CABA** (ida de conmuters) y **CABA-PBA** (vuelta de conmuters).

### 2. Índice de Vulnerabilidad Socio-Espacial (IVSE)
El IVSE identifica las zonas donde convergen la desventaja social de los usuarios y la ineficiencia espacial del sistema de transporte:
$$\text{IVSE} = \text{ts}_{\text{norm}} \times \text{ifi}_{\text{norm}}$$
- $\text{ts}_{\text{norm}}$: Proporción de viajes que hacen uso de **Tarifa Social / Subsidio** en la celda de origen (normalizado de 0 a 1).
- $\text{ifi}_{\text{norm}}$: Mediana del **IFI** en la celda de origen (normalizado de 0 a 1).

### 3. Teoría de Redes y Centralidades Estructurales
Se construye un grafo dirigido y ponderado $G(V, E)$ donde los nodos $V$ representan ubicaciones geográficas y las aristas $E$ representan los flujos de viaje estables de transporte público. El peso de las aristas está determinado por la duración promedio del viaje. 

Se evalúan dos centralidades fundamentales para medir la accesibilidad estructural:
- **Centralidad de Cercanía (Closeness Centrality)**: Mide la eficiencia y rapidez con la que se puede acceder desde un nodo al resto de la red.
- **Centralidad de Intermediación (Betweenness Centrality)**: Evalúa los nodos que actúan como "puentes" estratégicos o hubs de la red de transporte.

El análisis de red se realiza de manera **multiescala**:
- **Escala Hexagonal H3**: A resoluciones espaciales de 7 (regiones amplias), 8 (escala representativa), 9 y 10 (microescala).
- **Escala de Paradas de Transporte**: Agrupando el espacio mediante **polígonos de Voronoi** construidos a partir de las coordenadas físicas de las paradas.

### 4. Modelo de Regresión Multivariable (OLS)
Se estimó un modelo econométrico de mínimos cuadrados ordinarios para cuantificar la influencia de variables espaciales y de tránsito sobre la duración del viaje:
$$\text{duración}_{\text{minutos}} = \beta_0 + \beta_1 \cdot \text{etapas} + \beta_2 \cdot \text{distancia} + \beta_3 \cdot \text{densidad}_{\text{paradas}} + \beta_4 \cdot \text{lat}_o + \beta_5 \cdot \text{lon}_o + \epsilon$$
Donde `stops_density_o` representa la densidad de paradas en la celda H3 de origen y `lat_o`/`lon_o` capturan el efecto geográfico centro-periferia.

---

## 💻 Guía de Usuario y Reproducción

### Requisitos Previos
1. **Base de Datos**: PostgreSQL 12+ con PostGIS y la extensión `h3-pg` instalados.
2. **Python**: Python 3.9+ con los siguientes paquetes (instalables vía `pip install`):
   ```bash
   pip install duckdb pandas numpy matplotlib seaborn plotly networkx h3 geopandas shapely
   ```

### Paso 1: Reproducción de la Matriz OD (SQL)
1. Cree una base de datos en su servidor PostgreSQL.
2. Abra `queries/1_crear_tablas_principales.sql`, reemplace el marcador `[PATH]` por la ruta absoluta de este repositorio en su disco y ejecute el script. Esto creará el esquema y cargará las tablas ubicadas en `data/` y `resultados/`.
3. Ejecute secuencialmente los siguientes scripts en la base de datos:
   - `queries/2_construir_etapas.sql`
   - `queries/3_imputar_destinos.sql`
   - `queries/4_construir_tablas_viajes_tarjetas.sql`

### Paso 2: Ejecución del Análisis Avanzado (Python)
Una vez generadas las tablas en `resultados/` y `data/`, puede ejecutar el flujo analítico completo:

1. **Análisis de Fricción**: Ejecute el script para computar las estadísticas y gráficos descriptivos de IFI/IFT:
   ```bash
   python scripts/analizar_distribucion.py
   ```
2. **Análisis de Vulnerabilidad y Redes**: Ejecute el script integral para construir las matrices de grafos H3, los diagramas de Voronoi y estimar la regresión OLS:
   ```bash
   python scripts/analisis_vulnerabilidad_red.py
   ```
   *Este script guardará múltiples archivos CSV en `resultados/` y mapas interactivos listos para abrir en el navegador dentro de `resultados/visualizaciones/`.*
3. **Actualización de Notebooks**: Si desea integrar de forma interactiva estos resultados en el entorno de desarrollo, ejecute:
   ```bash
   python scripts/integrate_vulnerability.py
   ```
   Luego abra Jupyter y examine `notebooks/EDA-duck.ipynb`.

---

## 📄 Licencia

Copyright© 2022. Banco Interamericano de Desarrollo ("BID"). Uso autorizado. [AM-331-A3](/LICENSE.md)

---

## 👥 Autores

- **Felipe González** ([@alephcero](https://github.com/alephcero/))
- **Sebastián Anapolsky** ([@sanapolsky](https://github.com/sanapolsky/))

---

## 🤝 Acknowledgments / Reconocimientos

**Copyright © [2025]. Inter-American Development Bank ("IDB"). Authorized Use.**  
The procedures and results obtained based on the execution of this software are those programmed by the developers and do not necessarily reflect the views of the IDB, its Board of Executive Directors or the countries it represents.

**Copyright © [2025]. Banco Interamericano de Desarrollo ("BID"). Uso Autorizado.**  
Los procedimientos y resultados obtenidos con la ejecución de este software son los programados por los desarrolladores y no reflejan necesariamente las opiniones del BID, su Directorio Ejecutivo ni los países que representa.

### Support and Usage Documentation / Documentación de Soporte y Uso

**Copyright © [2025]. Inter-American Development Bank ("IDB").** The Support and Usage Documentation is licensed under the Creative Commons License CC-BY 4.0 license. The opinions expressed in the Support and Usage Documentation are those of its authors and do not necessarily reflect the opinions of the IDB, its Board of Executive Directors, or the countries it represents.

**Copyright © [2025]. Banco Interamericano de Desarrollo (BID).** La Documentación de Soporte y Uso está licenciada bajo la licencia Creative Commons CC-BY 4.0. Las opiniones expresadas en la Documentación de Soporte y Uso son las de sus autores y no reflejan necesariamente las opiniones del BID, su Directorio Ejecutivo ni los países que representa.
