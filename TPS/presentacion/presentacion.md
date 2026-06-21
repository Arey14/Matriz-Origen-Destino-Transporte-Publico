---
title: "Matriz de Origen-Destino de Transporte Público"
subtitle: "Presentación de Avances e Integración de Feedback (TP3)"
author: "Augusto Rey"
date: "11 de Junio de 2026"
theme: "metropolis"
aspectratio: 169
header-includes:
  - \usepackage{booktabs}
  - \usepackage{amsmath}
  - \usepackage{graphicx}
---

# Problemática de la Movilidad en el AMBA

\small

### Factores Críticos en el Territorio
- **Fragmentación Espacial**: Crecimiento periférico (PBA) desvinculado del empleo formal centralizado (CABA).
- **Intermodalidad Forzada**: Commuters de la periferia obligados a realizar múltiples combinaciones (colectivo + tren + subte) por falta de recorridos directos.
- **Vulnerabilidad**: Los sectores de menores ingresos sufren la mayor fricción física y económica.

---

# Objetivos Principales del Trabajo

\small

### Metas y Alcances Científicos
1. **Modelado Espacial**: Construir y agregar matrices de viaje origen-destino usando datos masivos SUBE bajo grilla H3 (resolución 8).
2. **Ingeniería de Características**: Formular métricas de ineficiencia de viaje (IFI) e ineficiencia de transbordo (IFT).
3. **Análisis de Redes y Equidad**: Cruzar las centralidades estructurales del grafo de transporte con el porcentaje de Tarifa Social.

---

# Integración de Feedback: Distribución de IFI / IFT

### Hallazgos de la Distribución Jurisdiccional
- **IFI (Ineficiencia de Viaje)**:
  - *Intra-CABA*: Muy baja ineficiencia y distribución concentrada (viajes directos).
  - *Intra-PBA*: Alta dispersión de ineficiencia (rodeos en trayectos periféricos).
  - *PBA-CABA (Interjurisdiccional)*: La ineficiencia media más alta, confirmando el costo físico de ingresar a los corredores radiales.
- **IFT (Fricción de Transbordo)**:
  - El viaje promedio PBA-CABA acumula más de **1.6 transbordos**, frente a solo **0.3** en viajes internos de CABA, reflejando una dependencia estructural extrema de las conexiones.

---

# Distribución de IFI / IFT por Jurisdicción

\begin{figure}[H]
\centering
\includegraphics[width=1.0\textwidth]{resultados/visualizaciones/figura12_boxplot_ifi_ift.png}
\caption{Boxplots descriptivos de IFI y IFT por tipo de flujo de viaje.}
\end{figure}

---

# Integración de Feedback: Métricas de Grafos

\small

### Representación Física en Dijkstra y Centralidades
- **Pesos de Enlace directos (IFI o IFT)**:
  - Representan el "costo" o "fricción" entre hexágonos.
  - Para encontrar el camino de mínimo costo (Dijkstra), los enlaces deben tener el peso directo de **IFI o IFT** (para buscar minimizar el costo acumulado).
- **Significado de las Centralidades**:
  - **Cercanía (Closeness)**: La inversa de la distancia media. Una cercanía *baja* representa aislamiento estructural (mayor costo/dificultad para llegar a ese nodo).
  - **Intermediación (Betweenness)**: Frecuencia de cruce por caminos óptimos. Identifica los grandes cuellos de botella e intercambiadores forzados de la red.

---

# Integración de Feedback: Rol de la Inversa

\small

### Fuerza de Conexión y Facilidad (1/IFI o 1/IFT)
- **Concepto**: Representa la facilidad de movimiento o afinidad de conexión entre zonas.
- **Aplicaciones**:
  - Se utiliza para algoritmos de detección de comunidades (ej. clustering jerárquico de grafos).
  - Análisis de similitud territorial (donde un mayor valor de enlace significa mayor proximidad funcional).

---

# Integración de Feedback: Propósito del Clustering (HDBSCAN)

### ¿Por qué utilizar Clustering Multidimensional?
- **Evitar el análisis univariado**: Permite integrar el IFI, IFT, centralidades (Closeness y Betweenness) y la vulnerabilidad social (Tarifa Social) en un solo perfil territorial.
- **Identificación de Áreas Críticas**: Agrupa orgánicamente hexágonos con deficiencias compartidas en transporte sin forzar límites político-administrativos arbitrarios.
- **Focalización**: Ofrece a los planificadores una guía espacial de dónde dirigir los recursos y subsidios de transporte con mayor urgencia.

---

# Resultados: Análisis de Correlación

\tiny

| Relación Analizada | Pearson ($r$) | Spearman ($\rho$) | Interpretación del Hallazgo |
| :--- | :---: | :---: | :--- |
| **Tarifa Social vs. Cercanía** | **-0.304** | **-0.280** | El aislamiento de red coincide con la vulnerabilidad social. |
| **Tarifa Social vs. IFI** | **+0.357** | **+0.347** | A mayores niveles de pobreza, mayor ineficiencia de viaje. |
| **Tarifa Social vs. IFT** | **+0.321** | **+0.312** | Mayor dependencia e ineficiencia de transbordos periféricos. |

\tiny
*Nota: Todas las correlaciones son significativas con $p < 0.001$.*

---

# Resultados: Modelo de Regresión MCO

\small

### Formulación del Modelo de Regresión
- **Ecuación del Modelo**:
  $$\text{Duración}_i = \beta_0 + \beta_1 \text{Etapas}_i + \beta_2 \text{Distancia}_i + \beta_3 \text{Densidad}_i + \beta_4 \text{Lat}_i + \beta_5 \text{Lon}_i + \epsilon_i$$
- **Estadísticas de Ajuste**:
  - **Muestra ($N$)**: `4,823,278` viajes completos válidos.
  - **R-squared ($R^2$)**: `0.1956` (el modelo explica el 19.56% de la varianza total).
  - **Significancia Global**: Estadístico $F$ altamente significativo ($p < 0.0001$).

---

# Resultados: Coeficientes de Regresión OLS

\footnotesize

### Impacto Neto de las Variables en la Duración (minutos)
- **Cantidad de Etapas ($\beta_1 = +42.20$)**:
  - Cada transbordo adicional añade en promedio **42.2 minutos** de traslado, controlando por distancia física y geografía.
- **Distancia física ($\beta_2 = +0.619$)**:
  - El tiempo de viaje aumenta solo **37 segundos por kilómetro**, lo que confirma que la ineficiencia de transbordo penaliza mucho más que la distancia en línea recta.
- **Densidad de Oferta en Origen ($\beta_3 = +0.172$)**:
  - Un incremento marginal de tiempo por cada parada alternativa en el origen (congestión local).

---

# Resultados: Clusters de Exclusión (HDBSCAN)

\footnotesize

### 1. Clúster 0: Periferia Crítica
- **Características**: Tarifa Social promedio de **45%**, IFI e IFT elevados, cercanía de red extremadamente baja.
- **Localización**: Zonas periféricas de PBA (Florencio Varela, Merlo, Moreno). Máximo aislamiento estructural.

### 2. Clúster 1: Nodos Conectores
- **Características**: Centralidad de intermediación (`betweenness`) máxima.
- **Localización**: Hubs de transferencia críticos (Constitución, Retiro, Once, Lanús, Morón).

---

# Resultados: Cluster Centro Consolidado

\small

### 3. Clúster 2: Centro Consolidado
- **Características**:
  - Tarifa Social muy baja (<15%).
  - Centralidad de cercanía (`closeness`) máxima en el grafo de transporte.
  - Índices de fricción espacial (IFI) y temporal (IFT) mínimos.
- **Localización**: Ciudad de Buenos Aires (CABA), corredor norte y primer cordón oeste del Conurbano.
- **Interpretación**: Acceso rápido y directo a la mayor concentración de empleo.

---

# Perfiles de Exclusión por Clusters

\begin{figure}[H]
\centering
\includegraphics[height=0.6\textheight, keepaspectratio]{resultados/visualizaciones/figura13_densidad_ifi_ift.png}
\caption{Curvas de densidad de probabilidad de IFI y IFT para los clusters obtenidos.}
\end{figure}

---

# Conclusiones y Recomendaciones de Planificación

### Conclusiones
- Se evidencia un patrón socio-espacial claro en el AMBA donde las poblaciones vulnerables pagan el mayor costo físico y de transbordos en su movilidad diaria.
- El análisis estructural de la red de transporte y el clustering multidimensional permiten identificar y priorizar las intervenciones urbanas con base cuantitativa.

### Recomendaciones
1. **Rediseño de Recorridos**: Crear corredores transversales en el conurbano para mitigar el embudo radial hacia CABA.
2. **Mitigación en Nodos**: Mejorar la infraestructura física e información en los Nodos Conectores con alta intermediación.
3. **Subsidios Focalizados**: Direccionar políticas tarifarias adicionales sobre los hexágonos identificados en el *Clúster Periferia Crítica*.

---

# Anexo: Mapa de Flujos y Accesibilidad H3

\begin{figure}[H]
\centering
\includegraphics[height=0.7\textheight, keepaspectratio]{resultados/visualizaciones/Figura7.png}
\caption{Mapa Hexagonal H3 de Transacciones SUBE en el AMBA.}
\end{figure}
