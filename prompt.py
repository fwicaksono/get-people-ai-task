import google.generativeai as genai

JOB_PROFILE_PROMPT = """
You are an expert Talent Acquisition Strategist. Draft a Job Profile based on these inputs:

### Context
- **Role**: {role}
- **Level**: {level}
- **Purpose**: {purpose}

### User Provided Details:
- **Specific Responsibilities**: {user_resps}
- **Required Competencies**: {user_comps}

### Instructions:
1. **Tone**: Professional, clear, and direct.
2. **Structure**: Strictly follow the sections below.
3. **Content Guidelines**:
    - **Job requirements**: Focus on hard skills/expertise. Use bolding for the category (e.g., **SQL expertise:**) followed by details.
    - **Job description**: Write a cohesive narrative paragraph (NOT a list). Focus on the 'why' and 'how' of the role.
    - **Key competencies**: List specific tools/tech stack. Use bolding for the tool names.

### Output Format:

**Job requirements**
* **[Skill Category]:** [Description]. (e.g. **SQL expertise:** complex joins, window functions...)
* **[Skill Category]:** [Description].
* **[Skill Category]:** [Description].

**Job description**
[Write a compelling paragraph here. Example: You turn business questions into data-driven answers. You’ll own the analysis cycle end-to-end: understand context, shape clear dashboards, and craft narratives that drive decisions.]

**key competencies**
* **[Tool/Skill]** (context), **[Tool/Skill]**, **[Tool/Skill]**
* **[Tool/Skill]**, **[Tool/Skill]**
"""

# --- CANDIDATE ANALYSIS PROMPT (New) ---
CANDIDATE_INSIGHT_PROMPT = """
You are a Talent Intelligence Analyst. Explain why **{name}** is the top-ranked candidate (Match Rate: {match_rate}%) for this role.

### Candidate Data:
- **Top Strengths**: {strengths}
- **Cognitive Score**: {s_cog} (Weight 30%)
- **Motivation Score**: {s_mot} (Weight 25%)
- **Leadership Score**: {s_lead} (Weight 20%)

### Instructions:
1. Provide a concise "Why this candidate?" summary.
2. Highlight their key differentiator (the "Spike").
3. Mention one potential gap if any score is below 75.
4. Keep it business-focused and under 100 words.

### Output:
**🚀 Why Top Rank:** [Your Analysis Here]
"""


def generate_job_profile_gemini(role, level, purpose, resps, comps):
    """Memanggil Gemini API dengan format prompt baru"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Kita gabungkan input user jadi string biasa, biar AI yang memformatnya jadi bullet/bold
        resps_str = ", ".join(resps) if resps else "(None provided, please suggest standard based on role)"
        comps_str = ", ".join(comps) if comps else "(None provided, please suggest standard based on role)"
        
        final_prompt = JOB_PROFILE_PROMPT.format(
            role=role, 
            level=level, 
            purpose=purpose,
            user_resps=resps_str,
            user_comps=comps_str
        )
        
        response = model.generate_content(final_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

def generate_candidate_analysis(candidate_row):
    """Menganalisis Top Candidate"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        final_prompt = CANDIDATE_INSIGHT_PROMPT.format(
            name=candidate_row['fullname'],
            match_rate=candidate_row['final_match_rate'],
            strengths=candidate_row['strengths_list'],
            s_cog=candidate_row['score_cognitive'],
            s_mot=candidate_row['score_motivation'],
            s_lead=candidate_row['score_leadership']
        )
        
        response = model.generate_content(final_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Analysis Error: {str(e)}"