import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import joblib

# Load data
df = pd.read_csv('student_spending_data.csv')

# Preprocessing
features_for_clustering = ['uang_saku', 'pengeluaran_makanan', 'pengeluaran_transport', 
                          'pengeluaran_hiburan', 'rasio_pengeluaran', 'semester']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features_for_clustering])

print("=== K-MEANS CLUSTERING ===")

# Menentukan jumlah cluster optimal menggunakan Elbow Method
inertias = []
silhouette_scores = []
K_range = range(2, 8)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))

# Plot Elbow Method
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(K_range, inertias, 'bo-')
plt.title('Elbow Method untuk Optimal K')
plt.xlabel('Jumlah Cluster (K)')
plt.ylabel('Inertia')
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(K_range, silhouette_scores, 'ro-')
plt.title('Silhouette Score untuk setiap K')
plt.xlabel('Jumlah Cluster (K)')
plt.ylabel('Silhouette Score')
plt.grid(True)

plt.tight_layout()
plt.savefig('optimal_k_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Pilih K optimal (berdasarkan analisis, kita pilih K=3 untuk kategori Hemat, Sedang, Boros)
optimal_k = 3
print(f"\nMenggunakan K = {optimal_k} cluster")

# Fitting final model
kmeans_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df['cluster'] = kmeans_final.fit_predict(X_scaled)

# Analisis hasil clustering
print("\n=== HASIL CLUSTERING ===")
print(f"Silhouette Score: {silhouette_score(X_scaled, df['cluster']):.3f}")

# Analisis karakteristik setiap cluster
cluster_analysis = df.groupby('cluster').agg({
    'uang_saku': ['mean', 'std'],
    'total_pengeluaran': ['mean', 'std'],
    'rasio_pengeluaran': ['mean', 'std'],
    'pengeluaran_makanan': 'mean',
    'pengeluaran_transport': 'mean',
    'pengeluaran_hiburan': 'mean',
    'semester': 'mean'
}).round(0)

print("\nKarakteristik setiap cluster:")
print(cluster_analysis)

# Labeling cluster berdasarkan rasio pengeluaran
cluster_means = df.groupby('cluster')['rasio_pengeluaran'].mean().sort_values()
cluster_labels = {
    cluster_means.index[0]: 'Hemat',
    cluster_means.index[1]: 'Sedang', 
    cluster_means.index[2]: 'Boros'
}

df['kategori_pengeluaran'] = df['cluster'].map(cluster_labels)

print(f"\nLabel cluster:")
for cluster, label in cluster_labels.items():
    print(f"Cluster {cluster}: {label}")

# Distribusi cluster
print(f"\nDistribusi kategori:")
print(df['kategori_pengeluaran'].value_counts())

# Visualisasi cluster
plt.figure(figsize=(15, 10))

plt.subplot(2, 2, 1)
colors = ['green', 'orange', 'red']
for i, (cluster, label) in enumerate(cluster_labels.items()):
    cluster_data = df[df['cluster'] == cluster]
    plt.scatter(cluster_data['uang_saku'], cluster_data['total_pengeluaran'], 
               c=colors[i], label=label, alpha=0.6)
plt.xlabel('Uang Saku (Rp)')
plt.ylabel('Total Pengeluaran (Rp)')
plt.title('Cluster berdasarkan Uang Saku vs Total Pengeluaran')
plt.legend()

plt.subplot(2, 2, 2)
for i, (cluster, label) in enumerate(cluster_labels.items()):
    cluster_data = df[df['cluster'] == cluster]
    plt.scatter(cluster_data['rasio_pengeluaran'], cluster_data['semester'], 
               c=colors[i], label=label, alpha=0.6)
plt.xlabel('Rasio Pengeluaran')
plt.ylabel('Semester')
plt.title('Cluster berdasarkan Rasio Pengeluaran vs Semester')
plt.legend()

plt.subplot(2, 2, 3)
spending_by_cluster = df.groupby('kategori_pengeluaran')[['pengeluaran_makanan', 'pengeluaran_transport', 'pengeluaran_hiburan']].mean()
spending_by_cluster.plot(kind='bar', ax=plt.gca())
plt.title('Rata-rata Pengeluaran per Kategori')
plt.xticks(rotation=45)
plt.ylabel('Pengeluaran (Rp)')

plt.subplot(2, 2, 4)
df['kategori_pengeluaran'].value_counts().plot(kind='pie', autopct='%1.1f%%')
plt.title('Distribusi Kategori Pengeluaran')

plt.tight_layout()
plt.savefig('clustering_results.png', dpi=300, bbox_inches='tight')
plt.show()

# Save model dan scaler
joblib.dump(kmeans_final, 'kmeans_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(cluster_labels, 'cluster_labels.pkl')

# Save hasil clustering
df.to_csv('student_spending_clustered.csv', index=False)

print("\nModel dan hasil clustering berhasil disimpan!")