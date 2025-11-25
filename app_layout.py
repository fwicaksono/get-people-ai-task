import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def manage_list_input(label, key_prefix):
    """Helper function untuk membuat input list Add/Remove"""
    if f'{key_prefix}_list' not in st.session_state:
        st.session_state[f'{key_prefix}_list'] = []

    # Input Field
    col1, col2 = st.columns([4, 1])
    new_item = col1.text_input(f"Add {label}", key=f"{key_prefix}_input")
    
    if col2.button("Add", key=f"{key_prefix}_add"):
        if new_item:
            st.session_state[f'{key_prefix}_list'].append(new_item)
            st.rerun() 

    # Display List with Delete Button
    if st.session_state[f'{key_prefix}_list']:
        st.caption(f"Current {label}:")
        for i, item in enumerate(st.session_state[f'{key_prefix}_list']):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"- {item}")
            if c2.button("🗑️", key=f"{key_prefix}_del_{i}"):
                st.session_state[f'{key_prefix}_list'].pop(i)
                st.rerun()

    return st.session_state[f'{key_prefix}_list']

def render_sidebar():
    with st.sidebar:
        st.header("1. Role Information")
        role_name = st.text_input("Role Name", "Data Analyst")
        job_level = st.selectbox("Job Level", ["Junior", "Middle", "Senior", "Lead"])
        role_purpose = st.text_area("Role Purpose", "Drive business insights.")
        
        st.divider()
        st.header("2. Job Details (Context)")
        st.info("Add more details to sharpen the AI Profile results.")
        
        with st.expander("Key Responsibilities"):
            resps = manage_list_input("Responsibility", "resp")
            
        with st.expander("Key Competencies (Hard/Soft)"):
            comps = manage_list_input("Competency", "comp")
            
        st.divider()
        
        st.header("3. Benchmark Strategy")
        st.info("Input High Performer IDs (Max 3). Leave blank for Auto-Benchmark.")
        
        bench_input = st.text_input("Employee IDs (Optional)", placeholder="Contoh: EMP100005, EMP100008")
        
        btn_run = st.button("🚀 Analyze & Match", type="primary")
        
    return role_name, job_level, role_purpose, resps, comps, bench_input, btn_run

def render_visualizations(df, best_candidate):
    
    st.markdown("### Talent Intelligence Dashboard")

    with st.expander("🎯 Active Benchmark Target (The '100%' Standard)", expanded=True):
        col_b1, col_b2, col_b3 = st.columns(3)
        
        # HANDLING NULL VALUES
        bench_iq = best_candidate['bench_iq'] if pd.notna(best_candidate['bench_iq']) else 0
        bench_pauli = best_candidate['bench_pauli'] if pd.notna(best_candidate['bench_pauli']) else 0
        bench_papi = best_candidate['bench_papi_n'] if pd.notna(best_candidate['bench_papi_n']) else 0
        
        col_b1.metric("Target IQ (Min)", f"{bench_iq}")
        col_b2.metric("Target Endurance (Pauli)", f"{bench_pauli}")
        col_b3.metric("Target Hard Work (PAPI N)", f"{bench_papi}/9.0")
        
        st.caption("*These values are dynamically calculated from your selected Benchmark IDs.*")


    with st.expander("📈 Match Rate Distribution", expanded=False):
        # 1. Hitung Histogram Manual agar bisa dikasih warna beda-beda
        counts, bin_edges = np.histogram(df['final_match_rate'], bins=15)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # 2. Buat DataFrame Sementara
        hist_df = pd.DataFrame({
            'Match Rate': bin_centers,
            'Count': counts
        })
        
        # 3. Plot menggunakan Bar Chart (bukan Histogram standar) agar support color scale
        fig_dist = px.bar(
            hist_df, 
            x='Match Rate', 
            y='Count', 
            color='Match Rate',  # Ini kuncinya: Warna berdasarkan skor (X-axis)
            title="Distribution of Candidate Match Rates",
            labels={'Match Rate': 'Match Rate (%)', 'Count': 'Number of Candidates'},
            color_continuous_scale='Viridis', # Pilihan warna: Viridis, Plasma, Inferno, Cividis, Tealgrn
        )
        
        # Tweak visual: Hilangkan gap berlebih, tambah garis kandidat
        fig_dist.update_layout(bargap=0.05, coloraxis_showscale=False) # Sembunyikan colorbar agar bersih
        fig_dist.add_vline(x=best_candidate['final_match_rate'], line_dash="dash", line_color="#FF4B4B", annotation_text="Top Pick")
        
        st.plotly_chart(fig_dist, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Profile Pattern Analysis**")
        categories = ['Cognitive', 'Motivation', 'Leadership', 'Adaptability', 'Reliability']
        values = [best_candidate['score_cognitive'], best_candidate['score_motivation'], best_candidate['score_leadership'], best_candidate['score_adaptability'], best_candidate['score_reliability']]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name=best_candidate['fullname'], line_color='#00CC96'))
        
        # UPDATE: Ganti warna garis target jadi hitam
        fig_radar.add_trace(go.Scatterpolar(r=[100]*5, theta=categories, name='Target Profile (100% Match)', line_color='black', line_dash='dot'))
        
        # UPDATE: Tambah tickfont color black untuk angka sumbu
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True, 
                    range=[0, 100],
                    tickfont=dict(color="black") # Angka Sumbu jadi Hitam
                )
            ), 
            showlegend=True, 
            margin=dict(t=20, b=20, l=65, r=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col2:
        st.markdown("**Score Breakdown (Progress)**")
        
        # --- UPDATE: VISUAL LOADING STYLE (PROGRESS BAR) ---
        categories = ['Cognitive', 'Motivation', 'Leadership', 'Adaptability', 'Reliability']
        values = [best_candidate['score_cognitive'], best_candidate['score_motivation'], best_candidate['score_leadership'], best_candidate['score_adaptability'], best_candidate['score_reliability']]
        
        fig_bar = go.Figure()

        # 1. Background Bar (The 'Track' - 100%) - Abu-abu terang sebagai background
        fig_bar.add_trace(go.Bar(
            y=categories,
            x=[100]*5,
            orientation='h',
            marker_color='#f0f2f6', # Light gray
            name='Target',
            hoverinfo='skip' # Tidak perlu hover di background
        ))

        # 2. Candidate Score Bar (The 'Fill') - Hijau sebagai progress
        fig_bar.add_trace(go.Bar(
            y=categories,
            x=values,
            orientation='h',
            marker_color='#00CC96', # Green brand color
            text=[f"<b>{v}%</b>" for v in values], # Tampilkan angka persen tebal
            textposition='auto',
            name='Score'
        ))

        fig_bar.update_layout(
            title=f"Detailed Score: {best_candidate['fullname']}",
            barmode='overlay', # PENTING: Overlay agar bar hijau menimpa bar abu-abu
            xaxis=dict(
                range=[0, 100], 
                showgrid=False, 
                visible=False # Sembunyikan axis bawah agar bersih seperti loading bar
            ),
            yaxis=dict(
                showgrid=False,
                # categoryorder='total ascending' # Opsional: Urutkan dari skor terkecil/terbesar
            ),
            margin=dict(t=40, b=10, l=100, r=40),
            height=300,
            showlegend=False # Sembunyikan legend karena sudah jelas
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
def render_results_table(df):
    """Menampilkan Semua Tabel Tanpa Pagination"""
    
    # Ambil 10 data teratas untuk ditampilkan
    top_df = df.head(10)

    # --- TABEL 1: RANKING (SCORING) ---
    st.markdown("###Ranked Talent List")
    
    score_cols = ["employee_id", "fullname", "final_match_rate", "top_tgv", "gap_tgv", "strengths_list"]
    st.dataframe(
        top_df[score_cols],
        column_config={
            "employee_id": "ID",
            "fullname": "Name",
            "final_match_rate": st.column_config.ProgressColumn("Match %", format="%.2f", min_value=0, max_value=100),
            "top_tgv": st.column_config.TextColumn("Strongest TGV", width="small"),
            "gap_tgv": st.column_config.TextColumn("Key Gap", width="small"),
            "strengths_list": st.column_config.TextColumn("Top Strengths (Traits)", width="medium"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.divider()

    # --- TABEL 2: INFO (DEMOGRAPHICS) ---
    st.markdown("###Employee Information")
    
    info_cols = ["fullname", "final_match_rate", "role", "division", "department", "job_level"]
    available_cols = [c for c in info_cols if c in top_df.columns]
    st.dataframe(top_df[available_cols], hide_index=True, use_container_width=True)

    st.divider()

    # --- TABEL 3: DETAILED PARAMETERS (FULL RAW DATA) ---
    st.markdown("### 🔬 Detailed Scoring Parameters")
    st.caption("Displaying data for the top 10 candidates.")
    
    st.dataframe(
        top_df,
        column_config={"final_match_rate": st.column_config.ProgressColumn("Match %", format="%.2f", min_value=0, max_value=100)},
        hide_index=True,
        use_container_width=True
    )
