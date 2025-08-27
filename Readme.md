# README — Minería de Transacciones (Market Basket + RFM + Clustering)

Este proyecto implementa un pipeline completo para:  
- **Análisis de cesta de compras (Market Basket Analysis)** con reglas de asociación (Apriori o fallback por pares).  
- **Segmentación de clientes (RFM + K-Means)** con evaluación de `k` y perfiles de clusters.  
- **Generación automática de reportes** en Word con tablas, reglas, gráficos y radar.  

El flujo está diseñado para que, incluso si eliminas todos los resultados (`outputs/` y `outputs_apriori/`), puedas **regenerar todo paso a paso** con los comandos que verás a continuación.  

---

## 📂 Estructura del Proyecto

```
mine_transacciones/
├─ data/
│  └─ ventas_ejemplo.csv
├─ outputs/                # Se regenera al correr los scripts
│  ├─ ventas_preprocessed.csv
│  ├─ rules_pairs_top.csv
│  ├─ rules_network_fallback.png
│  ├─ rfm_clusters.csv
│  ├─ Perfil_de_clusters.csv
│  ├─ Evaluaci_n_K__Elbow___Silhouette_.csv
│  ├─ rfm_scatter.png / rfm_scatter_colored.png
│  ├─ rfm_radar.png
│  ├─ top10_support.png
│  ├─ rules_interpretations.txt
│  ├─ top5_rules.txt
│  └─ informe_minero.docx
├─ outputs_apriori/        # Se crea si usas Apriori
│  ├─ rules_apriori.csv
│  └─ rules_network.png
├─ scripts/
│  ├─ clean_descriptions.py
│  ├─ run_apriori.py
│  ├─ plot_rules_network.py
│  ├─ plot_rules_network_fallback.py
│  ├─ radar_clusters.py
│  ├─ generate_rule_interpretations.py
│  ├─ top5_rules_to_txt.py
│  ├─ generate_report.py
│  └─ generate_report_extended.py
├─ src/
│  └─ mineria_ejercicios.py
├─ venv/                   # Entorno virtual (no versionar)
├─ requirements.txt
└─ README.md
```

---

## ⚙️ Instalación de dependencias

Desde cero (Windows PowerShell):

```powershell
# 1) Clonar o entrar a la carpeta
cd C:\Users\joshu\Downloads\mine_transacciones

# 2) Crear entorno virtual
python -m venv venv

# 3) Activar entorno
.\venv\Scripts\Activate.ps1

# 4) Instalar dependencias
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

En Linux / macOS:

```bash
cd ~/mine_transacciones
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## ▶️ Flujo paso a paso para regenerar todo

### 1. Limpieza de descripciones (opcional)
```powershell
python scripts/clean_descriptions.py
```

Esto normaliza nombres de productos (`Descripción → description limpia`).

---

### 2. Ejecutar análisis completo (pipeline principal)
Si tu profesor borró todos los **CSV y gráficos**, este comando recrea `ventas_preprocessed.csv`, reglas, RFM y clusters:

```powershell
python src/mineria_ejercicios.py --input data/ventas_ejemplo.csv --outdir outputs
```

Opciones:
- `--use_apriori` → intenta usar Apriori con `mlxtend`.
- `--min_support 0.01` → soporte mínimo (ajústalo si no aparecen reglas).
- `--min_confidence 0.25` → confianza mínima.
- `--top_n_items 50` → número de productos en fallback.
- `--k_min 2 --k_max 8` → rango de clusters para K-Means.

Ejemplo con Apriori:

```powershell
python src/mineria_ejercicios.py --input data/ventas_ejemplo.csv --outdir outputs_apriori --use_apriori --min_support 0.01 --min_confidence 0.25
```

---

### 3. Generar red de reglas
Si `rules_apriori.csv` está vacío, usa fallback.  
El siguiente script ya detecta si debe usar Apriori o fallback:

```powershell
python scripts/plot_rules_network.py
```

Resultado → `outputs_apriori/rules_network.png` o `outputs/rules_network_fallback.png`

---

### 4. Interpretar reglas y extraer top 5
```powershell
python scripts/generate_rule_interpretations.py
python scripts/top5_rules_to_txt.py
```

Genera:  
- `outputs/rules_interpretations.txt`  
- `outputs/top5_rules.txt`  

---

### 5. Visualizar clusters con radar
```powershell
python scripts/radar_clusters.py
```

Genera `outputs/rfm_radar.png`.

---

### 6. Generar informe automático
Versión básica:
```powershell
python scripts/generate_report.py
```

Versión extendida (incluye más tablas y gráficos):
```powershell
python scripts/generate_report_extended.py
```

Resultado:  
- `outputs/informe_minero.docx`  
- o `outputs/informe_minero_extended.docx`

---

## 📊 Archivos de salida finales esperados

- `ventas_preprocessed.csv` → dataset limpio.  
- `rules_apriori.csv` / `rules_pairs_top.csv` → reglas con métricas.  
- `rules_network.png` o `rules_network_fallback.png` → red de reglas.  
- `top10_support.png` → gráfico de productos más frecuentes.  
- `top5_rules.txt` y `rules_interpretations.txt` → reglas principales.  
- `rfm_clusters.csv` → clientes con cluster asignado.  
- `Perfil_de_clusters.csv` → perfil medio de cada cluster.  
- `rfm_scatter.png` y `rfm_radar.png` → gráficos de clientes.  
- `informe_minero.docx` → reporte con resultados.  

---

## 🚀 Ejemplo de regeneración completa (si borraste todo)

```powershell
# Activar entorno
.\venv\Scripts\Activate.ps1

# 1) Ejecutar pipeline principal
python src/mineria_ejercicios.py --input data/ventas_ejemplo.csv --outdir outputs --use_apriori --min_support 0.01 --min_confidence 0.25

# 2) Generar red de reglas
python scripts/plot_rules_network.py

# 3) Generar interpretaciones y top reglas
python scripts/generate_rule_interpretations.py
python scripts/top5_rules_to_txt.py

# 4) Generar radar de clusters
python scripts/radar_clusters.py

# 5) Generar informe final
python scripts/generate_report_extended.py
```

Al terminar tendrás todos los **CSV, gráficos y el informe Word** listos. ✅  


**Autor:** Joshua Chaves — [https://joshuachavez.vercel.app/](https://joshuachavez.vercel.app/)  