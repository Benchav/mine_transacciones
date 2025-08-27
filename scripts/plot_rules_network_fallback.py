# scripts/plot_rules_network_fallback.py
import os, math, pandas as pd, networkx as nx, matplotlib.pyplot as plt

CSV_PATH = 'outputs/rules_pairs_top.csv'
OUT_IMG = 'outputs/rules_network_fallback.png'
TOPN = 50

def safe_str(s, maxlen=60):
    if pd.isna(s): return ''
    s = str(s).strip()
    if len(s) > maxlen: return s[:maxlen-3] + '...'
    return s

if not os.path.exists(CSV_PATH):
    print("ERROR: no existe", CSV_PATH)
    raise SystemExit(1)

df = pd.read_csv(CSV_PATH)
if df.empty:
    print("ERROR: CSV fallback vacío:", CSV_PATH)
    raise SystemExit(1)

needed = ['antecedent','consequent','support','confidence_a_b','lift']
missing = [c for c in needed if c not in df.columns]
if missing:
    print("ERROR: faltan columnas en fallback CSV:", missing)
    print("Columnas disponibles:", df.columns.tolist())
    raise SystemExit(1)

df = df.dropna(subset=['antecedent','consequent'])
df = df.sort_values(by='lift', ascending=False).head(TOPN)
if df.empty:
    print("No hay reglas válidas en fallback tras filtrar.")
    raise SystemExit(1)

G = nx.DiGraph()
for _, r in df.iterrows():
    a = safe_str(r['antecedent']); b = safe_str(r['consequent'])
    if a=='' or b=='': continue
    try:
        lift = float(r['lift'])
    except:
        lift = 1.0
    G.add_edge(a,b,weight=lift)

if G.number_of_edges() == 0:
    print("No se añadieron aristas al grafo (datos inválidos).")
    raise SystemExit(1)

deg = dict(G.degree()); maxdeg = max(deg.values()) if deg else 1
pos = nx.spring_layout(G, k=0.6, seed=42, iterations=250)

node_sizes = [200 + (1800 * (deg[n]/maxdeg)) for n in G.nodes()]
lifts = [float(G[u][v]['weight']) for u,v in G.edges()]
minl, maxl = min(lifts), max(lifts)
if math.isclose(minl,maxl):
    edge_widths = [1.5 for _ in lifts]
else:
    edge_widths = [0.5 + 3.5 * ((w-minl)/(maxl-minl)) for w in lifts]

plt.figure(figsize=(14,11))
nx.draw_networkx_nodes(G,pos,node_size=node_sizes)
nx.draw_networkx_edges(G,pos,width=edge_widths,arrowsize=15,arrowstyle='-|>')
nx.draw_networkx_labels(G,pos,font_size=8)
plt.title(f'Reglas (fallback) - top {len(df)} por lift')
plt.axis('off')
plt.tight_layout()
plt.savefig(OUT_IMG, dpi=300, bbox_inches='tight')
plt.close()
print("Red de reglas (fallback) guardada en:", OUT_IMG)
