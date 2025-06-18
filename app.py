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

# Main app
def main():
    st.markdown('<h1 class="main-header">💰 Analisis Pola Pengeluaran Mahasiswa</h1>', unsafe_allow_html=True)
    st.markdown("---")
    models = load_models()
    sample_data = load_sample_data()
    st.sidebar.header("📊 Input Data Pengeluaran")
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