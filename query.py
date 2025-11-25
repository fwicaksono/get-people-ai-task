import pandas as pd
import streamlit as st
from sqlalchemy import text
from config import get_db_engine

# --- SQL CTE LOGIC (FIXED: EXCLUDE BENCHMARK FROM RESULTS) ---
MATCHING_QUERY = """
WITH 
-- 1. FILTER BENCHMARK (Untuk menghitung Baseline)
selected_benchmarks AS (
    SELECT DISTINCT employee_id 
    FROM performance_yearly 
    WHERE employee_id = ANY(:benchmark_ids) 
),
-- 2. HITUNG BASELINE STATS
benchmark_stats AS (
    SELECT 
        AVG(pp.iq) as base_iq,
        AVG(pp.pauli) as base_pauli,
        AVG(CASE WHEN ps.scale_code = 'Papi_N' THEN ps.score END) as base_papi_n,
        AVG(CASE WHEN ps.scale_code = 'Papi_A' THEN ps.score END) as base_papi_a,
        AVG(CASE WHEN ps.scale_code = 'Papi_L' THEN ps.score END) as base_papi_l,
        AVG(CASE WHEN ps.scale_code = 'Papi_P' THEN ps.score END) as base_papi_p,
        AVG(CASE WHEN ps.scale_code = 'Papi_I' THEN ps.score END) as base_papi_i,
        AVG(CASE WHEN ps.scale_code = 'Papi_Z' THEN ps.score END) as base_papi_z,
        AVG(CASE WHEN ps.scale_code = 'Papi_C' THEN ps.score END) as base_papi_c
    FROM selected_benchmarks sb
    JOIN profiles_psych pp ON sb.employee_id = pp.employee_id
    JOIN papi_scores ps ON sb.employee_id = ps.employee_id
),
-- 3. HITUNG BASELINE STRENGTHS
benchmark_top_strengths AS (
    SELECT ARRAY_AGG(theme) as base_themes
    FROM (
        SELECT s.theme
        FROM selected_benchmarks sb
        JOIN strengths s ON sb.employee_id = s.employee_id
        WHERE s.rank <= 5
        GROUP BY s.theme
        ORDER BY COUNT(*) DESC
        LIMIT 5
    ) sub
),
-- 4. DATA KANDIDAT (FILTER BARU: KECUALIKAN BENCHMARK)
candidate_data AS (
    SELECT 
        e.employee_id, e.fullname, pp.iq, pp.pauli,
        MAX(CASE WHEN ps.scale_code = 'Papi_N' THEN ps.score END) as papi_n,
        MAX(CASE WHEN ps.scale_code = 'Papi_A' THEN ps.score END) as papi_a,
        MAX(CASE WHEN ps.scale_code = 'Papi_L' THEN ps.score END) as papi_l,
        MAX(CASE WHEN ps.scale_code = 'Papi_P' THEN ps.score END) as papi_p,
        MAX(CASE WHEN ps.scale_code = 'Papi_I' THEN ps.score END) as papi_i,
        MAX(CASE WHEN ps.scale_code = 'Papi_Z' THEN ps.score END) as papi_z,
        MAX(CASE WHEN ps.scale_code = 'Papi_C' THEN ps.score END) as papi_c,
        
        ARRAY(SELECT theme FROM strengths s WHERE s.employee_id = e.employee_id ORDER BY rank ASC LIMIT 3) as top_3_strengths,
        ARRAY(SELECT theme FROM strengths s WHERE s.employee_id = e.employee_id AND s.rank <= 5) as my_top_themes
    FROM employees e
    LEFT JOIN profiles_psych pp ON e.employee_id = pp.employee_id
    LEFT JOIN papi_scores ps ON e.employee_id = ps.employee_id
    
    -- LOGIC: Do not include Benchmark IDs in the candidate list
    -- This ensures the output shows the SUCCESSOR, not the person themselves.
    WHERE e.employee_id <> ALL(:benchmark_ids)
    
    GROUP BY e.employee_id, e.fullname, pp.iq, pp.pauli
),
-- 5. MATCH SCORES
tv_scores AS (
    SELECT 
        c.employee_id, c.fullname, c.top_3_strengths,
        b.base_iq, b.base_pauli, b.base_papi_n, 
        
        c.iq, c.pauli, c.papi_n, c.papi_a, c.papi_l, c.papi_i, c.papi_z, c.papi_c,
        
        CASE WHEN c.iq >= b.base_iq THEN 100 ELSE GREATEST(0, 100 - (((b.base_iq - c.iq)::numeric / NULLIF(b.base_iq,0)) * 100 * 1.5)) END as m_iq,
        CASE WHEN c.pauli >= b.base_pauli THEN 100 ELSE GREATEST(0, 100 - (((b.base_pauli - c.pauli)::numeric / NULLIF(b.base_pauli,0)) * 100)) END as m_pauli,
        GREATEST(0, 100 - (ABS(COALESCE(c.papi_n,0) - b.base_papi_n) * 11.1)) as m_papi_n,
        GREATEST(0, 100 - (ABS(COALESCE(c.papi_a,0) - b.base_papi_a) * 11.1)) as m_papi_a,
        GREATEST(0, 100 - (ABS(COALESCE(c.papi_l,0) - b.base_papi_l) * 11.1)) as m_papi_l,
        GREATEST(0, 100 - (ABS(COALESCE(c.papi_i,0) - b.base_papi_i) * 11.1)) as m_papi_i,
        GREATEST(0, 100 - (ABS(COALESCE(c.papi_z,0) - b.base_papi_z) * 11.1)) as m_papi_z,
        GREATEST(0, 100 - (ABS(COALESCE(c.papi_c,0) - b.base_papi_c) * 11.1)) as m_papi_c,
        (SELECT COUNT(*) FROM UNNEST(c.my_top_themes) AS t WHERE t = ANY(bs.base_themes))::numeric / 5.0 * 100 as m_strengths_overlap
    FROM candidate_data c, benchmark_stats b, benchmark_top_strengths bs
),
-- 6. TGV GROUPING
tgv_scores AS (
    SELECT 
        *,
        (m_iq + m_papi_i + m_strengths_overlap) / 3.0 as tgv_cognitive,
        (m_pauli + m_papi_n + m_papi_a) / 3.0 as tgv_motivation,
        (m_papi_l + m_strengths_overlap) / 2.0 as tgv_leadership,
        (m_papi_z) as tgv_adaptability,
        (m_papi_c) as tgv_reliability
    FROM tv_scores
)
-- 7. FINAL OUTPUT
SELECT 
    t.employee_id, t.fullname, 
    array_to_string(t.top_3_strengths, ', ') as strengths_list,
    
    ROUND(t.tgv_cognitive, 1) as score_cognitive,
    ROUND(t.tgv_motivation, 1) as score_motivation,
    ROUND(t.tgv_leadership, 1) as score_leadership,
    ROUND(t.tgv_adaptability, 1) as score_adaptability,
    ROUND(t.tgv_reliability, 1) as score_reliability,
    
    t.iq, t.pauli, t.papi_n, t.papi_a, t.papi_l, t.papi_i, t.papi_z, t.papi_c,
    
    ROUND(t.base_iq, 0) as bench_iq,
    ROUND(t.base_pauli, 0) as bench_pauli,
    ROUND(t.base_papi_n, 1) as bench_papi_n,
    
    ROUND((t.tgv_cognitive * 0.30) + (t.tgv_motivation * 0.25) + (t.tgv_leadership * 0.20) + (t.tgv_adaptability * 0.15) + (t.tgv_reliability * 0.10), 2) as final_match_rate,
    
    CASE 
        WHEN t.tgv_cognitive >= GREATEST(t.tgv_motivation, t.tgv_leadership, t.tgv_adaptability, t.tgv_reliability) THEN 'Cognitive'
        WHEN t.tgv_motivation >= GREATEST(t.tgv_cognitive, t.tgv_leadership, t.tgv_adaptability, t.tgv_reliability) THEN 'Motivation'
        WHEN t.tgv_leadership >= GREATEST(t.tgv_cognitive, t.tgv_motivation, t.tgv_adaptability, t.tgv_reliability) THEN 'Leadership'
        ELSE 'Adaptability/Reliability'
    END as top_tgv,

    CASE 
        WHEN t.tgv_cognitive <= LEAST(t.tgv_motivation, t.tgv_leadership, t.tgv_adaptability, t.tgv_reliability) THEN 'Cognitive'
        WHEN t.tgv_motivation <= LEAST(t.tgv_cognitive, t.tgv_leadership, t.tgv_adaptability, t.tgv_reliability) THEN 'Motivation'
        WHEN t.tgv_leadership <= LEAST(t.tgv_cognitive, t.tgv_motivation, t.tgv_adaptability, t.tgv_reliability) THEN 'Leadership'
        WHEN t.tgv_adaptability <= LEAST(t.tgv_cognitive, t.tgv_motivation, t.tgv_leadership, t.tgv_reliability) THEN 'Adaptability'
        ELSE 'Reliability'
    END as gap_tgv,

    pos.name as role,
    div.name as division,
    dept.name as department,
    dir.name as directorate,
    gr.name as job_level

FROM tgv_scores t
JOIN employees e ON t.employee_id = e.employee_id
LEFT JOIN dim_positions pos ON e.position_id = pos.position_id
LEFT JOIN dim_divisions div ON e.division_id = div.division_id
LEFT JOIN dim_departments dept ON e.department_id = dept.department_id
LEFT JOIN dim_directorates dir ON e.directorate_id = dir.directorate_id
LEFT JOIN dim_grades gr ON e.grade_id = gr.grade_id

ORDER BY final_match_rate DESC
"""

def get_ranked_talent(benchmark_ids_list):
    engine = get_db_engine()
    clean_ids = [x.strip() for x in benchmark_ids_list if x.strip()]
    
    with engine.connect() as conn:
        if not clean_ids:
            # Jika user KOSONGKAN input, kita cari semua High Performer
            fallback_query = text("SELECT DISTINCT employee_id FROM performance_yearly WHERE rating = 5")
            df_fallback = pd.read_sql(fallback_query, conn)
            clean_ids = df_fallback['employee_id'].tolist()
            
            if not clean_ids:
                return pd.DataFrame(), False
            
            is_fallback = True
            # In fallback mode, we DO NOT need to exclude anyone
            # because the benchmark is taken from the general population, not specific individuals.
            # However, our SQL query already includes a `WHERE <> ALL(...)` clause.
            # The trick: Should we pass an empty exclude list when in fallback mode?
            # NO. It is safer to let the query continue excluding those benchmark IDs
            # (meaning a High Performer won’t appear in their own ranking).
            # This makes sense: We are looking for “The Next Stars,” not “The Current Stars.”

        else:
            is_fallback = False

        df = pd.read_sql(text(MATCHING_QUERY), conn, params={"benchmark_ids": clean_ids})
        
    return df, is_fallback