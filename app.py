import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
from recommendations import SpendingRecommendationSystem
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Analisis Pola Pengeluaran Mahasiswa",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .recommendation-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.8rem;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .tip-item {
        background-color: #f8f9fa;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-item {
        background-color: #fff3cd;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None

# Load models
@st.cache_resource
def load_models():
    try:
        kmeans_model = joblib.load('kmeans_model.pkl')
        scaler = joblib.load('scaler.pkl')
        cluster_labels = joblib.load('cluster_labels.pkl')
        rec_system = SpendingRecommendationSystem()
        return kmeans_model, scaler, cluster_labels, rec_system
    except FileNotFoundError:
        st.error("Model files tidak ditemukan! Pastikan Anda sudah menjalankan script training terlebih dahulu.")
        st.stop()

# Load sample data for visualization
@st.cache_data
def load_sample_data():
    try:
        return pd.read_csv('student_spending_clustered.csv')
    except FileNotFoundError:
        st.error("Data tidak ditemukan! Pastikan Anda sudah menjalankan script generate_data.py")
        st.stop()

def create_spending_visualization(uang_saku, makanan, transport, hiburan, category):
    """Create spending breakdown visualization"""
    spending_data = {
        'Kategori': ['Makanan', 'Transport', 'Hiburan', 'Sisa'],
        'Jumlah': [makanan, transport, hiburan, max(0, uang_saku - makanan - transport - hiburan)],
        'Warna': ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
    }
    fig_pie = px.pie(
        values=spending_data['Jumlah'],
        names=spending_data['Kategori'],
        title="Breakdown Pengeluaran Anda",
        color_discrete_sequence=spending_data['Warna']
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_bar = go.Figure(data=[
        go.Bar(name='Pengeluaran Anda', x=['Makanan', 'Transport', 'Hiburan'],
               y=[makanan, transport, hiburan], marker_color='lightblue'),
    ])
    fig_bar.update_layout(
        title="Pengeluaran per Kategori",
        xaxis_title="Kategori",
        yaxis_title="Jumlah (Rp)",
        showlegend=True
    )
    return fig_pie, fig_bar

def create_comparison_chart(sample_data, user_category, user_spending):
    """Create comparison with other students"""
    category_avg = sample_data.groupby('kategori_pengeluaran')[
        ['pengeluaran_makanan', 'pengeluaran_transport', 'pengeluaran_hiburan']
    ].mean()
    fig = go.Figure()
    # Add user data
    fig.add_trace(go.Bar(
        name='Pengeluaran Anda',
        x=['Makanan', 'Transport', 'Hiburan'],
        y=[user_spending['makanan'], user_spending['transport'], user_spending['hiburan']],
        marker_color='red',
        opacity=0.8
    ))
    # Add category average
    if user_category in category_avg.index:
        avg_data = category_avg.loc[user_category]
        fig.add_trace(go.Bar(
            name=f'Rata-rata {user_category}',
            x=['Makanan', 'Transport', 'Hiburan'],
            y=[avg_data['pengeluaran_makanan'], avg_data['pengeluaran_transport'], avg_data['pengeluaran_hiburan']],
            marker_color='blue',
            opacity=0.6
        ))
    fig.update_layout(
        title=f"Perbandingan dengan Mahasiswa Kategori {user_category}",
        xaxis_title="Kategori Pengeluaran",
        yaxis_title="Jumlah (Rp)",
        barmode='group'
    )
    return fig

def predict_spending_category(uang_saku, makanan, transport, hiburan, semester, models):
    kmeans_model, scaler, cluster_labels, rec_system = models
    total_pengeluaran = makanan + transport + hiburan
    rasio_pengeluaran = total_pengeluaran / uang_saku if uang_saku > 0 else 0
    input_data = np.array([[uang_saku, makanan, transport, hiburan, rasio_pengeluaran, semester]])
    input_scaled = scaler.transform(input_data)
    cluster = kmeans_model.predict(input_scaled)[0]
    category = cluster_labels[cluster]
    return category, total_pengeluaran, rasio_pengeluaran

def process_uploaded_csv(uploaded_file, models):
    """Process uploaded CSV file and return analysis results"""
    try:
        df = pd.read_csv(uploaded_file)
        
        # Validate required columns
        required_columns = ['uang_saku', 'pengeluaran_makanan', 'pengeluaran_transport', 'pengeluaran_hiburan', 'semester']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ Kolom yang hilang: {', '.join(missing_columns)}")
            st.info("📋 Format CSV yang diperlukan: uang_saku, pengeluaran_makanan, pengeluaran_transport, pengeluaran_hiburan, semester")
            return None
        
        # Validate data types and ranges
        validation_errors = []
        
        # Check for empty dataframe
        if df.empty:
            st.error("❌ File CSV kosong!")
            return None
        
        # Check for missing values
        if df[required_columns].isnull().any().any():
            st.warning("⚠️ Ditemukan nilai kosong dalam data. Baris dengan nilai kosong akan diabaikan.")
            df = df.dropna(subset=required_columns)
        
        # Validate numeric columns
        numeric_columns = ['uang_saku', 'pengeluaran_makanan', 'pengeluaran_transport', 'pengeluaran_hiburan']
        for col in numeric_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    df = df.dropna(subset=[col])
                except:
                    validation_errors.append(f"Kolom {col} harus berisi angka")
        
        # Validate semester range
        if not df['semester'].between(1, 8).all():
            validation_errors.append("Semester harus antara 1-8")
            df = df[df['semester'].between(1, 8)]
        
        # Validate positive values
        for col in numeric_columns:
            if (df[col] < 0).any():
                validation_errors.append(f"Kolom {col} tidak boleh negatif")
                df = df[df[col] >= 0]
        
        # Validate logical spending (total spending shouldn't be too much higher than allowance)
        df['total_temp'] = df['pengeluaran_makanan'] + df['pengeluaran_transport'] + df['pengeluaran_hiburan']
        unrealistic_spending = df[df['total_temp'] > df['uang_saku'] * 1.5]
        if not unrealistic_spending.empty:
            st.warning(f"⚠️ Ditemukan {len(unrealistic_spending)} data dengan pengeluaran tidak realistis (>150% uang saku). Data ini akan tetap diproses.")
        
        df = df.drop('total_temp', axis=1)
        
        if validation_errors:
            for error in validation_errors:
                st.warning(f"⚠️ {error}")
        
        if df.empty:
            st.error("❌ Tidak ada data valid yang tersisa setelah validasi!")
            return None
        
        st.success(f"✅ Data valid: {len(df)} baris siap diproses")
        
        # Process each row
        results = []
        for idx, row in df.iterrows():
            category, total_pengeluaran, rasio_pengeluaran = predict_spending_category(
                row['uang_saku'], row['pengeluaran_makanan'], row['pengeluaran_transport'],
                row['pengeluaran_hiburan'], row['semester'], models
            )
            
            pengeluaran_data = {
                'makanan': row['pengeluaran_makanan'],
                'transport': row['pengeluaran_transport'],
                'hiburan': row['pengeluaran_hiburan']
            }
            
            recommendations = models[3].get_recommendations(category, row['uang_saku'], pengeluaran_data)
            
            results.append({
                'index': idx + 1,
                'uang_saku': row['uang_saku'],
                'total_pengeluaran': total_pengeluaran,
                'rasio_pengeluaran': rasio_pengeluaran,
                'category': category,
                'recommendations': recommendations,
                'spending_data': pengeluaran_data
            })
        
        return results
    
    except pd.errors.EmptyDataError:
        st.error("❌ File CSV kosong atau tidak valid!")
        return None
    except pd.errors.ParserError:
        st.error("❌ Format file CSV tidak valid! Pastikan file menggunakan delimiter koma (,)")
        return None
    except UnicodeDecodeError:
        st.error("❌ Encoding file tidak didukung! Pastikan file disimpan dalam format UTF-8")
        return None
    except Exception as e:
        st.error(f"❌ Error memproses file: {str(e)}")
        st.info("💡 Pastikan file CSV Anda sesuai format yang diperlukan")
        return None

def display_csv_results(results):
    """Display results from CSV analysis"""
    st.markdown("## 📊 Hasil Analisis Data CSV")
    
    # Summary statistics
    categories = [r['category'] for r in results]
    category_counts = pd.Series(categories).value_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📁 Total Data", len(results))
    with col2:
        st.metric("💚 Hemat", category_counts.get('Hemat', 0))
    with col3:
        st.metric("💛 Sedang", category_counts.get('Sedang', 0))
    with col4:
        st.metric("❤️ Boros", category_counts.get('Boros', 0))
    
    # Category distribution chart
    fig_dist = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title="Distribusi Kategori dari Data CSV",
        color_discrete_map={'Hemat': '#28a745', 'Sedang': '#ffc107', 'Boros': '#dc3545'}
    )
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Detailed results table
    st.markdown("### 📋 Detail Hasil Analisis")
    
    # Create summary dataframe
    summary_data = []
    for result in results:
        summary_data.append({
            'No': result['index'],
            'Uang Saku': f"Rp {result['uang_saku']:,.0f}",
            'Total Pengeluaran': f"Rp {result['total_pengeluaran']:,.0f}",
            'Rasio': f"{result['rasio_pengeluaran']:.1%}",
            'Kategori': result['category'],
            'Sisa Uang': f"Rp {result['uang_saku'] - result['total_pengeluaran']:,.0f}"
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)
    
    # Export results
    col1, col2 = st.columns(2)
    with col1:
        # Export to CSV
        csv_export = summary_df.to_csv(index=False)
        st.download_button(
            label="📥 Export ke CSV",
            data=csv_export,
            file_name="hasil_analisis_pengeluaran.csv",
            mime="text/csv",
            help="Download hasil analisis dalam format CSV"
        )
    
    with col2:
        # Export detailed results to CSV
        detailed_data = []
        for result in results:
            detailed_data.append({
                'No': result['index'],
                'Uang_Saku': result['uang_saku'],
                'Pengeluaran_Makanan': result['spending_data']['makanan'],
                'Pengeluaran_Transport': result['spending_data']['transport'],
                'Pengeluaran_Hiburan': result['spending_data']['hiburan'],
                'Total_Pengeluaran': result['total_pengeluaran'],
                'Rasio_Pengeluaran': result['rasio_pengeluaran'],
                'Kategori': result['category'],
                'Sisa_Uang': result['uang_saku'] - result['total_pengeluaran'],
                'Rekomendasi_Utama': result['recommendations']['title']
            })
        
        detailed_df = pd.DataFrame(detailed_data)
        detailed_csv = detailed_df.to_csv(index=False)
        st.download_button(
            label="📥 Export Detail ke CSV",
            data=detailed_csv,
            file_name="detail_analisis_pengeluaran.csv",
            mime="text/csv",
            help="Download hasil analisis detail dalam format CSV"
        )
    
    # Individual analysis option
    st.markdown("### 🔍 Analisis Individual")
    selected_index = st.selectbox(
        "Pilih data untuk analisis detail:",
        options=range(len(results)),
        format_func=lambda x: f"Data #{x+1} - {results[x]['category']}"
    )
    
    if selected_index is not None:
        result = results[selected_index]
        
        # Display individual metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💳 Uang Saku", f"Rp {result['uang_saku']:,.0f}")
        with col2:
            st.metric("💸 Total Pengeluaran", f"Rp {result['total_pengeluaran']:,.0f}")
        with col3:
            st.metric("📊 Rasio Pengeluaran", f"{result['rasio_pengeluaran']:.1%}")
        with col4:
            sisa = result['uang_saku'] - result['total_pengeluaran']
            st.metric("💰 Sisa Uang", f"Rp {sisa:,.0f}")
        
        # Category display
        category_colors = {'Hemat': '#28a745', 'Sedang': '#ffc107', 'Boros': '#dc3545'}
        category_color = category_colors.get(result['category'], '#6c757d')
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, {category_color}20, {category_color}10);
                    border-radius: 1rem; border: 2px solid {category_color}; margin: 1rem 0;">
            <h3 style="color: {category_color}; margin: 0;">{result['recommendations']['title']}</h3>
            <p style="font-size: 1.1rem; margin: 0.5rem 0; color: #555;">
                {result['recommendations']['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Visualization for selected data
        fig_pie, fig_bar = create_spending_visualization(
            result['uang_saku'],
            result['spending_data']['makanan'],
            result['spending_data']['transport'],
            result['spending_data']['hiburan'],
            result['category']
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Recommendations
        st.markdown("#### 💡 Rekomendasi")
        for tip in result['recommendations']['tips']:
            st.markdown(f"""
            <div class="tip-item">
                {tip}
            </div>
            """, unsafe_allow_html=True)

# Main app
def main():
    st.markdown('<h1 class="main-header">💰 Analisis Pola Pengeluaran Mahasiswa</h1>', unsafe_allow_html=True)
    st.markdown("---")
    models = load_models()
    sample_data = load_sample_data()
    
    # Sidebar with input options
    st.sidebar.header("📊 Input Data Pengeluaran")
    
    # Add option to choose input method
    input_method = st.sidebar.radio(
        "Pilih metode input:",
        ["📝 Input Manual", "📁 Upload CSV"],
        help="Pilih cara memasukkan data pengeluaran"
    )
    
    if input_method == "📁 Upload CSV":
        st.sidebar.markdown("### 📁 Upload File CSV")
        st.sidebar.markdown("""
        **Format CSV yang diperlukan:**
        - `uang_saku`: Uang saku bulanan (Rp)
        - `pengeluaran_makanan`: Pengeluaran makanan (Rp)
        - `pengeluaran_transport`: Pengeluaran transport (Rp)
        - `pengeluaran_hiburan`: Pengeluaran hiburan (Rp)
        - `semester`: Semester (1-8)
        """)
        
        # Download template button
        template_data = {
            'uang_saku': [1000000, 1500000, 800000],
            'pengeluaran_makanan': [400000, 500000, 300000],
            'pengeluaran_transport': [150000, 200000, 100000],
            'pengeluaran_hiburan': [100000, 150000, 80000],
            'semester': [3, 5, 2]
        }
        template_df = pd.DataFrame(template_data)
        csv_template = template_df.to_csv(index=False)
        
        st.sidebar.download_button(
            label="📥 Download Template CSV",
            data=csv_template,
            file_name="template_pengeluaran.csv",
            mime="text/csv",
            help="Download template CSV untuk diisi dengan data Anda"
        )
        
        uploaded_file = st.sidebar.file_uploader(
            "Pilih file CSV",
            type=['csv'],
            help="Upload file CSV dengan data pengeluaran mahasiswa"
        )
        
        if uploaded_file is not None:
            st.sidebar.success(f"✅ File '{uploaded_file.name}' berhasil diupload!")
            
            # Preview data option
            if st.sidebar.checkbox("👁️ Preview Data"):
                try:
                    preview_df = pd.read_csv(uploaded_file)
                    st.markdown("### 👁️ Preview Data CSV")
                    st.markdown(f"**Jumlah baris**: {len(preview_df)}")
                    st.markdown(f"**Jumlah kolom**: {len(preview_df.columns)}")
                    st.markdown(f"**Kolom**: {', '.join(preview_df.columns.tolist())}")
                    
                    # Show first few rows
                    st.dataframe(preview_df.head(10), use_container_width=True)
                    
                    # Show basic statistics
                    if len(preview_df) > 0:
                        numeric_cols = preview_df.select_dtypes(include=[np.number]).columns
                        if len(numeric_cols) > 0:
                            st.markdown("#### 📊 Statistik Dasar")
                            st.dataframe(preview_df[numeric_cols].describe(), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ Error membaca file: {str(e)}")
            
            if st.sidebar.button("🔍 Analisis Data CSV", type="primary"):
                with st.spinner("Memproses data CSV..."):
                    results = process_uploaded_csv(uploaded_file, models)
                    if results:
                        st.session_state.csv_results = results
        
        # Display CSV results if available
        if 'csv_results' in st.session_state:
            display_csv_results(st.session_state.csv_results)
        else:
            st.markdown("""
            ## 📁 Upload Data CSV
            
            Anda dapat mengupload file CSV yang berisi data pengeluaran mahasiswa untuk dianalisis secara batch.
            
            ### 📋 Format File CSV:
            File CSV harus memiliki kolom berikut:
            - **uang_saku**: Uang saku bulanan dalam Rupiah
            - **pengeluaran_makanan**: Pengeluaran untuk makanan dalam Rupiah
            - **pengeluaran_transport**: Pengeluaran untuk transportasi dalam Rupiah
            - **pengeluaran_hiburan**: Pengeluaran untuk hiburan dalam Rupiah
            - **semester**: Semester mahasiswa (1-8)
            
            ### 📝 Contoh Format:
            ```
            uang_saku,pengeluaran_makanan,pengeluaran_transport,pengeluaran_hiburan,semester
            1000000,400000,150000,100000,3
            1500000,500000,200000,150000,5
            800000,300000,100000,80000,2
            ```
            
            💡 **Tips**:
            - Gunakan tombol "Download Template CSV" di sidebar untuk template siap pakai
            - Aktifkan "Preview Data" untuk melihat data sebelum dianalisis
            - File akan divalidasi otomatis dan error akan ditampilkan jika ada masalah
            
            ### 🎯 Fitur Analisis CSV:
            - **Analisis batch** untuk multiple data sekaligus
            - **Statistik ringkasan** distribusi kategori
            - **Visualisasi** hasil analisis
            - **Detail individual** untuk setiap data
            - **Rekomendasi** untuk setiap kategori pengeluaran
            - **Export hasil** ke CSV untuk dokumentasi
            - **Template download** untuk memudahkan input data
            - **Preview data** sebelum diproses
            - **Validasi otomatis** untuk memastikan kualitas data
            
            ### 📝 Tips Penggunaan CSV:
            1. **Gunakan template** yang disediakan untuk format yang benar
            2. **Pastikan tidak ada sel kosong** di kolom yang diperlukan
            3. **Gunakan angka tanpa titik atau koma** untuk nilai rupiah (contoh: 1000000 bukan 1.000.000)
            4. **Semester harus angka 1-8** sesuai sistem pendidikan
            5. **Simpan file dalam format CSV** dengan encoding UTF-8
            6. **Gunakan preview** untuk memeriksa data sebelum analisis
            
            ### ⚠️ Troubleshooting:
            - **Error encoding**: Simpan ulang file CSV dengan encoding UTF-8
            - **Error format**: Pastikan menggunakan koma (,) sebagai delimiter
            - **Data tidak valid**: Periksa apakah semua kolom berisi data yang benar
            - **File terlalu besar**: Batasi maksimal 1000 baris untuk performa optimal
            """)
    
    else:  # Manual input
        st.sidebar.markdown("Masukkan data pengeluaran bulanan Anda:")
    uang_saku = st.sidebar.number_input(
        "💳 Uang Saku (Rp/bulan)",
        min_value=100000,
        max_value=5000000,
        value=1000000,
        step=50000,
        help="Total uang saku yang Anda terima per bulan"
    )
    pengeluaran_makanan = st.sidebar.number_input(
        "🍽️ Pengeluaran Makanan (Rp/bulan)",
        min_value=0,
        max_value=int(uang_saku),
        value=min(400000, int(uang_saku * 0.4)),
        step=25000,
        help="Pengeluaran untuk makanan, jajanan, dan minuman"
    )
    pengeluaran_transport = st.sidebar.number_input(
        "🚌 Pengeluaran Transport (Rp/bulan)",
        min_value=0,
        max_value=int(uang_saku),
        value=min(150000, int(uang_saku * 0.15)),
        step=25000,
        help="Pengeluaran untuk transportasi ke kampus dan aktivitas lain"
    )
    pengeluaran_hiburan = st.sidebar.number_input(
        "🎮 Pengeluaran Hiburan (Rp/bulan)",
        min_value=0,
        max_value=int(uang_saku),
        value=min(100000, int(uang_saku * 0.1)),
        step=25000,
        help="Pengeluaran untuk hiburan, nongkrong, dan kesenangan"
    )
    semester = st.sidebar.selectbox(
        "📚 Semester",
        options=list(range(1, 9)),
        index=2,
        help="Semester saat ini"
    )
    if st.sidebar.button("🔍 Analisis Pengeluaran", type="primary"):
        total_input = pengeluaran_makanan + pengeluaran_transport + pengeluaran_hiburan
        if total_input > uang_saku * 1.2:
            st.sidebar.error("⚠️ Total pengeluaran terlalu tinggi dibanding uang saku!")
        else:
            category, total_pengeluaran, rasio_pengeluaran = predict_spending_category(
                uang_saku, pengeluaran_makanan, pengeluaran_transport,
                pengeluaran_hiburan, semester, models
            )
            pengeluaran_data = {
                'makanan': pengeluaran_makanan,
                'transport': pengeluaran_transport,
                'hiburan': pengeluaran_hiburan
            }
            recommendations = models[3].get_recommendations(category, uang_saku, pengeluaran_data)
            st.session_state.recommendations = {
                'category': category,
                'recommendations': recommendations,
                'spending_data': pengeluaran_data,
                'uang_saku': uang_saku,
                'total_pengeluaran': total_pengeluaran,
                'rasio_pengeluaran': rasio_pengeluaran
            }
    if st.session_state.recommendations:
        result = st.session_state.recommendations
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "💳 Uang Saku",
                f"Rp {result['uang_saku']:,.0f}",
                help="Total uang saku bulanan"
            )
        with col2:
            st.metric(
                "💸 Total Pengeluaran",
                f"Rp {result['total_pengeluaran']:,.0f}",
                help="Total pengeluaran bulanan"
            )
        with col3:
            st.metric(
                "📊 Rasio Pengeluaran",
                f"{result['rasio_pengeluaran']:.1%}",
                help="Persentase pengeluaran dari uang saku"
            )
        with col4:
            sisa = result['uang_saku'] - result['total_pengeluaran']
            st.metric(
                "💰 Sisa Uang",
                f"Rp {sisa:,.0f}",
                delta=f"{'Surplus' if sisa >= 0 else 'Defisit'}",
                help="Sisa uang setelah pengeluaran"
            )
        st.markdown("---")
        category_colors = {
            'Hemat': '#28a745',
            'Sedang': '#ffc107',
            'Boros': '#dc3545'
        }
        category_color = category_colors.get(result['category'], '#6c757d')
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, {category_color}20, {category_color}10);
                    border-radius: 1rem; border: 2px solid {category_color};">
            <h2 style="color: {category_color}; margin: 0;">{result['recommendations']['title']}</h2>
            <p style="font-size: 1.2rem; margin: 0.5rem 0; color: #555;">
                {result['recommendations']['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("## 📈 Visualisasi Pengeluaran")
        col1, col2 = st.columns(2)
        with col1:
            fig_pie, fig_bar = create_spending_visualization(
                result['uang_saku'],
                result['spending_data']['makanan'],
                result['spending_data']['transport'],
                result['spending_data']['hiburan'],
                result['category']
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.plotly_chart(fig_bar, use_container_width=True)
        fig_comparison = create_comparison_chart(
            sample_data,
            result['category'],
            result['spending_data']
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
        st.markdown("## 💡 Rekomendasi & Tips")
        st.markdown("### 📝 Tips Pengelolaan Keuangan")
        for tip in result['recommendations']['tips']:
            st.markdown(f"""
            <div class="tip-item">
                {tip}
            </div>
            """, unsafe_allow_html=True)
        if 'personalized_tips' in result['recommendations']:
            st.markdown("### 🎯 Tips Personal untuk Anda")
            for tip in result['recommendations']['personalized_tips']:
                st.markdown(f"""
                <div class="tip-item">
                    {tip}
                </div>
                """, unsafe_allow_html=True)
        if 'warnings' in result['recommendations']:
            st.markdown("### ⚠️ Peringatan")
            for warning in result['recommendations']['warnings']:
                st.markdown(f"""
                <div class="warning-item">
                    {warning}
                </div>
                """, unsafe_allow_html=True)
        st.markdown("### 📊 Rencana Budget Ideal")
        monthly_plan = models[3].get_monthly_planning(result['category'], result['uang_saku'])
        plan_col1, plan_col2 = st.columns(2)
        with plan_col1:
            st.markdown("**Alokasi Budget yang Disarankan:**")
            for category, details in monthly_plan.items():
                st.write(f"• **{category.title()}**: {details['percentage']} = Rp {details['amount']:,}")
        with plan_col2:
            current_spending = [
                result['spending_data']['makanan'],
                result['spending_data']['transport'],
                result['spending_data']['hiburan'],
                max(0, result['uang_saku'] - result['total_pengeluaran'])
            ]
            recommended_spending = [
                monthly_plan['makanan']['amount'] if 'makanan' in monthly_plan else 0,
                monthly_plan['transport']['amount'] if 'transport' in monthly_plan else 0,
                monthly_plan['hiburan']['amount'] if 'hiburan' in monthly_plan else 0,
                monthly_plan['tabungan']['amount'] if 'tabungan' in monthly_plan else 0
            ]
            fig_budget = go.Figure(data=[
                go.Bar(name='Pengeluaran Saat Ini', x=['Makanan', 'Transport', 'Hiburan', 'Tabungan'],
                       y=current_spending, marker_color='lightcoral'),
                go.Bar(name='Rekomendasi', x=['Makanan', 'Transport', 'Hiburan', 'Tabungan'],
                       y=recommended_spending, marker_color='lightgreen')
            ])
            fig_budget.update_layout(
                title="Perbandingan Budget",
                xaxis_title="Kategori",
                yaxis_title="Jumlah (Rp)",
                barmode='group'
            )
            st.plotly_chart(fig_budget, use_container_width=True)
    else:
        st.markdown("""
        ## 👋 Selamat Datang!
        Aplikasi ini akan membantu Anda menganalisis pola pengeluaran dan memberikan rekomendasi pengelolaan keuangan yang lebih baik.
        ### 📝 Cara Menggunakan:
        1. **Input data pengeluaran** Anda di sidebar kiri
        2. **Klik tombol "Analisis Pengeluaran"** untuk mendapatkan hasil
        3. **Lihat kategori** pengeluaran Anda (Hemat/Sedang/Boros)
        4. **Baca rekomendasi** yang diberikan untuk meningkatkan pengelolaan keuangan
        ### 📊 Yang Akan Anda Dapatkan:
        - **Kategori pengeluaran** berdasarkan pola spending Anda
        - **Visualisasi** breakdown pengeluaran
        - **Tips personal** sesuai kondisi keuangan Anda
        - **Rencana budget** yang ideal untuk kategori Anda
        - **Perbandingan** dengan mahasiswa lain dalam kategori yang sama
        """)
        st.markdown("## 📈 Statistik Data Mahasiswa")
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_uang_saku = sample_data['uang_saku'].mean()
            st.metric("💳 Rata-rata Uang Saku", f"Rp {avg_uang_saku:,.0f}")
        with col2:
            avg_pengeluaran = sample_data['total_pengeluaran'].mean()
            st.metric("💸 Rata-rata Pengeluaran", f"Rp {avg_pengeluaran:,.0f}")
        with col3:
            avg_rasio = sample_data['rasio_pengeluaran'].mean()
            st.metric("📊 Rata-rata Rasio", f"{avg_rasio:.1%}")
        st.markdown("### 📊 Distribusi Kategori Mahasiswa")
        category_dist = sample_data['kategori_pengeluaran'].value_counts()
        fig_dist = px.pie(
            values=category_dist.values,
            names=category_dist.index,
            title="Distribusi Kategori Pengeluaran",
            color_discrete_map={'Hemat': '#28a745', 'Sedang': '#ffc107', 'Boros': '#dc3545'}
        )
        st.plotly_chart(fig_dist, use_container_width=True)

if __name__ == "__main__":
    main()