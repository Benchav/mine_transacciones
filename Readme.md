# README --- Minería de Transacciones (Market Basket + RFM)

Este repositorio contiene código y scripts para realizar un análisis de
cesta de compra (Market Basket Analysis) y segmentación de clientes
(RFM + clustering) sobre un dataset de transacciones
(`ventas_ejemplo.csv`).\
La guía siguiente explica **paso a paso** desde cero cómo preparar el
entorno, ejecutar los análisis, qué hace cada archivo y cómo generar los
entregables (gráficos, tablas, informe).

------------------------------------------------------------------------

## Estructura del proyecto

    mine_transacciones/
    ├─ data/
    │  └─ ventas_ejemplo.csv
    ├─ outputs/
    │  ├─ ventas_preprocessed.csv
    │  ├─ top10_support.png
    │  ├─ rules_pairs_top.csv
    │  ├─ top5_rules.txt
    │  ├─ rfm_clusters.csv
    │  ├─ Perfil_de_clusters.csv
    │  ├─ Evaluaci_n_K__Elbow___Silhouette_.csv
    │  ├─ rfm_scatter.png
    │  └─ rfm_radar.png
    ├─ outputs_apriori/
    │  ├─ rules_apriori.csv
    │  └─ rules_network.png
    ├─ scripts/
    │  ├─ clean_descriptions.py
    │  ├─ run_apriori.py
    │  ├─ plot_rules_network.py
    │  ├─ radar_clusters.py
    │  ├─ generate_rule_interpretations.py
    │  ├─ generate_report.py
    │  └─ top5_rules_to_txt.py
    ├─ src/
    │  └─ mineria_ejercicios.py
    ├─ venv/
    ├─ requirements.txt
    └─ README.md

------------------------------------------------------------------------

## Instalación de dependencias

``` bash
python -m venv venv
# Windows
.env\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Dependencias principales:

    pandas
    numpy
    matplotlib
    seaborn
    scikit-learn
    mlxtend
    networkx
    python-docx
    Unidecode

------------------------------------------------------------------------

## Ejecución del análisis

### Script principal

``` bash
python src/mineria_ejercicios.py --input data/ventas_ejemplo.csv --outdir outputs
```

Opciones adicionales: - `--use_apriori` → usar Apriori si `mlxtend` está
instalado - `--min_support 0.02` - `--min_confidence 0.3` -
`--top_n_items 50` - `--k_min 2 --k_max 8`

Ejemplo con Apriori:

``` bash
python src/mineria_ejercicios.py --input data/ventas_ejemplo.csv --outdir outputs_apriori --use_apriori --min_support 0.02 --min_confidence 0.3
```

------------------------------------------------------------------------

## Scripts auxiliares

-   `scripts/clean_descriptions.py` → Limpieza de descripciones de
    productos.
-   `scripts/run_apriori.py` → Corre Apriori sobre
    `ventas_preprocessed.csv`.
-   `scripts/plot_rules_network.py` → Visualiza reglas como red
    (`rules_network.png`).
-   `scripts/radar_clusters.py` → Radar chart de clusters
    (`rfm_radar.png`).
-   `scripts/generate_rule_interpretations.py` → Explicaciones
    automáticas de reglas (`rules_interpretations.txt`).
-   `scripts/top5_rules_to_txt.py` → Extrae top 5 reglas
    (`top5_rules.txt`).
-   `scripts/generate_report.py` → Informe Word (`informe_minero.docx`).

------------------------------------------------------------------------

## Archivos de salida importantes

-   `ventas_preprocessed.csv` → dataset limpio
-   `rules_apriori.csv` / `rules_pairs_top.csv` → reglas con
    support/confidence/lift
-   `rules_network.png` → red de reglas
-   `top5_rules.txt` y `rules_interpretations.txt` → reglas principales
-   `rfm_clusters.csv` → clientes con cluster asignado
-   `Perfil_de_clusters.csv` → perfil de cada cluster
-   `rfm_scatter.png` y `rfm_radar.png` → gráficos RFM

------------------------------------------------------------------------

## Flujo recomendado para entregar

1.  Limpiar descripciones

    ``` bash
    python scripts/clean_descriptions.py
    ```

2.  Ejecutar análisis con Apriori

    ``` bash
    python src/mineria_ejercicios.py --input data/ventas_ejemplo.csv --outdir outputs_apriori --use_apriori
    ```

3.  Graficar red de reglas

    ``` bash
    python scripts/plot_rules_network.py
    ```

4.  Generar interpretaciones y top reglas

    ``` bash
    python scripts/generate_rule_interpretations.py
    python scripts/top5_rules_to_txt.py
    ```

5.  Generar radar clusters

    ``` bash
    python scripts/radar_clusters.py
    ```

6.  Generar informe

    ``` bash
    python scripts/generate_report.py
    ```

------------------------------------------------------------------------

## Crado por:

Proyecto creado por **Joshua Chaves** ---
https://joshuachavez.vercel.app/