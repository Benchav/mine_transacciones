# scripts/clean_descriptions.py
import pandas as pd
import unidecode, re, os

df = pd.read_csv('data/ventas_ejemplo.csv', encoding='ISO-8859-1', parse_dates=['InvoiceDate'])
def clean_desc(s):
    if pd.isna(s): return s
    s = str(s).lower().strip()
    s = unidecode.unidecode(s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s

df['Description_clean'] = df['Description'].apply(clean_desc)
os.makedirs('outputs', exist_ok=True)
df.to_csv('outputs/ventas_preprocessed.csv', index=False)  # sobrescribe preprocesado con columna nueva
print("Descriptions limpiadas y guardadas en outputs/ventas_preprocessed.csv")