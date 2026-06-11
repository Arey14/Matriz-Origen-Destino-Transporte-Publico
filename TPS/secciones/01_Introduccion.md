# Introducción

## Contexto y Motivación Científica

La movilidad urbana es un derecho fundamental que condiciona directamente el acceso de los ciudadanos al empleo, la educación, los servicios de salud y el esparcimiento. En grandes aglomeraciones urbanas, el sistema de transporte público no es solo una infraestructura técnica, sino un motor de inclusión o, por el contrario, un mecanismo de exclusión social. 

El Área Metropolitana de Buenos Aires (AMBA), una de las megaciudades más extensas y pobladas de América Latina, presenta una configuración territorial marcada por una profunda asimetría socioeconómica e institucional. Mientras la Ciudad Autónoma de Buenos Aires (CABA) concentra la mayor densidad de empleo formal, infraestructura de servicios y alternativas de transporte público masivo (subtes, trenes y carriles exclusivos de Metrobús), los municipios del Conurbano Bonaerense (Provincia de Buenos Aires - PBA) albergan a una proporción mayoritaria de la población en condiciones habitacionales diversas y con una red de transporte público fragmentada y predominantemente radial.

Esta asimetría espacial obliga a millones de ciudadanos residentes en el cordón externo del conurbano a realizar extensos desplazamientos diarios para acceder a sus lugares de trabajo en el núcleo urbano. Sin embargo, más allá de la distancia geográfica bruta, existe un factor de desigualdad menos visible pero altamente penalizador: la **intermodalidad forzada**. Mientras que la intermodalidad (la combinación de múltiples modos de transporte en un solo viaje) es un rasgo de eficiencia en sistemas metropolitanos integrados y planificados, en el AMBA suele manifestarse como una imposición debida a la falta de conectividad directa de superficie. Los usuarios periféricos se ven forzados a encadenar múltiples etapas de viaje (ej. colectivo barrial, tren de cercanías y un colectivo o subte final) simplemente para sortear la baja cobertura directa en sus lugares de residencia.

La motivación científica de este trabajo radica en cuantificar y mapear esta "fricción de movilidad". El uso de datos pasivos generados por sistemas automatizados de recaudo (tarjeta SUBE) ofrece una oportunidad inédita para observar la movilidad real de la ciudadanía a una escala masiva y con alta precisión geográfica. Este trabajo busca desarrollar una metodología estructurada para identificar "zonas de fricción crítica", permitiendo diferenciar la intermodalidad opcional y eficiente de aquella que es forzada e ineficiente, aportando herramientas analíticas de soporte para el diseño de políticas públicas orientadas a la equidad territorial.

## Planteamiento del Problema y Pregunta de Investigación

El reporte técnico del Banco Interamericano de Desarrollo (BID, 2022) destaca que los viajes interjurisdiccionales en el AMBA presentan un promedio de dos etapas por viaje. A pesar de este diagnóstico agregado, las dinámicas espaciales específicas y el impacto diferencial de los transbordos sobre los distintos estratos socioeconómicos de la población no han sido evaluados en detalle. La ineficiencia del sistema de transporte impone penalidades físicas y temporales (tiempos de espera en andenes, transbordos bajo condiciones climáticas adversas, e inseguridad en zonas de transferencia) que actúan como una fricción sistémica. Esta fricción recae de forma desproporcionada sobre la población de menores recursos, que reside predominantemente en las periferias debido al costo del suelo y depende de tarifas subsidiadas (Tarifa Social) para poder desplazarse.

A partir de esta problemática, se formula la siguiente **pregunta de investigación**:

> ¿En qué medida la intermodalidad forzada en el cordón externo del AMBA actúa como un factor de fricción espacial y temporal que penaliza el acceso de los usuarios en comparación con el centro urbano, y cómo se alinea esta ineficiencia estructural con la vulnerabilidad socioeconómica de los pasajeros?

## Objetivos del Trabajo

### Objetivo General
Determinar y cuantificar en qué medida la intermodalidad forzada en el transporte público del cordón externo del AMBA actúa como un factor de fricción espacial y temporal, identificando si existe una superposición estructural entre la postergación física de la red y la vulnerabilidad socioeconómica de los usuarios.

### Objetivos Específicos
1. **Modelar la movilidad metropolitana del AMBA como un grafo pesado y dirigido** basado en la agregación espacial de celdas H3, representando los flujos reales de pasajeros observados a partir de los datos transaccionales de la tarjeta SUBE.
2. **Identificar los puntos críticos de transbordo forzado y cuellos de botella** de la red mediante el cálculo de métricas topológicas de centralidad de intermediación ponderada.
3. **Formalizar y calcular índices sintéticos de fricción** (Índice de Fricción Espacial - IFI e Índice de Fricción Temporal - IFT) para caracterizar la penalización de transbordo en el territorio.
4. **Clasificar los desplazamientos metropolitanos mediante aprendizaje no supervisado (clustering)** sobre el espacio de características de fricción para aislar geográficamente los perfiles de viaje más ineficientes.
5. **Analizar la correlación estadística y espacial** entre las métricas de red (cercanía y aislamiento) y la distribución del ratio de Tarifa Social por zona de origen, validando la hipótesis de desigualdad socio-espacial.

## Estructura del Documento

Este trabajo está organizado en siete secciones principales. Tras esta introducción, la **Sección 2 (Marco Teórico)** repasa la literatura científica en torno al uso de datos de tarjetas inteligentes, los conceptos de equidad espacial en transporte y la aplicación de ciencia de redes. La **Sección 3 (Metodología)** describe la muestra del dataset SUBE, el preprocesamiento de coordenadas espaciales H3 y la formulación matemática de los índices de fricción y el modelo de grafos. La **Sección 4 (Resultados y Discusión)** presenta el análisis exploratorio descriptivo, los mapas de centralidades y del Índice de Vulnerabilidad Socio-Espacial, el agrupamiento de viajes y las matrices de correlación cruzada. La **Sección 5 (Conclusiones)** resume los hallazgos principales y propone recomendaciones de planificación urbana. Finalmente, la **Sección 6 (Bibliografía)** detalla las fuentes referenciadas y la **Sección 7 (Anexos)** aporta detalles sobre el procesamiento del código.
