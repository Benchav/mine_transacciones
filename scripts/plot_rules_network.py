# scripts/plot_rules_network.py
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

os.makedirs('outputs_apriori', exist_ok=True)
rules_path = 'outputs_apriori/rules_apriori.csv'
rules = pd.read_csv(rules_path)

# Tomar top N reglas por lift (ajusta N)
topN = 50
top = rules.head(topN)

G = nx.DiGraph()
for _, r in top.iterrows():
    a = r['antecedents']; b = r['consequents']; w = float(r['lift'])
    # nodos pueden ser conjuntos, aquí están en forma de string
    G.add_edge(a, b, weight=w)

plt.figure(figsize=(12,10))
pos = nx.spring_layout(G, k=0.6, seed=42)
weights = [G[u][v]['weight'] for u,v in G.edges()]
nx.draw_networkx_nodes(G, pos, node_size=400, node_color='lightblue')
nx.draw_networkx_edges(G, pos, width=[max(0.5,min(6,w)) for w in weights], arrowstyle='->', arrowsize=12)
nx.draw_networkx_labels(G, pos, font_size=8)
plt.title('Red de reglas (top %d por lift)' % topN)
plt.axis('off')
plt.tight_layout()
plt.savefig('outputs_apriori/rules_network.png', dpi=200)
plt.show()