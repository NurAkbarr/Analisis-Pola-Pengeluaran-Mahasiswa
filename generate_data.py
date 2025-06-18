import pandas as pd
import numpy as np
import random

# Set random seed untuk konsistensi
np.random.seed(42)
random.seed(42)

def generate_student_spending_data(n_samples=500):
    """Generate realistic student spending data"""
    
    data = []
    
    for i in range(n_samples):
        # Generate basic info
        semester = random.randint(1, 8)
        
        # Uang saku berdasarkan semester (mahasiswa senior biasanya lebih mandiri)
        if semester <= 2:
            uang_saku_base = np.random.normal(800000, 200000)  # Semester awal
        elif semester <= 4:
            uang_saku_base = np.random.normal(900000, 250000)  # Semester tengah
        else:
            uang_saku_base = np.random.normal(1000000, 300000)  # Semester akhir
            
        uang_saku = max(400000, min(2000000, uang_saku_base))  # Batasi range
        
        # Pengeluaran makanan (30-50% dari uang saku)
        makanan_ratio = np.random.uniform(0.3, 0.5)
        pengeluaran_makanan = uang_saku * makanan_ratio * np.random.uniform(0.8, 1.2)
        
        # Pengeluaran transport (10-25% dari uang saku)
        transport_ratio = np.random.uniform(0.1, 0.25)
        pengeluaran_transport = uang_saku * transport_ratio * np.random.uniform(0.7, 1.3)
        
        # Pengeluaran hiburan (5-30% dari uang saku)
        hiburan_ratio = np.random.uniform(0.05, 0.3)
        pengeluaran_hiburan = uang_saku * hiburan_ratio * np.random.uniform(0.5, 1.5)
        
        # Pastikan total pengeluaran masuk akal
        total_pengeluaran = pengeluaran_makanan + pengeluaran_transport + pengeluaran_hiburan
        
        # Jika total melebihi uang saku, sesuaikan
        if total_pengeluaran > uang_saku * 1.1:  # Toleransi 10%
            factor = (uang_saku * 0.95) / total_pengeluaran
            pengeluaran_makanan *= factor
            pengeluaran_transport *= factor
            pengeluaran_hiburan *= factor
        
        # Bulatkan ke ribuan terdekat
        data.append({
            'uang_saku': round(uang_saku, -3),
            'pengeluaran_makanan': round(pengeluaran_makanan, -3),
            'pengeluaran_transport': round(pengeluaran_transport, -3),
            'pengeluaran_hiburan': round(pengeluaran_hiburan, -3),
            'semester': semester
        })
    
    return pd.DataFrame(data)

# Generate data
df = generate_student_spending_data(500)

# Tambahkan beberapa kolom turunan untuk analisis
df['total_pengeluaran'] = df['pengeluaran_makanan'] + df['pengeluaran_transport'] + df['pengeluaran_hiburan']
df['rasio_pengeluaran'] = df['total_pengeluaran'] / df['uang_saku']
df['sisa_uang'] = df['uang_saku'] - df['total_pengeluaran']

# Simpan dataset
df.to_csv('student_spending_data.csv', index=False)

print("Dataset berhasil dibuat!")
print(f"Total data: {len(df)} mahasiswa")
print("\nContoh data:")
print(df.head())
print("\nStatistik dasar:")
print(df.describe())