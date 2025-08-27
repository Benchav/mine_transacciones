# scripts/plot_rules_network.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

# Paths
apriori_path = "outputs_apriori/rules_apriori.csv"
pairs_path = "outputs/rules_pairs_top.csv"
out_path = "outputs_apriori/rules_network.png"

# Cargar reglas Apriori si existen
rules = None
if os.path.exists(apriori_path):
    rules = pd.read_csv(apriori_path)
    if rules.empty:
        rules = None

# Si Apriori está vacío → usar fallback por pares
if rules is None and os.path.exists(pairs_path):
    rules = pd.read_csv(pairs_path).rename(columns={
        "antecedent": "antecedents",
        "consequent": "consequents",
        "confidence_a_b": "confidence"
    })

if rules is None or rules.empty:
    print("⚠️ No hay reglas para graficar (ni Apriori ni fallback).")
    exit()

# Quedarse con top 50 reglas por lift
rules = rules.sort_values(by="lift", ascending=False).head(50)

# Crear grafo
G = nx.DiGraph()
for _, row in rules.iterrows():
    antecedent = row["antecedents"]
    consequent = row["consequents"]
    lift = row["lift"]
    conf = row["confidence"] if "confidence" in row else row["confidence_a_b"]

    G.add_edge(antecedent, consequent, weight=lift, confidence=conf)

# Dibujar
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, k=0.5, seed=42)
edges = nx.draw_networkx_edges(G, pos, alpha=0.5)
nodes = nx.draw_networkx_nodes(G, pos, node_color="skyblue", node_size=800)
labels = nx.draw_networkx_labels(G, pos, font_size=8)

plt.title("Red de Reglas (Top 50 por Lift)")
plt.axis("off")
plt.tight_layout()
plt.savefig(out_path)
plt.close()

print(f"✅ Red de reglas guardada en {out_path}")