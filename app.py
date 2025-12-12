import streamlit as st
import pandas as pd
import re
import html
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

    /* Buttons - Force white text with multiple selectors */
    .stButton > button,
    .stButton > button p,
    .stButton > button span,
    .stButton button[kind="primary"],
    .stButton button[kind="secondary"] {
        color: #FFFFFF !important;
    }
    
    .stButton > button {
        background-color: var(--primary);
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
    
    /* Primary Button - ensure white text */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
    }
    
    /* Secondary Button - readable text */
    .stButton > button[kind="secondary"] {
        background-color: #64748B;
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
    ["Analysis & Search", "Candidate Dashboard", "Job Management", "Smart Match"],
    label_visibility="collapsed"
)

# --- Main App Logic ---

render_header()

if page == "Analysis & Search":
    st.markdown("## Resume Analysis & Job Search")
    
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
            if st.button("Process Resume", type="primary"):
                with st.spinner("Extracting data and running AI analysis..."):
                    try:
                        # Parsing
                        parser = ResumeParser()
                        file_type = uploaded_file.name.split(".")[-1]
                        data = parser.parse(uploaded_file, file_type)

                        # Enhanced Title Extraction using LLM
                        from src.llm_analyser import LLMAnalyser
                        try:
                            llm_analyser = LLMAnalyser()
                            refined_title = llm_analyser.extract_title_from_resume(data.get("raw_text", ""))
                            if refined_title and refined_title != "Professional":
                                data["job_title"] = refined_title
                        except Exception as e:
                            print(f"LLM Title Extraction failed: {e}")
                        
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
        
        tab1, tab2, tab3 = st.tabs(["AI Critique", "Job & LinkedIn Matches", "Raw Data"])
        
        with tab1:
            st.markdown("### AI Career Coach")
            if st.button("Generate Critique"):
                with st.spinner("Consulting LLM..."):
                    from src.llm_analyser import LLMAnalyser
                    llm = LLMAnalyser()
                    critique = llm.analyze_resume(data.get("raw_text", ""))
                    st.markdown(critique)

        with tab2:
            c1, c2 = st.columns(2)
            
            with c1:
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

            with c2:
                st.markdown("### External Job Search")
                st.markdown(f"**Target Role:** {data.get('job_title', 'Not found')}")
                
                # Search filters in an expander for cleaner UI
                with st.expander("Search Filters", expanded=False):
                    location_ext = st.text_input("Location", placeholder="e.g., San Francisco, Remote", key="ext_loc")
                    remote_ext = st.checkbox("Remote only", key="ext_remote")
                    num_ext = st.slider("Number of results", 3, 10, 5, key="ext_num")
                
                if st.button("Search Job Boards", type="secondary", use_container_width=True, key="ext_search_btn"):
                    with st.spinner("Searching LinkedIn and Indeed..."):
                        from src.external_search import ExternalJobSearch
                        ext_search = ExternalJobSearch()
                        ext_jobs = ext_search.recommend_jobs(
                            skills=data.get("skills", []), 
                            job_title=data.get("job_title"),
                            location=location_ext if location_ext else None,
                            remote_only=remote_ext,
                            limit=num_ext
                        )
                        st.session_state['ext_search_results'] = ext_jobs
                
                # Display external search results
                if st.session_state.get('ext_search_results'):
                    for job in st.session_state['ext_search_results']:
                        # Build metadata
                        meta_parts = []
                        if job.get('location') != "Not specified":
                            meta_parts.append(f"Location: {job.get('location')}")
                        if job.get('is_remote'):
                            meta_parts.append("Remote")
                        meta_str = " • ".join(meta_parts) if meta_parts else ""
                        
                        # Clean snippet
                        snippet = job.get('snippet', '')
                        snippet = html.unescape(snippet)  # Decode HTML entities first
                        snippet = re.sub(r'<[^>]+>', '', snippet)  # Remove HTML tags
                        snippet = snippet.replace('&nbsp;', ' ').strip()
                        
                        # Build HTML without newlines
                        html_card = f'<div style="border-left: 4px solid #0077B5; padding: 1rem; margin: 0.5rem 0; background: white; border-radius: 4px;"><a href="{job.get("link")}" target="_blank" style="text-decoration:none; color:#0F172A;"><h4 style="margin:0; color:#0077B5;">{job.get("title")} <span style="font-size:0.8rem;">↗</span></h4></a>'
                        if meta_str:
                            html_card += f'<p style="font-size:0.8rem; color:#94A3B8; margin:0.25rem 0;">{meta_str}</p>'
                        html_card += f'<p style="font-size:0.875rem; color:#64748B; margin-top:0.5rem;">{snippet[:120]}...</p></div>'
                        
                        st.markdown(html_card, unsafe_allow_html=True)
                elif 'ext_search_results' in st.session_state:
                    st.info("No jobs found. Try different filters.")


        with tab3:
            st.text_area("Extracted Text", data.get("raw_text"), height=300)

elif page == "Candidate Dashboard":
    st.markdown("## Candidate Repository")
    
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
        st.markdown(f"### Profile Detail: {cand.get('name')}")
        st.json(cand)
        if st.button("Close Viewer"):
            del st.session_state['selected_candidate']
            st.rerun()

elif page == "Job Management":
    st.markdown("## Job Postings")
    
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
    st.markdown("## Smart Match")
    st.markdown("Compare any resume against a job description instantly.")
    
    c1, c2 = st.columns(2)
    
    resume_txt = ""
    jd_txt = ""
    resume_data = {}

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
                    resume_data = parser.parse(f, f.name.split(".")[-1])
                    resume_txt = resume_data.get("raw_text", "")
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
                    
                    # Store current job info
                    current_job_title = None
                    if 'sel' in locals() and sel:
                        current_job_title = sel.get('title')
                    elif jd_txt:
                        # Extract title from pasted text using LLM
                        current_job_title = LLMAnalyser().extract_job_title(jd_txt)
                    
                    # Store in session state
                    st.session_state['smart_match_result'] = res
                    st.session_state['smart_match_resume_data'] = resume_data
                    st.session_state['smart_match_job_title'] = current_job_title
                    st.session_state['smart_match_selected_job'] = sel if 'sel' in locals() else None
    
    # Display results from session state if available
    if 'smart_match_result' in st.session_state:
        st.markdown("### Fit Report")
        st.markdown(st.session_state['smart_match_result'])
        
        st.markdown("---")
        st.markdown("### External Job Search")
        
        # Get resume data from session state
        saved_resume_data = st.session_state.get('smart_match_resume_data', {})
        saved_job = st.session_state.get('smart_match_selected_job')
        saved_job_title = st.session_state.get('smart_match_job_title')  # NEW: Get stored job title
        
        search_skills = saved_resume_data.get("skills", [])
        search_title = saved_resume_data.get("job_title")
        
        # Fallback 1: Use job description title if no resume title
        if not search_title and saved_job_title:
            search_title = saved_job_title
        
        # Fallback 2: Try from selected job object
        if not search_title and saved_job:
            search_title = saved_job.get('title')
        
        # Show hint if no data available
        if not search_title and not search_skills:
            st.warning("No resume or job data found. Please run 'Match Analysis' first to extract skills and job title.")
        
        # Search filters
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            # Allow user to override the search title
            final_search_title = st.text_input("Job Title", value=search_title if search_title else "")
        with col_f2:
            location_input = st.text_input("Location", placeholder="e.g., New York, Remote")
            
        with col_f3:
            num_results = st.slider("Results", 3, 15, 5)
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            remote_only = st.checkbox("Remote only")
        with col_c2:
            posted_last_24h = st.checkbox("Posted last 24h")
        
        if st.button("Search Job Boards", key="linkedin_search_btn", type="primary", use_container_width=True):
            with st.spinner("Searching LinkedIn and Indeed..."):
                from src.external_search import ExternalJobSearch
                ext = ExternalJobSearch()
                results = ext.recommend_jobs(
                    skills=search_skills,
                    job_title=final_search_title, # Use the input value
                    location=location_input if location_input else None,
                    remote_only=remote_only,
                    posted_last_24h=posted_last_24h,
                    limit=num_results
                )
                
                # Store results in session state
                st.session_state['linkedin_results'] = results
        
        # Display job results if available
        if 'linkedin_results' in st.session_state and st.session_state['linkedin_results']:
            st.markdown(f"#### Found {len(st.session_state['linkedin_results'])} Jobs")
            for job in st.session_state['linkedin_results']:
                # Build metadata line
                metadata_parts = []
                if job.get('location') != "Not specified":
                    metadata_parts.append(f"Location: {job.get('location')}")
                if job.get('is_remote'):
                    metadata_parts.append("Remote")
                
                metadata_str = " • ".join(metadata_parts) if metadata_parts else ""
                
                # Clean snippet - remove HTML tags
                snippet = job.get('snippet', '')
                snippet = html.unescape(snippet)  # Decode HTML entities first
                snippet = re.sub(r'<[^>]+>', '', snippet)  # Remove HTML tags
                snippet = snippet.replace('&nbsp;', ' ').strip()  # Clean entities
                
                # Build HTML string without newlines to prevent code block rendering
                html_card = f'<div style="border-left: 4px solid #0077B5; padding: 1rem; margin: 0.5rem 0; background: white; border-radius: 4px;"><a href="{job.get("link")}" target="_blank" style="text-decoration:none; color:#0F172A;"><h4 style="margin:0; color:#0077B5;">{job.get("title")} <span style="font-size:0.8rem;">↗</span></h4></a>'
                if metadata_str:
                    html_card += f'<p style="font-size:0.8rem; color:#94A3B8; margin:0.25rem 0;">{metadata_str}</p>'
                html_card += f'<p style="font-size:0.875rem; color:#64748B; margin-top:0.5rem;">{snippet[:150]}...</p></div>'
                
                st.markdown(html_card, unsafe_allow_html=True)
        elif 'linkedin_results' in st.session_state:
            st.info("No jobs found with these criteria. Try adjusting your filters or location.")


