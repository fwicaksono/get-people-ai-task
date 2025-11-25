import streamlit as st
import uuid
from app_layout import render_sidebar, render_visualizations, render_results_table
from prompt import generate_job_profile_gemini, generate_candidate_analysis
from query import get_ranked_talent

st.set_page_config(page_title="AI Talent Matcher", layout="wide", page_icon="🧬")
st.title("🧬 AI Talent Match Intelligence")
st.markdown("Automated Success Pattern Discovery & Matching")

def main():
    # Render Sidebar
    role, level, purpose, resps, comps, bench_ids, is_clicked = render_sidebar()

    if is_clicked:
        # 1. PARAMETERIZE JOB VACANCY (Simulasi Recording)
        # Sesuai requirement: "Record or parameterize a new job_vacancy_id"
        if 'vacancy_id' not in st.session_state:
            st.session_state['vacancy_id'] = str(uuid.uuid4())[:8]
        
        # Setiap kali Run diklik, kita anggap ini sesi analisis baru
        current_vacancy_id = st.session_state['vacancy_id']
        st.toast(f"🆔 Analysis Session ID: {current_vacancy_id} initialized.")

        # 2. VALIDASI BENCHMARK
        ids_list = [x.strip() for x in bench_ids.split(",") if x.strip()]
        if len(ids_list) > 3:
            st.error(f"Maximum Benchmark limit is 3 IDs! You entered {len(ids_list)} !!")
            st.stop()

        # 3. GENERATE AI CONTEXT
        with st.expander("📄 View AI-Generated Job Context", expanded=False):
             with st.spinner("Analyzing context & Requirements..."):
                ai_output = generate_job_profile_gemini(role, level, purpose, resps, comps)
                st.markdown(ai_output)

        st.divider()

        # 4. RECOMPUTE BASELINES & SQL (Dynamic)
        # Fungsi ini otomatis menghitung ulang baseline dari input `ids_list` 
        # dan menjalankan parameterized query tanpa edit code.
        with st.spinner("Recomputing Success Baselines & Ranking..."):
            df_results, is_fallback = get_ranked_talent(ids_list)

        if df_results.empty:
            st.warning("No data found.")
        else:
            if is_fallback:
                st.info(f"Auto-Benchmark: Using {len(ids_list) if not ids_list else 'All'} High Performers.")
            else:
                st.success(f"✅ Custom Benchmark: ID {', '.join(ids_list)}")
            
            best_candidate = df_results.iloc[0]

            # 5. REGENERATE VISUALS
            render_visualizations(df_results, best_candidate)
            
            # 6. AI CANDIDATE INSIGHT
            st.divider()
            st.markdown(f"### AI Insight: Why {best_candidate['fullname']} ranks #1?")
            with st.spinner("Generating insight..."):
                insight = generate_candidate_analysis(best_candidate)
                st.info(insight)
            
            st.divider()

            # 7. DISPLAY OUTPUT TABLES
            render_results_table(df_results)

if __name__ == "__main__":
    main()