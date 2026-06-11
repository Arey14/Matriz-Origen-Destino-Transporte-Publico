import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import networkx as nx
import h3
import os
import json
import geopandas as gpd
from shapely.geometry import Point, box, MultiPoint
from shapely.ops import voronoi_diagram, unary_union
from shapely.prepared import prep
from shapely.strtree import STRtree
import math

def main():
    print("Iniciando el Análisis de Vulnerabilidad, Centralidad y Sensibilidad Multiescala (Versión Mejorada)...")

    # Construir el contorno de tierra de AMBA desde indices_h3.csv
    import pandas as pd
    from shapely.geometry import Polygon, Point
    from shapely.ops import unary_union
    from shapely.prepared import prep
    
    df_indices = pd.read_csv("data/indices_h3.csv")
    df_indices['h3_res8'] = df_indices['h3'].apply(lambda x: h3.cell_to_parent(x, 8))
    unique_res8 = df_indices['h3_res8'].unique()
    polygons = []
    for hex_id in unique_res8:
        boundary_lat_lon = h3.cell_to_boundary(hex_id)
        polygons.append(Polygon([(lon, lat) for lat, lon in boundary_lat_lon]))
    land_boundary = unary_union(polygons)
    prepared_land = prep(land_boundary)
    
    # Conectamos a DuckDB en memoria
    con = duckdb.connect(database=':memory:')

    # Cambiar al directorio del proyecto
    project_dir = "/home/augusto/Downloads/Compressed/Tesis/Matriz-Origen-Destino-Transporte-Publico"
    os.chdir(project_dir)

    print("Cargando datasets en DuckDB...")
    try:
        con.execute("CREATE VIEW viajes AS SELECT * FROM read_csv_auto('resultados/viajes.csv', ignore_errors=true)")
        con.execute("CREATE VIEW etapas AS SELECT * FROM read_csv_auto('resultados/etapas.csv', ignore_errors=true)")
        con.execute("CREATE VIEW tarjetas AS SELECT * FROM read_csv_auto('resultados/tarjetas.csv', ignore_errors=true)")
        con.execute("CREATE VIEW indices_h3 AS SELECT * FROM read_csv_auto('data/indices_h3.csv', ignore_errors=true)")
        con.execute("CREATE VIEW paradas AS SELECT * FROM read_csv_auto('data/paradas.csv', ignore_errors=true)")
        con.execute("CREATE VIEW tarifas AS SELECT * FROM read_csv_auto('data/tarifas.csv', ignore_errors=true)")
    except Exception as e:
        print(f"Error al cargar datasets: {e}")
        return

    # Cargar extensiones de DuckDB
    con.execute("LOAD spatial;")
    con.execute("LOAD h3;")

    print("Creando vista viajes_geo con Imputación Temporal Refinada (Mejora 1)...")
    # Creamos viajes_geo usando la fórmula de regresión/velocidades teóricas basada en modos para viajes intra-horarios
    con.execute("""
        CREATE VIEW viajes_geo AS
        WITH viajes_coords AS (
            SELECT 
                v.*,
                po.latitud AS lat_o, po.longitud AS lon_o, po.h3 AS h3_o_10,
                pd.latitud AS lat_d, pd.longitud AS lon_d, pd.h3 AS h3_d_10,
                
                -- Regex para limpiar las terminaciones .0 en id_tarjeta e id_viaje
                REGEXP_REPLACE(CAST(v.id_tarjeta AS VARCHAR), '\\\\.0$', '') AS id_tarjeta_str,
                REGEXP_REPLACE(CAST(v.id_viaje AS VARCHAR), '\\\\.0$', '') AS id_viaje_str,

                -- Distancia Haversine pura en SQL
                6371.0 * 2 * ASIN(SQRT(
                    POWER(SIN(RADIANS(pd.latitud - po.latitud) / 2.0), 2) + 
                    COS(RADIANS(po.latitud)) * COS(RADIANS(pd.latitud)) * POWER(SIN(RADIANS(pd.longitud - po.longitud) / 2.0), 2)
                )) AS distancia,
                
                -- Jurisdicciones
                CASE WHEN h3_o_idx.provincia ILIKE '%CABA%' OR h3_o_idx.provincia ILIKE '%Ciudad Autónoma%' OR h3_o_idx.provincia ILIKE '%Capital Federal%' THEN 'CABA' ELSE 'PBA' END AS jur_origen,
                CASE WHEN h3_d_idx.provincia ILIKE '%CABA%' OR h3_d_idx.provincia ILIKE '%Ciudad Autónoma%' OR h3_d_idx.provincia ILIKE '%Capital Federal%' THEN 'CABA' ELSE 'PBA' END AS jur_destino
                
            FROM viajes v
            LEFT JOIN paradas po ON v.parada_id_o = po.id
            LEFT JOIN paradas pd ON v.parada_id_d = pd.id
            LEFT JOIN indices_h3 h3_o_idx ON po.h3 = h3_o_idx.h3
            LEFT JOIN indices_h3 h3_d_idx ON pd.h3 = h3_d_idx.h3
        ),
        viajes_clasificados AS (
            SELECT 
                *,
                CASE 
                    WHEN jur_origen = 'CABA' AND jur_destino = 'CABA' THEN 'Intra-CABA'
                    WHEN jur_origen = 'PBA' AND jur_destino = 'PBA' THEN 'Intra-PBA'
                    WHEN jur_origen IS NOT NULL AND jur_destino IS NOT NULL THEN 'CABA-PBA'
                    ELSE 'Desconocido'
                END AS tipo_viaje,
                CASE 
                    WHEN jur_origen = 'CABA' AND jur_destino = 'CABA' THEN 'Intra-CABA'
                    WHEN jur_origen = 'PBA' AND jur_destino = 'PBA' THEN 'Intra-PBA'
                    WHEN jur_origen = 'PBA' AND jur_destino = 'CABA' THEN 'PBA-CABA'
                    WHEN jur_origen = 'CABA' AND jur_destino = 'PBA' THEN 'CABA-PBA'
                    ELSE 'Desconocido'
                END AS tipo_viaje_detallado,
                
                CASE 
                    WHEN cantidad_etapas = 1 THEN '1 etapa'
                    WHEN cantidad_etapas = 2 THEN '2 etapas'
                    ELSE '3+ etapas'
                END AS etapas_agrupadas,
                
                -- Modos de Transporte
                COALESCE(etapas_colectivo, 0) AS c_col,
                COALESCE(etapas_tren, 0) AS c_tren,
                COALESCE(etapas_subte, 0) AS c_sub
            FROM viajes_coords
        ),
        viajes_modos AS (
            SELECT
                *,
                CASE
                    WHEN c_col > 0 AND c_tren = 0 AND c_sub = 0 THEN 'Solo Colectivo'
                    WHEN c_tren > 0 AND c_col = 0 AND c_sub = 0 THEN 'Solo Tren'
                    WHEN c_sub > 0 AND c_col = 0 AND c_tren = 0 THEN 'Solo Subte'
                    WHEN c_col > 0 AND c_tren > 0 AND c_sub = 0 THEN 'Col + Tren'
                    WHEN c_col > 0 AND c_sub > 0 AND c_tren = 0 THEN 'Col + Subte'
                    WHEN c_tren > 0 AND c_sub > 0 AND c_col = 0 THEN 'Tren + Subte'
                    WHEN c_col > 0 AND c_tren > 0 AND c_sub > 0 THEN 'Col + Tren + Subte'
                    ELSE 'Desconocido/Otros'
                END AS modo_transporte
            FROM viajes_clasificados
            WHERE tipo_viaje != 'Desconocido'
        ),
        tarifas_unicas AS (
            SELECT 
                REGEXP_REPLACE(CAST(id_tarjeta AS VARCHAR), '\\\\.0$', '') AS id_tarjeta_str,
                REGEXP_REPLACE(CAST(id_viaje AS VARCHAR), '\\\\.0$', '') AS id_viaje_str,
                FIRST(CAST(id_tarifa AS INTEGER)) AS id_tarifa,
                MIN(TRY_CAST(hora AS INTEGER)) AS hora_inicio,
                MAX(TRY_CAST(hora AS INTEGER)) AS hora_fin
            FROM etapas
            WHERE id_tarifa IS NOT NULL
            GROUP BY 1, 2
        )
        SELECT 
            v.*,
            COALESCE(t.nombre, 'Desconocida') AS nombre_tarifa,
            CASE 
                WHEN UPPER(COALESCE(t.nombre, 'Desconocida')) IN ('TARIFA PLENA', 'DESCONOCIDA') THEN 'Tarifa Plena'
                ELSE 'Tarifa Social / Subsidio'
            END AS perfil_tarifario,
            
            -- Tiempos y Fricción
            tu.hora_inicio,
            tu.hora_fin,
            CASE 
                WHEN (tu.hora_fin - tu.hora_inicio) < 0 THEN (tu.hora_fin - tu.hora_inicio) + 24 
                WHEN (tu.hora_fin - tu.hora_inicio) = 0 THEN 
                    LEAST(
                        CASE 
                            WHEN modo_transporte = 'Solo Colectivo' THEN (distancia / 15.0) + 0.08
                            WHEN modo_transporte = 'Solo Tren' THEN (distancia / 35.0) + 0.15
                            WHEN modo_transporte = 'Solo Subte' THEN (distancia / 25.0) + 0.08
                            WHEN modo_transporte = 'Col + Tren' THEN (distancia / 25.0) + 0.25
                            WHEN modo_transporte = 'Col + Subte' THEN (distancia / 20.0) + 0.16
                            WHEN modo_transporte = 'Tren + Subte' THEN (distancia / 30.0) + 0.23
                            WHEN modo_transporte = 'Col + Tren + Subte' THEN (distancia / 25.0) + 0.33
                            ELSE (distancia / 18.0) + 0.1
                        END, 
                        0.9
                    )
                ELSE COALESCE((tu.hora_fin - tu.hora_inicio), 0)
            END AS duracion_horas
        FROM viajes_modos v
        LEFT JOIN tarifas_unicas tu ON v.id_tarjeta_str = tu.id_tarjeta_str AND v.id_viaje_str = tu.id_viaje_str
        LEFT JOIN tarifas t ON tu.id_tarifa = CAST(t.id AS INTEGER)
    """)

    # ==========================================
    # MEJORA 3.A: ANÁLISIS MULTIESCALA H3 (RESOLUCIONES 7, 8, 9, 10)
    # ==========================================
    h3_results = []
    comparison_records = []
    
    # Resoluciones a analizar
    resolutions = [7, 8, 9, 10]
    
    print("\n--- INICIANDO ANÁLISIS MULTIESCALA H3 ---")
    for res in resolutions:
        print(f"\nProcesando H3 Resolución {res}...")
        
        # 1. Extracción de nodos y métricas de vulnerabilidad
        # Para el dataset semanal escalamos los umbrales: >=700 viajes en el nodo
        df_vulnerabilidad = con.execute(f"""
            SELECT 
                h3_h3_to_string(h3_cell_to_parent(h3_string_to_h3(h3_o_10), {res})) AS h3_index,
                COUNT(*) AS total_viajes,
                SUM(CASE WHEN perfil_tarifario = 'Tarifa Social / Subsidio' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS tarifa_social_ratio,
                MEDIAN((cantidad_etapas / distancia) * 10) AS mediana_IFI,
                MEDIAN(cantidad_etapas / duracion_horas) AS mediana_IFT,
                AVG(duracion_horas * 60) AS avg_duration_min,
                AVG(distancia / duracion_horas) AS avg_speed_kmh
            FROM viajes_geo
            WHERE h3_o_10 IS NOT NULL AND distancia >= 0.5 AND duracion_horas > 0
            GROUP BY 1
            HAVING COUNT(*) >= 700
        """).df()
        if not df_vulnerabilidad.empty:
            # Filtrar celdas fuera del contorno de tierra de AMBA (incluye el río y Uruguay)
            df_vulnerabilidad['centroid'] = df_vulnerabilidad['h3_index'].apply(lambda x: h3.cell_to_latlng(x))
            df_vulnerabilidad['in_land'] = df_vulnerabilidad.apply(lambda r: prepared_land.contains(Point(r['centroid'][1], r['centroid'][0])), axis=1)
            df_vulnerabilidad = df_vulnerabilidad[df_vulnerabilidad['in_land']].drop(columns=['centroid', 'in_land'])

        if df_vulnerabilidad.empty:
            print(f"Advertencia: No hay nodos activos en Resolución {res} con >=700 viajes.")
            continue
            
        print(f"Nodos activos extraídos: {len(df_vulnerabilidad):,}")
        
        # Normalizar métricas para el IVSE
        min_ts, max_ts = df_vulnerabilidad['tarifa_social_ratio'].min(), df_vulnerabilidad['tarifa_social_ratio'].max()
        if max_ts > min_ts:
            df_vulnerabilidad['ts_norm'] = (df_vulnerabilidad['tarifa_social_ratio'] - min_ts) / (max_ts - min_ts)
        else:
            df_vulnerabilidad['ts_norm'] = 0.0
            
        min_ifi, max_ifi = df_vulnerabilidad['mediana_IFI'].min(), df_vulnerabilidad['mediana_IFI'].max()
        if max_ifi > min_ifi:
            df_vulnerabilidad['ifi_norm'] = (df_vulnerabilidad['mediana_IFI'] - min_ifi) / (max_ifi - min_ifi)
        else:
            df_vulnerabilidad['ifi_norm'] = 0.0
            
        df_vulnerabilidad['IVSE'] = df_vulnerabilidad['ts_norm'] * df_vulnerabilidad['ifi_norm']

        # 2. Extracción de enlaces para la red
        # Umbral semanal de >=210 viajes por enlace
        df_edges = con.execute(f"""
            SELECT 
                h3_h3_to_string(h3_cell_to_parent(h3_string_to_h3(h3_o_10), {res})) AS source,
                h3_h3_to_string(h3_cell_to_parent(h3_string_to_h3(h3_d_10), {res})) AS target,
                COUNT(*) AS volume,
                AVG(duracion_horas) AS avg_duration
            FROM viajes_geo
            WHERE h3_o_10 IS NOT NULL AND h3_d_10 IS NOT NULL AND distancia >= 0.5 AND duracion_horas > 0
            GROUP BY 1, 2
            HAVING COUNT(*) >= 210
        """).df()
        
        print(f"Enlaces de red extraídos: {len(df_edges):,}")
        
        # Construcción del grafo con NetworkX
        G = nx.DiGraph()
        for _, row in df_edges.iterrows():
            G.add_edge(row['source'], row['target'], weight=row['avg_duration'], volume=row['volume'])
            
        # Calculamos centralidades
        print("Calculando cercanía (closeness centrality)...")
        closeness = nx.closeness_centrality(G, distance='weight')
        print("Calculando intermediación (betweenness centrality)...")
        betweenness = nx.betweenness_centrality(G, weight='weight')
        
        df_centralidades = pd.DataFrame({
            'h3_index': list(G.nodes()),
            'closeness': [closeness.get(node, 0) for node in G.nodes()],
            'betweenness': [betweenness.get(node, 0) for node in G.nodes()]
        })
        
        df_final = pd.merge(df_vulnerabilidad, df_centralidades, on='h3_index', how='inner')
        
        # Guardamos correlaciones
        corr_pears = df_final[['tarifa_social_ratio', 'mediana_IFI', 'closeness', 'betweenness', 'avg_duration_min', 'avg_speed_kmh']].corr(method='pearson')
        corr_spear = df_final[['tarifa_social_ratio', 'mediana_IFI', 'closeness', 'betweenness', 'avg_duration_min', 'avg_speed_kmh']].corr(method='spearman')
        
        # Guardamos métricas generales del grafo
        comparison_records.append({
            'Escala': f'H3 Res {res}',
            'Nodos Activos (V)': len(df_final),
            'Enlaces Estables (E)': G.number_of_edges(),
            'Pearson_TS_Closeness': corr_pears.loc['tarifa_social_ratio', 'closeness'],
            'Spearman_TS_Closeness': corr_spear.loc['tarifa_social_ratio', 'closeness'],
            'Pearson_TS_IFI': corr_pears.loc['tarifa_social_ratio', 'mediana_IFI'],
            'Spearman_TS_IFI': corr_spear.loc['tarifa_social_ratio', 'mediana_IFI'],
            'Pearson_TS_Speed': corr_pears.loc['tarifa_social_ratio', 'avg_speed_kmh'],
            'Spearman_TS_Speed': corr_spear.loc['tarifa_social_ratio', 'avg_speed_kmh']
        })
        
        # Si es la escala representativa (Res 8), guardamos las figuras y CSV
        if res == 8:
            df_final.to_csv("resultados/metricas_vulnerabilidad_red.csv", index=False)
            print("Guardado resultados/metricas_vulnerabilidad_red.csv para Res 8.")
            
            # Generar geometries GeoJSON para las celdas H3 activas
            print("Generando geometries GeoJSON para mapas H3 Res 8...")
            geojson_features = []
            for hex_id in df_final['h3_index'].unique():
                try:
                    boundary_lat_lon = h3.cell_to_boundary(hex_id)
                    boundary = [[lon, lat] for lat, lon in boundary_lat_lon]
                    boundary.append(boundary[0])  # Cerrar
                    geojson_features.append({
                        "type": "Feature",
                        "id": hex_id,
                        "geometry": {"type": "Polygon", "coordinates": [boundary]}
                    })
                except Exception:
                    continue
            geojson_data = {"type": "FeatureCollection", "features": geojson_features}
            
            # Mapear Figura 14: IVSE
            umbral_max_ivse = df_final['IVSE'].quantile(0.98)
            fig14 = px.choropleth_map(
                df_final, geojson=geojson_data, locations='h3_index', color='IVSE',
                color_continuous_scale="Reds", range_color=(0, umbral_max_ivse),
                map_style="carto-darkmatter", zoom=10, center=dict(lat=-34.6037, lon=-58.3816),
                opacity=0.7, title="Figura 14: Índice de Vulnerabilidad Socio-Espacial (IVSE) - H3 Res 8 (Semanal)"
            )
            fig14.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
            fig14.write_html('figura14_vulnerabilidad_sql.html')
            
            # Mapear Figura 15: Cercanía
            umbral_max_close = df_final['closeness'].quantile(0.98)
            fig15 = px.choropleth_map(
                df_final, geojson=geojson_data, locations='h3_index', color='closeness',
                color_continuous_scale="Viridis", range_color=(df_final['closeness'].min(), umbral_max_close),
                map_style="carto-darkmatter", zoom=10, center=dict(lat=-34.6037, lon=-58.3816),
                opacity=0.7, title="Figura 15: Cercanía Estructural de Transporte (Closeness) - H3 Res 8 (Semanal)"
            )
            fig15.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
            fig15.write_html('figura15_cercania_red.html')
            
            # Mapear Figura 16: Intermediación
            umbral_max_between = df_final['betweenness'].quantile(0.98)
            fig16 = px.choropleth_map(
                df_final, geojson=geojson_data, locations='h3_index', color='betweenness',
                color_continuous_scale="Inferno", range_color=(0, umbral_max_between),
                map_style="carto-darkmatter", zoom=10, center=dict(lat=-34.6037, lon=-58.3816),
                opacity=0.7, title="Figura 16: Centralidad de Intermediación (Betweenness) - H3 Res 8 (Semanal)"
            )
            fig16.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
            fig16.write_html('figura16_intermediacion_red.html')
            print("Figuras 14, 15 y 16 renderizadas con éxito.")

    # ==========================================
    # MEJORA 3.B: Voronoi / Stop-Level Network Analysis
    # ==========================================
    print("\n--- INICIANDO ANÁLISIS VORONOI A NIVEL DE PARADAS ---")
    
    # 1. Obtención de paradas y métricas
    df_vor_nodes = con.execute("""
        SELECT 
            parada_id_o AS parada_id,
            COUNT(*) AS total_viajes,
            SUM(CASE WHEN perfil_tarifario = 'Tarifa Social / Subsidio' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS tarifa_social_ratio,
            MEDIAN((cantidad_etapas / distancia) * 10) AS mediana_IFI,
            MEDIAN(cantidad_etapas / duracion_horas) AS mediana_IFT,
            AVG(duracion_horas * 60) AS avg_duration_min,
            AVG(distancia / duracion_horas) AS avg_speed_kmh
        FROM viajes_geo
        WHERE parada_id_o IS NOT NULL AND distancia >= 0.5 AND duracion_horas > 0
        GROUP BY 1
        HAVING COUNT(*) >= 700
    """).df()
    
    print(f"Paradas activas (nodos Voronoi): {len(df_vor_nodes):,}")
    
    # Normalizar para IVSE
    min_ts, max_ts = df_vor_nodes['tarifa_social_ratio'].min(), df_vor_nodes['tarifa_social_ratio'].max()
    df_vor_nodes['ts_norm'] = (df_vor_nodes['tarifa_social_ratio'] - min_ts) / (max_ts - min_ts) if max_ts > min_ts else 0.0
    
    min_ifi, max_ifi = df_vor_nodes['mediana_IFI'].min(), df_vor_nodes['mediana_IFI'].max()
    df_vor_nodes['ifi_norm'] = (df_vor_nodes['mediana_IFI'] - min_ifi) / (max_ifi - min_ifi) if max_ifi > min_ifi else 0.0
    
    df_vor_nodes['IVSE'] = df_vor_nodes['ts_norm'] * df_vor_nodes['ifi_norm']

    # 2. Extracción de enlaces de paradas
    df_vor_edges = con.execute("""
        SELECT 
            parada_id_o AS source,
            parada_id_d AS target,
            COUNT(*) AS volume,
            AVG(duracion_horas) AS avg_duration
        FROM viajes_geo
        WHERE parada_id_o IS NOT NULL AND parada_id_d IS NOT NULL AND distancia >= 0.5 AND duracion_horas > 0
        GROUP BY 1, 2
        HAVING COUNT(*) >= 210
    """).df()
    
    print(f"Enlaces de paradas extraídos: {len(df_vor_edges):,}")
    
    # Grafo de paradas
    G_vor = nx.DiGraph()
    for _, row in df_vor_edges.iterrows():
        G_vor.add_edge(int(row['source']), int(row['target']), weight=row['avg_duration'], volume=row['volume'])
        
    print(f"Grafo de Paradas: {G_vor.number_of_nodes()} nodos y {G_vor.number_of_edges()} enlaces.")
    
    # Calcular centralidades
    print("Calculando cercanía en paradas...")
    closeness_vor = nx.closeness_centrality(G_vor, distance='weight')
    print("Calculando intermediación en paradas...")
    betweenness_vor = nx.betweenness_centrality(G_vor, weight='weight')
    
    df_vor_centralidades = pd.DataFrame({
        'parada_id': list(G_vor.nodes()),
        'closeness': [closeness_vor.get(node, 0) for node in G_vor.nodes()],
        'betweenness': [betweenness_vor.get(node, 0) for node in G_vor.nodes()]
    })
    
    # Asegurar tipo de datos consistente para el merge
    df_vor_nodes['parada_id'] = df_vor_nodes['parada_id'].astype(int)
    df_vor_centralidades['parada_id'] = df_vor_centralidades['parada_id'].astype(int)
    
    df_vor_final = pd.merge(df_vor_nodes, df_vor_centralidades, on='parada_id', how='inner')
    df_vor_final.to_csv("resultados/metricas_vulnerabilidad_voronoi.csv", index=False)
    
    # Correlaciones Voronoi
    corr_pears_vor = df_vor_final[['tarifa_social_ratio', 'mediana_IFI', 'closeness', 'betweenness', 'avg_duration_min', 'avg_speed_kmh']].corr(method='pearson')
    corr_spear_vor = df_vor_final[['tarifa_social_ratio', 'mediana_IFI', 'closeness', 'betweenness', 'avg_duration_min', 'avg_speed_kmh']].corr(method='spearman')
    
    comparison_records.append({
        'Escala': 'Voronoi Paradas',
        'Nodos Activos (V)': len(df_vor_final),
        'Enlaces Estables (E)': G_vor.number_of_edges(),
        'Pearson_TS_Closeness': corr_pears_vor.loc['tarifa_social_ratio', 'closeness'],
        'Spearman_TS_Closeness': corr_spear_vor.loc['tarifa_social_ratio', 'closeness'],
        'Pearson_TS_IFI': corr_pears_vor.loc['tarifa_social_ratio', 'mediana_IFI'],
        'Spearman_TS_IFI': corr_spear_vor.loc['tarifa_social_ratio', 'mediana_IFI'],
        'Pearson_TS_Speed': corr_pears_vor.loc['tarifa_social_ratio', 'avg_speed_kmh'],
        'Spearman_TS_Speed': corr_spear_vor.loc['tarifa_social_ratio', 'avg_speed_kmh']
    })

    # 3. Generación y renderizado de diagramas de Voronoi
    print("Generando diagramas de Voronoi espaciales...")
    df_coords_paradas = con.execute(f"""
        SELECT id, latitud, longitud
        FROM paradas
        WHERE id IN ({','.join([str(x) for x in df_vor_final['parada_id']])})
    """).df()
    
    df_coords_paradas = df_coords_paradas.dropna(subset=['latitud', 'longitud'])
    points = [Point(lon, lat) for lon, lat in zip(df_coords_paradas['longitud'], df_coords_paradas['latitud'])]
    multi_point = MultiPoint(points)
    
    min_lon = df_coords_paradas['longitud'].min() - 0.05
    max_lon = df_coords_paradas['longitud'].max() + 0.05
    min_lat = df_coords_paradas['latitud'].min() - 0.05
    max_lat = df_coords_paradas['latitud'].max() + 0.05
    boundary = box(min_lon, min_lat, max_lon, max_lat)
    
    vor_polys = voronoi_diagram(multi_point, envelope=boundary)
    tree = STRtree(points)
    voronoi_records = []
    
    for poly in vor_polys.geoms:
        # Intersecar con el contorno de tierra en lugar de la caja delimitadora
        clipped_poly = poly.intersection(land_boundary)
        if clipped_poly.is_empty:
            continue
        # Extraer solo partes poligonales de la intersección (por si devuelve GeometryCollection)
        if clipped_poly.geom_type == 'GeometryCollection':
            polys = [g for g in clipped_poly.geoms if g.geom_type in ('Polygon', 'MultiPolygon')]
            if not polys:
                continue
            clipped_poly = unary_union(polys)
        elif clipped_poly.geom_type not in ('Polygon', 'MultiPolygon'):
            continue
            
        nearest_idx = tree.nearest(clipped_poly.centroid)
        parada_row = df_coords_paradas.iloc[nearest_idx]
        voronoi_records.append({
            'parada_id': int(parada_row['id']),
            'geometry': clipped_poly
        })
        
    gdf_vor = gpd.GeoDataFrame(voronoi_records, crs="EPSG:4326")
    geojson_vor = json.loads(gdf_vor.to_json())
    
    # Unir las métricas en df_vor_final para graficar
    # Plotly exige un DataFrame alineado
    df_plot_vor = pd.merge(df_vor_final, df_coords_paradas, left_on='parada_id', right_on='id', how='inner')
    
    # Mapa Voronoi 1: IVSE
    umbral_max_vor_ivse = df_plot_vor['IVSE'].quantile(0.98)
    fig_vor_ivse = px.choropleth_map(
        df_plot_vor, geojson=geojson_vor, locations='parada_id', featureidkey="properties.parada_id",
        color='IVSE', color_continuous_scale="Reds", range_color=(0, umbral_max_vor_ivse),
        map_style="carto-darkmatter", zoom=10, center=dict(lat=-34.6037, lon=-58.3816),
        opacity=0.6, title="Figura 17: Índice de Vulnerabilidad Socio-Espacial (IVSE) - Agregación de Voronoi por Paradas"
    )
    fig_vor_ivse.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    fig_vor_ivse.write_html('figura17_vulnerabilidad_voronoi.html')
    
    # Mapa Voronoi 2: Cercanía
    umbral_max_vor_close = df_plot_vor['closeness'].quantile(0.98)
    fig_vor_close = px.choropleth_map(
        df_plot_vor, geojson=geojson_vor, locations='parada_id', featureidkey="properties.parada_id",
        color='closeness', color_continuous_scale="Viridis", range_color=(df_plot_vor['closeness'].min(), umbral_max_vor_close),
        map_style="carto-darkmatter", zoom=10, center=dict(lat=-34.6037, lon=-58.3816),
        opacity=0.6, title="Figura 18: Cercanía Estructural (Closeness Centrality) - Agregación de Voronoi por Paradas"
    )
    fig_vor_close.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    fig_vor_close.write_html('figura18_cercania_voronoi.html')
    print("Mapas de Voronoi guardados con éxito (figura17 y figura18).")

    # ==========================================
    # GUARDADO Y REPORTE COMPARATIVO DE ESCALAS
    # ==========================================
    df_comparison = pd.DataFrame(comparison_records)
    df_comparison.to_csv("resultados/comparacion_escalas_h3.csv", index=False)
    
    print("\n=========================================================================")
    print("         TABLA COMPARATIVA MULTIESCALA (H3 y Voronoi)")
    print("=========================================================================")
    print(df_comparison.round(4).to_string(index=False))
    print("=========================================================================\n")

    # ==========================================
    # MODELADO DE REGRESIÓN MULTIVARIABLE (OLS)
    # ==========================================
    print("[Modelo de Regresión MCO] Estimando impacto temporal a nivel de viajes...")
    try:
        # Helper para la probabilidad de distribución normal
        def Z_prob(x):
            return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

        # Densidad de oferta en origen (resolución 10 por simplicidad)
        con.execute("""
            CREATE OR REPLACE VIEW densidad_origen AS
            SELECT h3, COUNT(*) as stops_count
            FROM paradas
            WHERE h3 IS NOT NULL
            GROUP BY h3
        """)

        # Cargar datos desde las vistas existentes
        df_reg = con.execute("""
            SELECT 
                v.duracion_horas * 60.0 AS duracion_minutos,
                v.cantidad_etapas,
                v.distancia,
                COALESCE(d.stops_count, 0) AS stops_density_o,
                v.lat_o,
                v.lon_o
            FROM viajes_geo v
            LEFT JOIN densidad_origen d ON v.h3_o_10 = d.h3
            WHERE v.distancia >= 0.5 AND v.duracion_horas > 0 AND v.lat_o IS NOT NULL AND v.lon_o IS NOT NULL
        """).df()

        print(f"Registros MCO: {len(df_reg):,}")
        df_reg = df_reg.dropna().replace([np.inf, -np.inf], np.nan).dropna()

        y = df_reg['duracion_minutos'].values
        X = np.column_stack([
            np.ones(len(df_reg)),
            df_reg['cantidad_etapas'].values,
            df_reg['distancia'].values,
            df_reg['stops_density_o'].values,
            df_reg['lat_o'].values,
            df_reg['lon_o'].values
        ])

        # OLS mediante numpy
        beta, residuals, rank, s = np.linalg.lstsq(X, y, rcond=-1)

        # R-squared
        y_mean = np.mean(y)
        ss_tot = np.sum((y - y_mean) ** 2)
        ss_res = np.sum((y - np.dot(X, beta)) ** 2)
        r2 = 1.0 - (ss_res / ss_tot)

        # Inferencia estadística
        n, k = X.shape
        dof = n - k
        sigma2 = ss_res / dof
        vcov = np.linalg.inv(np.dot(X.T, X)) * sigma2
        se = np.sqrt(np.diag(vcov))
        t_stats = beta / se

        p_values_str = []
        for t in t_stats:
            if abs(t) > 8:
                p_values_str.append("< 0.0001")
            else:
                p = 2.0 * (1.0 - Z_prob(abs(t)))
                p_values_str.append(f"{p:.4f}")

        labels = [
            'Intercepto', 
            'Cantidad de Etapas', 
            'Distancia (km)', 
            'Densidad Oferta Origen (paradas)', 
            'Latitud Origen', 
            'Longitud Origen'
        ]

        results = []
        for i in range(len(labels)):
            results.append({
                'Variable': labels[i],
                'Coeficiente (Beta)': beta[i],
                'Error Estándar': se[i],
                't-stat': t_stats[i],
                'p-value': p_values_str[i]
            })

        df_res = pd.DataFrame(results)
        print("--- RESULTADOS DE LA REGRESIÓN OLS ---")
        print(f"R-squared: {r2:.4f}")
        print(df_res.round(6).to_string(index=False))

        df_res.to_csv("resultados/regresion_ols.csv", index=False)
        print("MCO finalizado con éxito.")
        
    except Exception as e:
        print(f"Error en regresión: {e}")
    print("========================================================\n")

if __name__ == "__main__":
    main()
