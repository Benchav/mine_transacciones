# scripts/run_apriori.py
import os, pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

os.makedirs('outputs_apriori', exist_ok=True)

# Cargar preprocesado si existe, sino el CSV original
if os.path.exists('outputs/ventas_preprocessed.csv'):
    df = pd.read_csv('outputs/ventas_preprocessed.csv', parse_dates=['InvoiceDate'])
else:
    df = pd.read_csv('data/ventas_ejemplo.csv', encoding='ISO-8859-1', parse_dates=['InvoiceDate'])

# Opcional: usar 'Description_clean' si limpiaste (ver paso 4)
desc_col = 'Description' 
if 'Description_clean' in df.columns:
    desc_col = 'Description_clean'

# Crear matriz transaccional binaria
basket = (df.groupby(['InvoiceNo', desc_col])['Quantity'].sum().unstack().fillna(0))
basket_binary = (basket > 0).astype(int)

# Apriori
min_support = 0.02   # cambia a 0.01 si quieres 1%
frequent_items = apriori(basket_binary, min_support=min_support, use_colnames=True)
print(f"Itemsets frecuentes: {len(frequent_items)}")

# Reglas
min_confidence = 0.3
rules = association_rules(frequent_items, metric='confidence', min_threshold=min_confidence)
rules = rules.sort_values(by='lift', ascending=False).reset_index(drop=True)

# Convertir conjuntos a strings
rules['antecedents'] = rules['antecedents'].apply(lambda s: ', '.join(sorted(list(s))))
rules['consequents'] = rules['consequents'].apply(lambda s: ', '.join(sorted(list(s))))

out = 'outputs_apriori/rules_apriori.csv'
rules.to_csv(out, index=False)
print(f"Reglas guardadas en {out}")