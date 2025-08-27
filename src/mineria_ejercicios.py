import os
import argparse
import logging
from datetime import timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Intento importar mlxtend (Apriori). Si falla, usamos fallback.
USE_MLXTEND = True
try:
    from mlxtend.frequent_patterns import apriori, association_rules
except Exception:
    USE_MLXTEND = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ---------------- utilidades ----------------
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

# ---------------- preprocesamiento ----------------
def load_and_preprocess(path):
    """
    Carga CSV y realiza limpieza mínima requerida por el proyecto:
    - Verifica columnas requeridas
    - Elimina filas con nulos en columnas claves
    - Convierte tipos (Quantity, UnitPrice)
    - Filtra Quantity>0 y UnitPrice>0
    - Crea TotalPrice y convierte InvoiceDate a datetime (con fallback dayfirst)
    """
    logging.info(f"Cargando datos desde: {path}")
    df = pd.read_csv(path, encoding='ISO-8859-1')
    logging.info(f"Shape original: {df.shape}")

    required = ['InvoiceNo','Description','Quantity','UnitPrice','CustomerID','InvoiceDate']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas necesarias en el CSV: {missing}")

    df = df.dropna(subset=required)
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
    df = df.dropna(subset=['Quantity','UnitPrice'])
    df = df[(df['Quantity']>0) & (df['UnitPrice']>0)]

    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    if df['InvoiceDate'].isnull().any():
        # intentar con dayfirst (d/m/Y)
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], dayfirst=True, errors='coerce')

    df = df.dropna(subset=['InvoiceDate'])
    logging.info(f"Shape después de preprocesamiento: {df.shape}")
    return df

# ---------------- matriz transaccional ----------------
def create_transaction_matrix(df):
    """
    Crea matriz InvoiceNo x Description con valores binarios (1 si aparece en la transacción)
    """
    logging.info("Creando matriz transaccional (InvoiceNo x Description) binarizada")
    basket = (df.groupby(['InvoiceNo','Description'])['Quantity']
                .sum().unstack().fillna(0))
    basket_binary = (basket > 0).astype(int)
    logging.info(f"Matriz transaccional con shape: {basket_binary.shape}")
    return basket_binary

# ---------------- Apriori (si está disponible) ----------------
def run_apriori_rules(basket_binary, min_support=0.02, min_confidence=0.3, outdir='outputs'):
    if not USE_MLXTEND:
        logging.warning("mlxtend no disponible. Saltando Apriori.")
        return None

    logging.info("Ejecutando Apriori (mlxtend)")
    frequent_items = apriori(basket_binary, min_support=min_support, use_colnames=True)
    logging.info(f"Itemsets frecuentes encontrados: {len(frequent_items)}")

    if frequent_items.empty:
        logging.warning("No se encontraron itemsets frecuentes con el min_support dado")
        return None

    rules = association_rules(frequent_items, metric='confidence', min_threshold=min_confidence)
    if rules.empty:
        logging.warning("No se generaron reglas con los umbrales dados")
        return None

    rules = rules.sort_values(by='lift', ascending=False).reset_index(drop=True)
    # convertir conjuntos a strings legibles
    for col in ['antecedents','consequents']:
        rules[col] = rules[col].apply(lambda s: ', '.join(sorted(list(s))))
    out_path = os.path.join(outdir, 'rules_apriori.csv')
    rules.to_csv(out_path, index=False)
    logging.info(f"Reglas Apriori guardadas en: {out_path}")
    return rules

# ---------------- Fallback por pares (vectorizado) ----------------
def run_pairs_fallback(basket_binary, top_n_items=50, outdir='outputs'):
    """
    Calcula reglas por pares usando co-ocurrencia X.T.dot(X).
    Limita a top_n_items por frecuencia para controlar memoria y tiempo.
    """
    logging.info("Ejecutando fallback por pares (co-ocurrencia)")
    X = basket_binary.values  # (n_trans, n_items)
    n_trans = X.shape[0]
    item_names = basket_binary.columns.tolist()

    co_counts = X.T.dot(X)  # (n_items, n_items)
    item_counts = np.diag(co_counts)

    # seleccionar top items por frecuencia
    top_idx = np.argsort(item_counts)[-top_n_items:][::-1]
    pairs = []
    for i_idx in range(len(top_idx)):
        i = top_idx[i_idx]
        for j_idx in range(i_idx+1, len(top_idx)):
            j = top_idx[j_idx]
            count_ab = int(co_counts[i,j])
            if count_ab == 0:
                continue
            support = count_ab / n_trans
            conf_a_b = count_ab / item_counts[i] if item_counts[i] > 0 else 0
            conf_b_a = count_ab / item_counts[j] if item_counts[j] > 0 else 0
            lift = support / ((item_counts[i]/n_trans)*(item_counts[j]/n_trans)) if (item_counts[i]>0 and item_counts[j]>0) else 0
            pairs.append({
                'antecedent': item_names[i],
                'consequent': item_names[j],
                'count_ab': count_ab,
                'support': support,
                'confidence_a_b': conf_a_b,
                'confidence_b_a': conf_b_a,
                'lift': lift
            })

    pairs_df = pd.DataFrame(pairs).sort_values(by='lift', ascending=False).reset_index(drop=True)
    out_path = os.path.join(outdir, 'rules_pairs_top.csv')
    pairs_df.to_csv(out_path, index=False)
    logging.info(f"Reglas pares guardadas en: {out_path}")
    return pairs_df

# ---------------- visualizaciones ----------------
def plot_top_items_support(basket_binary, outpath, top_n=10):
    support = (basket_binary.sum()/basket_binary.shape[0]).sort_values(ascending=False)
    top = support.head(top_n)
    plt.figure(figsize=(10,5))
    plt.bar(range(len(top)), top.values)
    plt.xticks(range(len(top)), top.index, rotation=45, ha='right')
    plt.ylabel('Support (fraction of transactions)')
    plt.title('Top items por support')
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()
    logging.info(f"Gráfico top items guardado en: {outpath}")

# ---------------- RFM y clustering ----------------
def compute_rfm_and_cluster(df, outdir, k_min=2, k_max=8):
    logging.info("Calculando tabla RFM")
    latest_date = df['InvoiceDate'].max() + timedelta(days=1)
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (latest_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalPrice': 'sum'
    }).reset_index()
    rfm.columns = ['CustomerID','Recency','Frequency','Monetary']
    rfm = rfm.dropna(subset=['CustomerID'])
    rfm = rfm[rfm['Monetary']>0].reset_index(drop=True)

    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm[['Recency','Frequency','Monetary']])

    inertia = []
    sil_scores = []
    K_range = range(k_min, k_max+1)
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(rfm_scaled)
        inertia.append(km.inertia_)
        try:
            sil_scores.append(silhouette_score(rfm_scaled, km.labels_))
        except Exception:
            sil_scores.append(np.nan)

    eval_df = pd.DataFrame({'k': list(K_range), 'inertia': inertia, 'silhouette': sil_scores})
    eval_out = os.path.join(outdir, 'Evaluaci_n_K__Elbow___Silhouette_.csv')
    eval_df.to_csv(eval_out, index=False)
    logging.info(f"Evaluación de K guardada en: {eval_out}")

    if not all(np.isnan(sil_scores)):
        k_final = int(K_range[np.nanargmax(sil_scores)])
    else:
        k_final = 4
    logging.info(f"K seleccionado: {k_final}")

    km_final = KMeans(n_clusters=k_final, random_state=42, n_init=10)
    rfm['Cluster'] = km_final.fit_predict(rfm_scaled)

    rfm_out = os.path.join(outdir, 'rfm_clusters.csv')
    rfm.to_csv(rfm_out, index=False)
    logging.info(f"RFM con clusters guardada en: {rfm_out}")

    profile = rfm.groupby('Cluster')[['Recency','Frequency','Monetary']].agg(['mean','median','count'])
    # aplanar multiindex de columnas
    profile.columns = ['_'.join(col).strip() for col in profile.columns.values]
    profile = profile.reset_index()
    profile_out = os.path.join(outdir, 'Perfil_de_clusters.csv')
    profile.to_csv(profile_out, index=False)
    logging.info(f"Perfil de clusters guardado en: {profile_out}")

    # Scatter Recency vs Monetary
    fig_scatter = os.path.join(outdir, 'rfm_scatter.png')
    plt.figure(figsize=(8,6))
    plt.scatter(rfm['Recency'], rfm['Monetary'], s=20)
    plt.xlabel('Recency (days)')
    plt.ylabel('Monetary (total spend)')
    plt.title('Recency vs Monetary (clientes)')
    plt.tight_layout()
    plt.savefig(fig_scatter)
    plt.close()
    logging.info(f"Scatter RFM guardado en: {fig_scatter}")

    return rfm, profile, eval_df

# ---------------- guardado preprocesado ----------------
def save_preprocessed(df, outdir):
    out = os.path.join(outdir, 'ventas_preprocessed.csv')
    df.to_csv(out, index=False)
    logging.info(f"Preprocesado guardado en: {out}")
    return out

# ---------------- main ----------------
def main(args):
    outdir = ensure_dir(args.outdir)

    df = load_and_preprocess(args.input)
    save_preprocessed(df, outdir)

    basket = create_transaction_matrix(df)
    plot_top_items_support(basket, os.path.join(outdir,'top10_support.png'), top_n=10)

    # Reglas: Apriori si se solicita y está disponible; sino fallback
    if args.use_apriori:
        if USE_MLXTEND:
            run_apriori_rules(basket, min_support=args.min_support, min_confidence=args.min_confidence, outdir=outdir)
        else:
            logging.warning("Se solicitó Apriori pero mlxtend no está instalado. Usando fallback pares.")
            run_pairs_fallback(basket, top_n_items=args.top_n_items, outdir=outdir)
    else:
        run_pairs_fallback(basket, top_n_items=args.top_n_items, outdir=outdir)

    compute_rfm_and_cluster(df, outdir, k_min=args.k_min, k_max=args.k_max)

    logging.info("Ejecución completada. Revisa la carpeta de salida para resultados y gráficas.")
    logging.info(f"Archivos en {outdir}: {os.listdir(outdir)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Minería de transacciones: Market Basket + RFM + Clustering')
    parser.add_argument('--input', required=True, help='Path al CSV de transacciones (ventas_ejemplo.csv)')
    parser.add_argument('--outdir', default='outputs', help='Carpeta donde guardar resultados')
    parser.add_argument('--min_support', type=float, default=0.02, help='Min support para Apriori')
    parser.add_argument('--min_confidence', type=float, default=0.3, help='Min confidence para reglas Apriori')
    parser.add_argument('--use_apriori', action='store_true', help='Forzar uso de Apriori (si mlxtend está instalado)')
    parser.add_argument('--top_n_items', type=int, default=50, help='Número máximo de items a considerar en fallback pares')
    parser.add_argument('--k_min', type=int, default=2, help='K mínimo para evaluación de clusters')
    parser.add_argument('--k_max', type=int, default=8, help='K máximo para evaluación de clusters')
    args = parser.parse_args()

    main(args)