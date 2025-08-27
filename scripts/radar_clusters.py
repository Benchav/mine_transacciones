# scripts/radar_clusters.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import os

rfm = pd.read_csv('outputs/rfm_clusters.csv')
profile = rfm.groupby('Cluster')[['Recency','Frequency','Monetary']].mean()

scaler = MinMaxScaler()
profile_scaled = pd.DataFrame(scaler.fit_transform(profile), columns=profile.columns, index=profile.index)

categories = list(profile_scaled.columns)
N = len(categories)
angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
angles += angles[:1]

plt.figure(figsize=(8,6))
for idx in profile_scaled.index:
    values = profile_scaled.loc[idx].tolist()
    values += values[:1]
    plt.polar(angles, values, label=f'Cluster {idx}')
plt.thetagrids(np.degrees(angles[:-1]), categories)
plt.title('Perfil RFM por cluster (normalizado)')
plt.legend(loc='upper right', bbox_to_anchor=(1.2,1.1))
os.makedirs('outputs', exist_ok=True)
plt.savefig('outputs/rfm_radar.png', bbox_inches='tight', dpi=200)
plt.show()
