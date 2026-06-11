# Conclusiones y Trabajo Futuro

## Síntesis de los Hallazgos Principales

Esta investigación ha permitido caracterizar y cuantificar de forma sistemática la relación existente entre la inequidad socioeconómica y la ineficiencia de la red de transporte público en el Área Metropolitana de Buenos Aires (AMBA). Los hallazgos empíricos nos permiten arribar a las siguientes conclusiones:

1.  **Validación de la Intermodalidad Forzada**: Se demostró que la necesidad de realizar transbordos en el cordón externo del AMBA no es una opción de eficiencia multimodal elegida por el usuario, sino una fricción espacial forzada debido a la ausencia de recorridos directos. Los conmuters interjurisdiccionales son quienes sufren la mayor penalización temporal de la red, promediando casi 49 minutos por viaje y experimentando una alta densidad de transbordos en sus desplazamientos cotidianos.
2.  **Superposición de Vulnerabilidad Social e Isolation Estructural**: Las métricas de red revelaron una clara correlación negativa entre el ratio de Tarifa Social y la centralidad de cercanía (`closeness centrality`). Este resultado confirma estadísticamente que las zonas residenciales que concentran mayor población vulnerable se encuentran físicamente aisladas en la red de transporte público, sufriendo los mayores tiempos acumulados de viaje para acceder al resto de la metrópolis.
3.  **Fragmentación del Viaje en Sectores Populares**: La correlación positiva entre la Tarifa Social y el Índice de Fricción Espacial (IFI) valida que los usuarios de menores recursos deben encadenar más etapas de viaje por cada unidad de distancia recorrida. Esta fragmentación de viaje representa un costo de fricción adicional transferido al usuario vulnerable, quien compensa las deficiencias de cobertura de la red con su propio tiempo diario disponible.

## Contribuciones a la Planificación del Transporte

La metodología desarrollada en esta tesis, implementada en herramientas de código abierto como DuckDB, NetworkX y H3, ofrece una contribución directa a la planificación y gestión de políticas públicas en el AMBA:

*   **Identificación de Desiertos de Tránsito Vulnerables**: El mapeo del Índice de Vulnerabilidad Socio-Espacial (IVSE) localiza con precisión georeferenciada las zonas críticas en el segundo y tercer cordón conurbano que requieren intervención prioritaria.
*   **Herramienta de Diagnóstico para Recorridos Locales**: La centralidad de intermediación ponderada identificó de manera precisa los hubs tradicionales y cuellos de botella de transbordo obligatorios. Esto provee un insumo clave para que la Comisión Nacional de Regulación del Transporte (CNRT) evalúe la reestructuración de las líneas de colectivos locales en Provincia, promoviendo recorridos tangenciales y alimentadores que reduzcan los transbordos forzados hacia los corredores ferroviarios troncales.
*   **Metodología de Evaluación de Equidad**: El trabajo demuestra que los datos pasivos de tarjetas inteligentes (Smart Card Data) de SUBE pueden ser explotados de manera ágil y masiva para evaluar la equidad social en accesibilidad, pasando de análisis meramente descriptivos de demanda de pasajeros a auditorías estructurales de inclusión territorial.

## Recomendaciones para Futuros Trabajos

Para profundizar en el análisis desarrollado y sortear las limitaciones metodológicas identificadas, se proponen las siguientes líneas de investigación futuras:

*   **Integración de Datos de Programación y GPS (GTFS)**: La incorporación de datos estandarizados sobre las frecuencias planificadas (General Transit Feed Specification - GTFS) y los registros de GPS en tiempo real de los colectivos permitiría cuantificar con precisión los tiempos reales de espera en andenes y paradas, enriqueciendo el cálculo del IFT y del costo en el grafo.
*   **Modelado de Costo Tarifario Real**: Integrar el costo monetario acumulado del viaje multimodal (incorporando los descuentos automáticos por transbordo de la RED SUBE) en la construcción de la red para analizar la fricción económica y evaluar políticas de subsidio tarifario focalizado.
*   **Análisis del Impacto de la Pandemia y Teletrabajo**: Repetir la metodología sobre matrices origen-destino post-pandemia para evaluar si la descentralización del trabajo administrativo en CABA ha reducido la fricción de conmuting de la periferia o si, por el contrario, la brecha de acceso para los trabajadores presenciales vulnerables se ha ampliado.
