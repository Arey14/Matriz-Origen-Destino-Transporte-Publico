import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    # Set plot styling
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'figure.titlesize': 15})

    print("Conectando a DuckDB en memoria...")
    con = duckdb.connect(database=':memory:')

    # Change current working directory to where the csv files are located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)

    print("Cargando datasets en DuckDB...")
    con.execute("CREATE VIEW viajes AS SELECT * FROM read_csv_auto('resultados/viajes.csv', ignore_errors=true)")
    con.execute("CREATE VIEW etapas AS SELECT * FROM read_csv_auto('resultados/etapas.csv', ignore_errors=true)")
    con.execute("CREATE VIEW paradas AS SELECT * FROM read_csv_auto('data/paradas.csv', ignore_errors=true)")
    con.execute("CREATE VIEW indices_h3 AS SELECT * FROM read_csv_auto('data/indices_h3.csv', ignore_errors=true)")

    print("Ejecutando consulta SQL para calcular IFI, IFT y clasificar viajes (incluyendo PBA-CABA y CABA-PBA por separado)...")
    
    # We query and calculate variables. We filter for valid voyages as in the notebook.
    # We also separate PBA-CABA and CABA-PBA!
    query = """
        WITH viajes_coords AS (
            SELECT 
                v.*,
                po.latitud AS lat_o, po.longitud AS lon_o,
                pd.latitud AS lat_d, pd.longitud AS lon_d,
                REGEXP_REPLACE(CAST(v.id_tarjeta AS VARCHAR), '\\\\.0$', '') AS id_tarjeta_str,
                REGEXP_REPLACE(CAST(v.id_viaje AS VARCHAR), '\\\\.0$', '') AS id_viaje_str,
                
                -- Haversine distance
                6371.0 * 2 * ASIN(SQRT(
                    POWER(SIN(RADIANS(pd.latitud - po.latitud) / 2.0), 2) + 
                    COS(RADIANS(po.latitud)) * COS(RADIANS(pd.latitud)) * POWER(SIN(RADIANS(pd.longitud - po.longitud) / 2.0), 2)
                )) AS distancia,
                
                -- Jurisdictions
                CASE WHEN h3_o_idx.provincia ILIKE '%CABA%' OR h3_o_idx.provincia ILIKE '%Ciudad Autónoma%' OR h3_o_idx.provincia ILIKE '%Capital Federal%' THEN 'CABA' ELSE 'PBA' END AS jur_origen,
                CASE WHEN h3_d_idx.provincia ILIKE '%CABA%' OR h3_d_idx.provincia ILIKE '%Ciudad Autónoma%' OR h3_d_idx.provincia ILIKE '%Capital Federal%' THEN 'CABA' ELSE 'PBA' END AS jur_destino,
                
                COALESCE(etapas_colectivo, 0) AS c_col,
                COALESCE(etapas_tren, 0) AS c_tren,
                COALESCE(etapas_subte, 0) AS c_sub
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
                    WHEN jur_origen = 'PBA' AND jur_destino = 'CABA' THEN 'PBA-CABA'
                    WHEN jur_origen = 'CABA' AND jur_destino = 'PBA' THEN 'CABA-PBA'
                    ELSE 'Desconocido'
                END AS tipo_viaje_detallado,
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
            FROM viajes_coords
            WHERE jur_origen IS NOT NULL AND jur_destino IS NOT NULL
        ),
        tarifas_unicas AS (
            SELECT 
                REGEXP_REPLACE(CAST(id_tarjeta AS VARCHAR), '\\\\.0$', '') AS id_tarjeta_str,
                REGEXP_REPLACE(CAST(id_viaje AS VARCHAR), '\\\\.0$', '') AS id_viaje_str,
                MIN(TRY_CAST(hora AS INTEGER)) AS hora_inicio,
                MAX(TRY_CAST(hora AS INTEGER)) AS hora_fin
            FROM etapas
            GROUP BY 1, 2
        ),
        viajes_con_tiempos AS (
            SELECT 
                v.*,
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
            FROM viajes_clasificados v
            LEFT JOIN tarifas_unicas tu ON v.id_tarjeta_str = tu.id_tarjeta_str AND v.id_viaje_str = tu.id_viaje_str
        )
        SELECT 
            tipo_viaje_detallado,
            cantidad_etapas,
            distancia,
            duracion_horas,
            (cantidad_etapas / distancia) * 10 AS IFI,
            (cantidad_etapas / duracion_horas) AS IFT
        FROM viajes_con_tiempos
        WHERE distancia >= 0.5 AND duracion_horas > 0 AND tipo_viaje_detallado != 'Desconocido'
    """
    
    print("Extrayendo datos...")
    df = con.execute(query).df()
    print(f"Datos extraídos: {len(df):,} viajes procesados.")

    # Calculate statistics
    print("\n--- ESTADÍSTICAS DESCRIPTIVAS DE IFI (Etapas cada 10 km) ---")
    desc_ifi = df.groupby('tipo_viaje_detallado')['IFI'].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    print(desc_ifi.round(3).to_string())

    print("\n--- ESTADÍSTICAS DESCRIPTIVAS DE IFT (Etapas por hora) ---")
    desc_ift = df.groupby('tipo_viaje_detallado')['IFT'].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
    print(desc_ift.round(3).to_string())

    # Save statistics to a CSV or text file
    desc_ifi.to_csv("resultados/estadisticas_IFI.csv")
    desc_ift.to_csv("resultados/estadisticas_IFT.csv")

    # Generate Plots
    print("\nGenerando gráficos de distribución...")
    
    # We will sample the dataframe to make plotting faster and avoid huge vector graphics
    # But we calculate statistics on the FULL dataset
    df_sample = df.sample(n=min(100000, len(df)), random_state=42)

    # 1. Boxplot comparison (to show medians, quartiles, and range without showing millions of outliers)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # For IFI, since there can be large outliers (e.g. short distances with multiple stages), we cap the y-axis for visibility
    sns.boxplot(data=df_sample, x='tipo_viaje_detallado', y='IFI', ax=axes[0],
                order=['Intra-CABA', 'Intra-PBA', 'PBA-CABA', 'CABA-PBA'], palette='Set2', showfliers=False)
    axes[0].set_title('Distribución de IFI (Capped y-axis, no outliers)')
    axes[0].set_xlabel('Tipo de Viaje')
    axes[0].set_ylabel('IFI (Etapas por 10 km)')
    
    # Add median labels on the boxes
    medians_ifi = df.groupby('tipo_viaje_detallado')['IFI'].median()
    for i, category in enumerate(['Intra-CABA', 'Intra-PBA', 'PBA-CABA', 'CABA-PBA']):
        val = medians_ifi[category]
        axes[0].text(i, val + 0.1, f'{val:.2f}', ha='center', va='bottom', weight='bold', color='black',
                     bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    # For IFT, we do the same
    sns.boxplot(data=df_sample, x='tipo_viaje_detallado', y='IFT', ax=axes[1],
                order=['Intra-CABA', 'Intra-PBA', 'PBA-CABA', 'CABA-PBA'], palette='Set2', showfliers=False)
    axes[1].set_title('Distribución de IFT (Capped y-axis, no outliers)')
    axes[1].set_xlabel('Tipo de Viaje')
    axes[1].set_ylabel('IFT (Etapas por hora)')

    medians_ift = df.groupby('tipo_viaje_detallado')['IFT'].median()
    for i, category in enumerate(['Intra-CABA', 'Intra-PBA', 'PBA-CABA', 'CABA-PBA']):
        val = medians_ift[category]
        axes[1].text(i, val + 0.05, f'{val:.2f}', ha='center', va='bottom', weight='bold', color='black',
                     bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    plt.suptitle('Distribución comparativa de Índices de Fricción (IFI y IFT)', fontweight='bold')
    plt.tight_layout()
    plt.savefig('resultados/visualizaciones/figura12_boxplot_ifi_ift.png', dpi=300)
    plt.close()

    # 2. KDE / Histogram density plots for detail
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))

    # IFI Density (zoom in on range 0 to 10)
    for cat in ['Intra-CABA', 'Intra-PBA', 'PBA-CABA', 'CABA-PBA']:
        subset = df[df['tipo_viaje_detallado'] == cat]
        sns.kdeplot(data=subset, x='IFI', ax=axes[0], label=cat, fill=True, alpha=0.2, clip=(0, 10))
    axes[0].set_title('Densidad de Probabilidad del IFI (Corte en IFI <= 10)')
    axes[0].set_xlabel('IFI (Etapas por 10 km)')
    axes[0].set_ylabel('Densidad')
    axes[0].legend(title='Tipo de Viaje')

    # IFT Density (zoom in on range 0 to 6)
    for cat in ['Intra-CABA', 'Intra-PBA', 'PBA-CABA', 'CABA-PBA']:
        subset = df[df['tipo_viaje_detallado'] == cat]
        sns.kdeplot(data=subset, x='IFT', ax=axes[1], label=cat, fill=True, alpha=0.2, clip=(0, 6))
    axes[1].set_title('Densidad de Probabilidad del IFT (Corte en IFT <= 6)')
    axes[1].set_xlabel('IFT (Etapas por hora)')
    axes[1].set_ylabel('Densidad')
    axes[1].legend(title='Tipo de Viaje')

    plt.suptitle('Curvas de Densidad de IFI e IFT por Jurisdicción de Viaje', fontweight='bold')
    plt.tight_layout()
    plt.savefig('resultados/visualizaciones/figura13_densidad_ifi_ift.png', dpi=300)
    plt.close()

    print("Gráficos guardados en resultados/visualizaciones/figura12_boxplot_ifi_ift.png y resultados/visualizaciones/figura13_densidad_ifi_ift.png")

if __name__ == "__main__":
    main()
