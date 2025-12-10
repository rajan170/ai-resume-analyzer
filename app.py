import streamlit as st
import pandas as pd
from src.parser import ResumeParser
from src.db import Database
from src.scorer import ATSScorer
from src.matcher import JobMatcher
from src.external_search import ExternalJobSearch
from dotenv import load_dotenv
import os


st.set_page_config(
    page_title="AI Resume Analyser",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Initialize Database
db = Database()

# Check Database Connection
if not db.check_connection():
    st.error("Cannot connect to Database.")
    st.info("Please verify that MongoDB is running.")
    st.code("brew services start mongodb-community", language="bash")
    st.stop()

# Custom CSS for polished, professional UI
st.markdown("""
<style>
    /* Global Settings */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    :root {
        --primary: #2563EB;
        --primary-light: #3B82F6;
        --secondary: #64748B;
        --bg-color: #F8FAFC;
        --card-bg: #FFFFFF;
        --text-color: #0F172A;
        --accent-success: #10B981;
        --accent-warning: #F59E0B;
        --accent-error: #EF4444;
    }

    .stApp {
        background-color: var(--bg-color);
    }

    /* Typography */
    h1, h2, h3 {
        color: var(--text-color);
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
    h2 { font-size: 1.5rem; margin-top: 2rem; margin-bottom: 1rem; }
    p, label { color: #334155; }

    /* Custom Header */
    .custom-header {
        padding: 2rem 0;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 2rem;
    }
    
    .custom-header h1 { margin: 0; color: var(--primary); }
    .custom-header p { font-size: 1.1rem; color: var(--secondary); margin-top: 0.5rem; }

    /* Cards */
    .stCard {
        background-color: var(--card-bg);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    
    .stCard:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    /* Metrics Override */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: var(--primary);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: var(--secondary);
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1.25rem;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #1D4ED8;
        border-color: #1D4ED8;
    }
    
    .stButton > button:focus {
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.3);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Input Fields */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px;
        border: 1px solid #CBD5E1;
        padding: 0.5rem;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
    }

    /* Status Boxes */
    .stSuccess { background-color: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }
    .stInfo { background-color: #EFF6FF; color: #1E40AF; border: 1px solid #BFDBFE; }
    .stWarning { background-color: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
    .stError { background-color: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }

    /* Dataframes and Tables */
    [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; border: 1px solid #E2E8F0; }

</style>
""", unsafe_allow_html=True)


# --- UI Components ---

def render_header():
    st.markdown("""
    <div class="custom-header">
        <h1>Resume Analyser AI</h1>
        <p>Intelligent talent acquisition powered by LLMs and semantic search</p>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, help_text=None):
    st.markdown(f"""
    <div class="stCard">
        <div style="font-size: 0.875rem; color: #64748B; margin-bottom: 0.25rem;">{label}</div>
        <div style="font-size: 2rem; font-weight: 700; color: #2563EB;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# --- Navigation ---

st.sidebar.markdown("### Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Upload Resume", "Candidate Dashboard", "Job Management", "Smart Match"],
    label_visibility="collapsed"
)

# --- Main App Logic ---

render_header()

if page == "Upload Resume":
    st.markdown("## 📄 Processing Hub")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="stCard">
            <h3>Upload Candidate Resume</h3>
            <p style="font-size: 0.9rem; margin-bottom: 1rem;">Supported formats: PDF, DOCX (Max 2MB)</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Drag and drop file here", 
            type=["pdf", "docx"], 
            label_visibility="collapsed"
        )

        if uploaded_file:
            if st.button("🚀 Process Resume", type="primary"):
                with st.spinner("Extracting data and running AI analysis..."):
                    try:
                        # Parsing
                        parser = ResumeParser()
                        file_type = uploaded_file.name.split(".")[-1]
                        data = parser.parse(uploaded_file, file_type)
                        
                        # Scoring
                        scorer = ATSScorer()
                        analysis = scorer.score_resume(data)
                        
                        # Save to Session
                        st.session_state['resume_data'] = data
                        st.session_state['resume_analysis'] = analysis
                        st.session_state['resume_id'] = None
                        
                        st.success("Resume processed successfully!")
                    except Exception as e:
                        st.error(f"Processing Failed: {e}")

    with col2:
        if 'resume_data' in st.session_state:
            data = st.session_state['resume_data']
            analysis = st.session_state['resume_analysis']
            
            st.markdown("### Analysis Summary")
            
            score = analysis.get("ats_score", 0)
            score_color = "#10B981" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"
            
            st.markdown(f"""
            <div class="stCard" style="text-align: center;">
                <h4 style="margin:0;">ATS Score</h4>
                <div style="font-size: 3rem; font-weight: 800; color: {score_color};">{score}</div>
                <div style="font-size: 0.875rem; color: #64748B;">out of 100</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("Extracted Details", expanded=True):
                st.write(f"**Name:** {data.get('name')}")
                st.write(f"**Role:** {data.get('job_title')}")
                st.write(f"**Email:** {data.get('email')}")
                
            # DB Persistence
            if st.session_state.get('resume_id') is None and st.button("Save Profile to DB"):
                if data.get("job_title"):
                    data["name"] = f"{data.get('name')} - {data.get('job_title')}"
                data["ats_score"] = score
                data["ats_feedback"] = analysis.get("feedback")
                
                candidate_id = db.insert_candidate(data)
                st.session_state['resume_id'] = candidate_id
                st.success(f"Saved! ID: {candidate_id}")
    
    # Full Analysis Section
    if 'resume_data' in st.session_state:
        st.markdown("---")
        data = st.session_state['resume_data']
        
        tab1, tab2, tab3 = st.tabs(["AI Critique", "Job Matches", "Raw Data"])
        
        with tab1:
            st.markdown("### AI Career Coach")
            if st.button("✨ Generate Critique"):
                with st.spinner("Consulting LLM..."):
                    from src.llm_analyser import LLMAnalyser
                    llm = LLMAnalyser()
                    critique = llm.analyze_resume(data.get("raw_text", ""))
                    st.markdown(critique)

        with tab2:
            st.markdown("### Internal Matches")
            matcher = JobMatcher()
            jobs = db.get_all_jobs()
            matches = matcher.match_jobs(data, jobs) if jobs else []
            
            if matches:
                 for job in matches[:3]:
                    match_score = job.get('match_score')
                    color = "#10B981" if match_score >= 80 else "#64748B"
                    
                    st.markdown(f"""
                    <div class="stCard">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0;">{job.get('title')}</h4>
                            <span style="background:{color}; color:white; padding:4px 12px; border-radius:12px; font-size:0.8rem;">{match_score}% Match</span>
                        </div>
                        <p style="margin-top:0.5rem; font-size:0.9rem;">{job.get('department')}</p>
                        <p style="font-size:0.875rem; color:#64748B;">{job.get('description')[:150]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No strong internal matches found.")

        with tab3:
            st.text_area("Extracted Text", data.get("raw_text"), height=300)

elif page == "Candidate Dashboard":
    st.markdown("## 👥 Candidate Repository")
    
    candidates = db.get_all_candidates()
    
    if candidates:
        df = pd.DataFrame(candidates)
        
        # Metrics Row
        m1, m2, m3 = st.columns(3)
        with m1: render_metric_card("Total Profiles", len(candidates))
        with m2: render_metric_card("Avg ATS Score", f"{df['ats_score'].mean():.1f}")
        with m3: render_metric_card("Top Talent (80+)", len(df[df['ats_score'] >= 80]))

        st.markdown("### Profiles")
        
        # Enhanced Grid View
        for cand in candidates:
            with st.container():
                st.markdown(f"""
                <div class="stCard">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h3 style="margin:0; font-size:1.1rem; color:#1E293B;">{cand.get('name', 'Unnamed Profile')}</h3>
                            <p style="margin:0; color:#64748B; font-size:0.9rem;">{cand.get('email', 'No Email')} | {cand.get('phone', 'No Phone')}</p>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:1.5rem; font-weight:700; color:#2563EB;">{cand.get('ats_score', 0)}</span>
                            <div style="font-size:0.7rem; color:#64748B;">ATS SCORE</div>
                        </div>
                    </div>
                    <div style="margin-top:1rem; padding-top:1rem; border-top:1px solid #F1F5F9; display:flex; gap:10px;">
                        <!-- Action buttons would go here (requires callbacks or form hacks in basic Streamlit) -->
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Native buttons for actions
                c1, c2, c3 = st.columns([1, 1, 6])
                with c1:
                    if st.button("View", key=f"v_{cand['_id']}"):
                        st.session_state['selected_candidate'] = cand
                        st.rerun()
                with c2:
                    if st.button("Delete", key=f"d_{cand['_id']}"):
                        db.delete_candidate(cand['_id'])
                        st.success("Deleted")
                        st.rerun()

    else:
        st.info("No candidates in the database.")

    # Details Modal (Expander)
    if 'selected_candidate' in st.session_state:
        cand = st.session_state['selected_candidate']
        st.markdown("---")
        st.markdown(f"### 🔍 Profile Detail: {cand.get('name')}")
        st.json(cand)
        if st.button("Close Viewer"):
            del st.session_state['selected_candidate']
            st.rerun()

elif page == "Job Management":
    st.markdown("## 💼 Job Postings")
    
    with st.form("new_job"):
        st.markdown("### Create New Opening")
        c1, c2 = st.columns(2)
        title = c1.text_input("Job Title")
        dept = c2.text_input("Department")
        skills = st.text_input("Required Skills (comma separated)")
        desc = st.text_area("Job Description", height=150)
        
        if st.form_submit_button("Publish Job", type="primary"):
            if title and desc:
                db.insert_job({
                    "title": title, "department": dept, "description": desc,
                    "required_skills": [s.strip() for s in skills.split(",") if s.strip()]
                })
                st.success("Job Published!")
            else:
                st.warning("Title and Description are required.")
    
    st.markdown("### Active Listings")
    jobs = db.get_all_jobs()
    for job in jobs:
        st.markdown(f"""
        <div class="stCard">
            <h4>{job.get('title')} <span style="font-weight:400; color:#64748B;">({job.get('department')})</span></h4>
            <p>{job.get('description')}</p>
            <p style="font-size:0.85rem; color:#2563EB;"><strong>Skills:</strong> {', '.join(job.get('required_skills', []))}</p>
        </div>
        """, unsafe_allow_html=True)

elif page == "Smart Match":
    st.markdown("## 🎯 Smart Match")
    st.markdown("Compare any resume against a job description instantly.")
    
    c1, c2 = st.columns(2)
    
    resume_txt = ""
    jd_txt = ""
    
    with c1:
        st.markdown("### 1. Resume Source")
        tabs = st.tabs(["Upload", "Paste"])
        with tabs[0]:
            f = st.file_uploader("Resume File", type=["pdf", "docx"], key="sm_up")
            if f:
                if f.size > 2*1024*1024:
                    st.error("File > 2MB")
                else:
                    parser = ResumeParser()
                    resume_txt = parser.parse(f, f.name.split(".")[-1]).get("raw_text", "")
                    st.success("Loaded!")
        with tabs[1]:
            t = st.text_area("Paste Text", height=200)
            if t: resume_txt = t
            
    with c2:
        st.markdown("### 2. Job Target")
        tabs2 = st.tabs(["Select Existing", "Paste"])
        with tabs2[0]:
            jobs = db.get_all_jobs()
            if jobs:
                sel = st.selectbox("Select Job", jobs, format_func=lambda x: x.get('title'))
                if sel: jd_txt = sel.get('description')
        with tabs2[1]:
            j = st.text_area("Paste JD", height=200)
            if j: jd_txt = j

    if st.button("Run Match Analysis", type="primary", use_container_width=True):
        if not resume_txt or not jd_txt:
            st.error("Missing Resume or Job Description")
        else:
            if len(resume_txt) > 10000:
                st.error("Resume too long (>10k chars)")
            else:
                with st.spinner("Analyzing fit..."):
                    from src.llm_analyser import LLMAnalyser
                    res = LLMAnalyser().analyze_fit(resume_txt, jd_txt)
                    st.markdown("### 📋 Fit Report")
                    st.markdown(res)


