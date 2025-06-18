import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('student_spending_data.csv')

print("=== EKSPLORASI DATA ===")
print(f"Shape data: {df.shape}")
print(f"Missing values: {df.isnull().sum().sum()}")
print("\nInfo dataset:")
print(df.info())

# Visualisasi distribusi data
plt.figure(figsize=(15, 10))

plt.subplot(2, 3, 1)
plt.hist(df['uang_saku'], bins=30, alpha=0.7, color='skyblue')
plt.title('Distribusi Uang Saku')
plt.xlabel('Uang Saku (Rp)')

plt.subplot(2, 3, 2)
plt.hist(df['total_pengeluaran'], bins=30, alpha=0.7, color='lightgreen')
plt.title('Distribusi Total Pengeluaran')
plt.xlabel('Total Pengeluaran (Rp)')

plt.subplot(2, 3, 3)
plt.hist(df['rasio_pengeluaran'], bins=30, alpha=0.7, color='salmon')
plt.title('Distribusi Rasio Pengeluaran')
plt.xlabel('Rasio Pengeluaran')

plt.subplot(2, 3, 4)
plt.scatter(df['uang_saku'], df['total_pengeluaran'], alpha=0.6)
plt.title('Uang Saku vs Total Pengeluaran')
plt.xlabel('Uang Saku (Rp)')
plt.ylabel('Total Pengeluaran (Rp)')

plt.subplot(2, 3, 5)
semester_spending = df.groupby('semester')['rasio_pengeluaran'].mean()
plt.bar(semester_spending.index, semester_spending.values, color='orange', alpha=0.7)
plt.title('Rata-rata Rasio Pengeluaran per Semester')
plt.xlabel('Semester')
plt.ylabel('Rasio Pengeluaran')

plt.subplot(2, 3, 6)
spending_breakdown = df[['pengeluaran_makanan', 'pengeluaran_transport', 'pengeluaran_hiburan']].mean()
plt.pie(spending_breakdown.values, labels=spending_breakdown.index, autopct='%1.1f%%')
plt.title('Rata-rata Breakdown Pengeluaran')

plt.tight_layout()
plt.savefig('data_exploration.png', dpi=300, bbox_inches='tight')
plt.show()

print("\n=== PREPROCESSING DATA ===")

# Fitur untuk clustering
features_for_clustering = ['uang_saku', 'pengeluaran_makanan', 'pengeluaran_transport', 
                          'pengeluaran_hiburan', 'rasio_pengeluaran', 'semester']

# Normalisasi data untuk clustering
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features_for_clustering])

print("Data preprocessing selesai!")
print(f"Features untuk clustering: {features_for_clustering}")
print(f"Shape data setelah scaling: {X_scaled.shape}")