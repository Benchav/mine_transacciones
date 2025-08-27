# scripts/generate_rule_interpretations.py
import pandas as pd
import os

os.makedirs('outputs', exist_ok=True)

apriori_path = 'outputs_apriori/rules_apriori.csv'
fallback_path = 'outputs/rules_pairs_top.csv'

if os.path.exists(apriori_path):
    rules = pd.read_csv(apriori_path)
    use_apriori = True
else:
    rules = pd.read_csv(fallback_path)
    use_apriori = False

# Normalizar nombres de columnas para facilitar
if use_apriori:
    # columnas esperadas: antecedents, consequents, support, confidence, lift
    cols_map = {
        'antecedents': 'antecedents',
        'consequents': 'consequents',
        'support': 'support',
        'confidence': 'confidence',
        'lift': 'lift'
    }
else:
    # fallback: antecedent, consequent, support, confidence_a_b, lift
    cols_map = {
        'antecedents': 'antecedent',
        'consequents': 'consequent',
        'support': 'support',
        'confidence': 'confidence_a_b',
        'lift': 'lift'
    }

# Tomar top 5 (si hay menos, toma lo que haya)
topn = rules.head(5)

out_lines = []
out_lines.append("Interpretaciones automatizadas de las 5 reglas top\n")
out_lines.append("Fuente: " + ("Apriori (outputs_apriori/rules_apriori.csv)" if use_apriori else "Fallback pares (outputs/rules_pairs_top.csv)"))
out_lines.append("\n")

for idx, row in topn.iterrows():
    antecedents = str(row[cols_map['antecedents']])
    consequents = str(row[cols_map['consequents']])
    support = float(row[cols_map['support']]) if cols_map['support'] in row else None
    confidence = float(row[cols_map['confidence']]) if cols_map['confidence'] in row else None
    lift = float(row[cols_map['lift']]) if cols_map['lift'] in row else None

    # Formatear números de forma legible
    support_pct = f"{support*100:.2f}%" if support is not None else "N/A"
    confidence_pct = f"{confidence*100:.2f}%" if confidence is not None else "N/A"
    lift_str = f"{lift:.2f}" if lift is not None else "N/A"

    paragraph = (
        f"Regla {idx+1}: {antecedents} -> {consequents}\n"
        f"- Support: {support_pct}\n"
        f"- Confidence (A->B): {confidence_pct}\n"
        f"- Lift: {lift_str}\n\n"
        f"Interpretación práctica:\n"
        f"Cuando un cliente compra [{antecedents}], la probabilidad de que también compre [{consequents}] es {confidence_pct}.\n"
        f"El lift de {lift_str} indica que la relación es {('fuerte' if lift and lift>1.5 else 'moderada' if lift and lift>1.1 else 'débil' if lift and lift>1 else 'no informativa')} en comparación al azar.\n"
        f"Acción sugerida: mostrar [{consequents}] como producto sugerido en la página de [{antecedents}] o crear un combo/promoción durante un periodo de prueba y medir el uplift.\n"
        "-----\n"
    )
    out_lines.append(paragraph)

out_path = 'outputs/rules_interpretations.txt'
with open(out_path, 'w', encoding='utf-8') as f:
    f.writelines("\n".join(out_lines))

print("Interpretaciones generadas en:", out_path)
