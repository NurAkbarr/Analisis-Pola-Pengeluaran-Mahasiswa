import sys
import pandas as pd
import numpy as np

# Pastikan output terminal menggunakan UTF-8 (agar emoji tidak error di Windows)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    # Untuk Python < 3.7, gunakan cara lain atau abaikan
    pass

class SpendingRecommendationSystem:
    def __init__(self):
        self.tips_database = {
            'Hemat': {
                'title': '🎉 Hebat! Anda termasuk kategori HEMAT',
                'description': 'Pengelolaan keuangan Anda sudah sangat baik!',
                'tips': [
                    '💰 Pertahankan kebiasaan menabung yang sudah baik',
                    '📊 Mulai investasi kecil-kecilan untuk masa depan',
                    '📚 Alokasikan sedikit budget untuk pengembangan diri',
                    '🎯 Tetapkan target tabungan yang lebih ambisius',
                    '💡 Bagikan tips hemat Anda ke teman-teman'
                ],
                'warnings': [
                    '⚠️ Jangan terlalu pelit pada kebutuhan penting seperti makanan bergizi',
                    '⚠️ Sesekali berikan reward untuk diri sendiri'
                ]
            },
            'Sedang': {
                'title': '👍 Anda termasuk kategori SEDANG',
                'description': 'Pengelolaan keuangan Anda cukup baik, tapi masih bisa ditingkatkan.',
                'tips': [
                    '📝 Buat catatan pengeluaran harian untuk tracking yang lebih baik',
                    '🍽️ Kurangi jajan dan masak sendiri sesekali',
                    '🚌 Gunakan transportasi umum atau sepeda untuk menghemat',
                    '🎮 Batasi pengeluaran hiburan, pilih yang gratis/murah',
                    '💳 Gunakan aplikasi keuangan untuk budgeting',
                    '👥 Ajak teman untuk aktivitas hemat seperti piknik di taman'
                ],
                'warnings': [
                    '⚠️ Waspada pengeluaran impulsif, pikirkan dulu sebelum membeli',
                    '⚠️ Jangan terlalu sering nongkrong di tempat mahal'
                ]
            },
            'Boros': {
                'title': '🚨 Anda termasuk kategori BOROS',
                'description': 'Pengeluaran Anda melebihi batas wajar. Saatnya berbenah!',
                'tips': [
                    '🛑 STOP membeli barang yang tidak perlu',
                    '📱 Hapus aplikasi belanja online dari ponsel',
                    '🍜 Kurangi makan di luar, bawa bekal dari rumah',
                    '🚶 Jalan kaki atau naik angkot daripada ojek online',
                    '🎯 Tetapkan budget harian dan patuhi dengan disiplin',
                    '💰 Sisihkan uang di rekening yang sulit diakses',
                    '👨‍👩‍👧‍👦 Minta bantuan keluarga untuk mengontrol pengeluaran',
                    '📊 Gunakan metode envelope budgeting'
                ],
                'warnings': [
                    '🔥 URGENT: Kurangi pengeluaran hiburan minimal 50%',
                    '🔥 URGENT: Hindari hutang atau pinjaman tambahan',
                    '🔥 URGENT: Evaluasi gaya hidup dan prioritas'
                ]
            }
        }
        
        self.budget_suggestions = {
            'Hemat': {
                'makanan': '35-40%',
                'transport': '15-20%', 
                'hiburan': '5-10%',
                'tabungan': '15-25%'
            },
            'Sedang': {
                'makanan': '40-45%',
                'transport': '20-25%',
                'hiburan': '10-15%', 
                'tabungan': '10-15%'
            },
            'Boros': {
                'makanan': '45-50%',
                'transport': '25-30%',
                'hiburan': '5-10%',
                'tabungan': '5-10%'
            }
        }
    
    def get_recommendations(self, kategori, uang_saku, pengeluaran_data):
        """Generate personalized recommendations"""
        
        recommendations = self.tips_database[kategori].copy()
        budget_guide = self.budget_suggestions[kategori]
        
        # Hitung rasio pengeluaran
        total_pengeluaran = sum(pengeluaran_data.values())
        rasio_pengeluaran = total_pengeluaran / uang_saku
        
        # Analisis detail pengeluaran
        makanan_ratio = pengeluaran_data['makanan'] / uang_saku
        transport_ratio = pengeluaran_data['transport'] / uang_saku  
        hiburan_ratio = pengeluaran_data['hiburan'] / uang_saku
        
        # Personalized tips berdasarkan pola pengeluaran
        personalized_tips = []
        
        if makanan_ratio > 0.5:
            personalized_tips.append('🍽️ Pengeluaran makanan terlalu tinggi! Coba masak sendiri atau beli makanan yang lebih ekonomis')
        
        if transport_ratio > 0.3:
            personalized_tips.append('🚌 Pengeluaran transport berlebihan. Pertimbangkan naik angkot atau jalan kaki untuk jarak dekat')
            
        if hiburan_ratio > 0.2:
            personalized_tips.append('🎮 Pengeluaran hiburan terlalu tinggi. Cari alternatif hiburan gratis seperti olahraga atau baca buku')
        
        # Tambahkan tips personal
        if personalized_tips:
            recommendations['personalized_tips'] = personalized_tips
        
        # Tambahkan budget guide
        recommendations['budget_guide'] = budget_guide
        
        # Tambahkan perhitungan
        sisa_uang = uang_saku - total_pengeluaran
        recommendations['financial_summary'] = {
            'total_pengeluaran': total_pengeluaran,
            'rasio_pengeluaran': f"{rasio_pengeluaran:.1%}",
            'sisa_uang': sisa_uang,
            'status_sisa': 'Surplus' if sisa_uang > 0 else 'Defisit'
        }
        
        return recommendations
    
    def get_monthly_planning(self, kategori, uang_saku):
        """Generate monthly budget planning"""
        
        budget_guide = self.budget_suggestions[kategori]
        
        planning = {}
        for category, percentage in budget_guide.items():
            # Parse percentage range
            if '-' in percentage:
                min_pct, max_pct = percentage.replace('%', '').split('-')
                avg_pct = (float(min_pct) + float(max_pct)) / 2 / 100
            else:
                avg_pct = float(percentage.replace('%', '')) / 100
                
            planning[category] = {
                'percentage': percentage,
                'amount': int(uang_saku * avg_pct)
            }
        
        return planning

# Test the recommendation system
if __name__ == "__main__":
    rec_system = SpendingRecommendationSystem()
    
    # Test data
    test_data = {
        'uang_saku': 1000000,
        'pengeluaran': {
            'makanan': 600000,
            'transport': 200000,
            'hiburan': 300000
        }
    }
    
    # Simulasi prediksi kategori
    total = sum(test_data['pengeluaran'].values())
    rasio = total / test_data['uang_saku']
    
    if rasio <= 0.7:
        kategori = 'Hemat'
    elif rasio <= 0.9:
        kategori = 'Sedang'
    else:
        kategori = 'Boros'
    
    recommendations = rec_system.get_recommendations(
        kategori, 
        test_data['uang_saku'], 
        test_data['pengeluaran']
    )
    
    print("=== TEST RECOMMENDATION SYSTEM ===")
    print(f"Kategori: {kategori}")
    # Hilangkan emoji jika masih error, atau gunakan try-except
    try:
        print(f"Rekomendasi: {recommendations['title']}")
    except UnicodeEncodeError:
        print(f"Rekomendasi: {recommendations['title'].encode('ascii', 'ignore').decode()}")
    print("Tips:")
    for tip in recommendations['tips']:
        try:
            print(f"  {tip}")
        except UnicodeEncodeError:
            print(f"  {tip.encode('ascii', 'ignore').decode()}")
    
    if 'personalized_tips' in recommendations:
        print("\nTips Personal:")
        for tip in recommendations['personalized_tips']:
            try:
                print(f"  {tip}")
            except UnicodeEncodeError:
                print(f"  {tip.encode('ascii', 'ignore').decode()}")
    
    print(f"\nRingkasan Keuangan:")
    summary = recommendations['financial_summary']
    print(f"  Total Pengeluaran: Rp {summary['total_pengeluaran']:,}")
    print(f"  Rasio Pengeluaran: {summary['rasio_pengeluaran']}")
    print(f"  Sisa Uang: Rp {summary['sisa_uang']:,} ({summary['status_sisa']})")
    
    monthly_plan = rec_system.get_monthly_planning(kategori, test_data['uang_saku'])
    print(f"\nRencana Budget Bulanan:")
    for category, details in monthly_plan.items():
        print(f"  {category.title()}: {details['percentage']} = Rp {details['amount']:,}")
    
    print("\nRecommendation system siap digunakan!")