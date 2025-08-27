import pandas as pd
import os

# Cambia la ruta según sea apriori o fallback
apriori_path = 'outputs_apriori/rules_apriori.csv'
fallback_path = 'outputs/rules_pairs_top.csv'

if os.path.exists(apriori_path):
    rules = pd.read_csv(apriori_path)
    cols = ['antecedents','consequents','support','confidence','lift']
    rules = rules[cols].head(5)
else:
    rules = pd.read_csv(fallback_path)
    cols = ['antecedent','consequent','support','confidence_a_b','lift']
    rules = rules[cols].head(5)

out_txt = 'outputs/top5_rules.txt'
with open(out_txt, 'w', encoding='utf-8') as f:
    f.write(rules.to_string(index=False))
print('Top 5 reglas guardadas en', out_txt)
