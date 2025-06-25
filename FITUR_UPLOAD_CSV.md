# 📁 Fitur Upload CSV - Analisis Pola Pengeluaran Mahasiswa

## 🎯 Overview
Fitur upload CSV memungkinkan pengguna untuk menganalisis data pengeluaran mahasiswa secara batch (multiple data sekaligus) dengan mengupload file CSV.

## ✨ Fitur Utama

### 1. 📤 Upload File CSV
- Upload file CSV dengan data pengeluaran mahasiswa
- Validasi otomatis format dan data
- Support untuk multiple records dalam satu file

### 2. 📋 Template CSV
- Download template CSV siap pakai
- Format yang sudah sesuai dengan kebutuhan sistem
- Contoh data untuk referensi

### 3. 👁️ Preview Data
- Lihat data sebelum diproses
- Statistik dasar dari data yang diupload
- Validasi visual untuk memastikan data benar

### 4. 🔍 Analisis Batch
- Analisis semua data sekaligus
- Statistik ringkasan distribusi kategori
- Visualisasi hasil analisis

### 5. 📊 Hasil Detail
- Tabel hasil analisis untuk semua data
- Analisis individual untuk setiap record
- Rekomendasi personal untuk setiap kategori

### 6. 💾 Export Hasil
- Export hasil ringkasan ke CSV
- Export hasil detail lengkap ke CSV
- Dokumentasi hasil untuk keperluan laporan

## 📝 Format File CSV

### Kolom yang Diperlukan:
```csv
uang_saku,pengeluaran_makanan,pengeluaran_transport,pengeluaran_hiburan,semester
1000000,400000,150000,100000,3
1500000,500000,200000,150000,5
800000,300000,100000,80000,2
```

### Deskripsi Kolom:
- **uang_saku**: Uang saku bulanan dalam Rupiah (angka tanpa titik/koma)
- **pengeluaran_makanan**: Pengeluaran untuk makanan dalam Rupiah
- **pengeluaran_transport**: Pengeluaran untuk transportasi dalam Rupiah
- **pengeluaran_hiburan**: Pengeluaran untuk hiburan dalam Rupiah
- **semester**: Semester mahasiswa (1-8)

## 🚀 Cara Penggunaan

### Step 1: Persiapan Data
1. Buka aplikasi Streamlit
2. Pilih "Upload CSV" di sidebar
3. Download template CSV (opsional)
4. Siapkan data dalam format CSV yang benar

### Step 2: Upload & Preview
1. Upload file CSV menggunakan file uploader
2. Aktifkan "Preview Data" untuk melihat data
3. Periksa apakah data sudah sesuai format

### Step 3: Analisis
1. Klik tombol "Analisis Data CSV"
2. Tunggu proses validasi dan analisis
3. Lihat hasil statistik ringkasan

### Step 4: Eksplorasi Hasil
1. Lihat distribusi kategori pengeluaran
2. Periksa tabel detail hasil analisis
3. Pilih data individual untuk analisis mendalam
4. Baca rekomendasi untuk setiap kategori

### Step 5: Export (Opsional)
1. Export hasil ringkasan ke CSV
2. Export hasil detail lengkap ke CSV
3. Simpan untuk dokumentasi atau laporan

## ✅ Validasi Data

### Validasi Otomatis:
- ✅ Pengecekan kolom yang diperlukan
- ✅ Validasi tipe data (numerik untuk nilai rupiah)
- ✅ Validasi range semester (1-8)
- ✅ Pengecekan nilai negatif
- ✅ Deteksi data kosong/missing
- ✅ Warning untuk pengeluaran tidak realistis

### Error Handling:
- ❌ File kosong atau tidak valid
- ❌ Format CSV yang salah
- ❌ Encoding file tidak didukung
- ❌ Kolom yang hilang
- ❌ Data tidak valid

## 💡 Tips & Best Practices

### 📋 Persiapan Data:
1. **Gunakan template** yang disediakan untuk menghindari error format
2. **Periksa data** sebelum upload untuk memastikan tidak ada nilai kosong
3. **Gunakan angka bulat** untuk nilai rupiah (tanpa titik atau koma)
4. **Simpan dalam UTF-8** encoding untuk menghindari masalah karakter

### 🔍 Analisis:
1. **Preview data** terlebih dahulu sebelum analisis
2. **Perhatikan warning** validasi yang muncul
3. **Analisis individual** untuk insight yang lebih mendalam
4. **Export hasil** untuk dokumentasi

### 📊 Interpretasi Hasil:
1. **Lihat distribusi kategori** untuk gambaran umum
2. **Bandingkan dengan rata-rata** untuk konteks
3. **Baca rekomendasi** untuk setiap kategori
4. **Gunakan visualisasi** untuk memahami pola

## 🔧 Troubleshooting

### Masalah Umum:

**1. Error "Kolom yang hilang"**
- Pastikan semua kolom required ada dalam CSV
- Gunakan template yang disediakan
- Periksa nama kolom (case-sensitive)

**2. Error "Format file CSV tidak valid"**
- Pastikan menggunakan koma (,) sebagai delimiter
- Simpan file dalam format CSV, bukan Excel
- Periksa encoding file (gunakan UTF-8)

**3. Data tidak muncul setelah upload**
- Periksa apakah file berisi data
- Pastikan tidak ada baris kosong di awal file
- Validasi format data sesuai requirement

**4. Warning "pengeluaran tidak realistis"**
- Periksa apakah nilai pengeluaran masuk akal
- Pastikan tidak ada kesalahan input (misal: 10000000 vs 1000000)
- Data tetap akan diproses meski ada warning

## 📈 Contoh Use Case

### 1. Analisis Kelas/Angkatan
- Upload data pengeluaran seluruh mahasiswa dalam satu kelas
- Lihat distribusi kategori pengeluaran
- Identifikasi mahasiswa yang perlu bantuan pengelolaan keuangan

### 2. Penelitian Pola Pengeluaran
- Kumpulkan data dari berbagai semester
- Analisis perbedaan pola pengeluaran berdasarkan semester
- Export hasil untuk analisis statistik lanjutan

### 3. Monitoring Berkala
- Upload data pengeluaran bulanan
- Bandingkan dengan periode sebelumnya
- Track progress pengelolaan keuangan mahasiswa

## 🎯 Manfaat Fitur

### Untuk Mahasiswa:
- ✅ Analisis batch untuk data teman-teman
- ✅ Perbandingan dengan peer group
- ✅ Insight pola pengeluaran kelompok

### Untuk Dosen/Peneliti:
- ✅ Analisis data penelitian dengan mudah
- ✅ Visualisasi hasil untuk presentasi
- ✅ Export data untuk analisis lanjutan

### Untuk Institusi:
- ✅ Monitoring kesejahteraan mahasiswa
- ✅ Data untuk kebijakan bantuan keuangan
- ✅ Insight untuk program literasi keuangan

---

**💡 Tip**: Mulai dengan template CSV yang disediakan dan gunakan fitur preview untuk memastikan data Anda sudah benar sebelum analisis!