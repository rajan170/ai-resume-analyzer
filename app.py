import streamlit as st
import pandas as pd
from src.parser import ResumeParser
from src.db import Database
from src.scorer import ATSScorer
from src.matcher import JobMatcher
from src.external_search import ExternalJobSearch
from dotenv import load_dotenv
import os

"""
AI-Driven Resume Analyser
=========================

This is the main entry point for the Streamlit application. It serves as the
presentation layer, orchestrating the interaction between the user (recruiter),
the data layer (MongoDB), and the logic layer (Parsing, AI Analysis, Matching).

Key Features:
- Resume Upload & Parsing: Extracts structured data from PDF/DOCX.
- AI Analysis: Uses local LLMs to provide qualitative feedback.
- Candidate Dashboard: Manages candidate profiles.
- Job Matching: Semantically matches candidates to job openings.
"""

# Load environment variables
load_dotenv()

# Initialize Database
db = Database()

# Page Configuration
# We set the page layout to 'wide' to accommodate the dashboard view and
# ensure the sidebar is expanded by default for better navigation discoverability.
st.set_page_config(
    page_title="AI Resume Analyser",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
# We inject custom CSS to override Streamlit's default look, aiming for a
# professional, clean aesthetic. This includes custom colors for headers,
# card-like containers for data, and polished button styles.
st.markdown("""
<style>
    /* Main styling */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    h1 {
        color: #1f77b4;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #2c3e50;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #34495e;
        font-weight: 500;
    }
    
    /* Card-like containers */
    .stExpander {
        background-color: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1f77b4;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #1f77b4;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #1557a0;
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3);
    }
    
    /* Warning boxes */
    .stWarning {
        background-color: rgba(255, 193, 7, 0.1);
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 4px;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: rgba(23, 162, 184, 0.1);
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        border-radius: 4px;
    }
    
    /* Success boxes */
    .stSuccess {
        background-color: rgba(40, 167, 69, 0.1);
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 4px;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e9ecef;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #4a4a4a;
        border-radius: 10px;
        padding: 2rem;
    }
    
    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

st.title("AI-Driven Resume Analyser")
st.markdown("*Intelligent resume screening powered by AI and semantic matching*")
st.markdown("---")

st.sidebar.title("Navigation")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Select Page",
    ["Upload Resume", "Candidate Dashboard", "Job Management"],
    label_visibility="collapsed"
)

page_name = page

if page_name == "Upload Resume":
    st.header("Upload Resume")
    st.markdown("Upload a candidate's resume to extract information and generate insights")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF or DOCX file",
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX"
    )
    
    if uploaded_file is not None:
        if st.button("Parse & Analyze"):
            with st.spinner("Analyzing resume..."):
                try:
                    # 1. Parse
                    # We use the ResumeParser to extract text and entities.
                    # The parser also attempts to identify the candidate's job title.
                    parser = ResumeParser()
                    file_type = uploaded_file.name.split(".")[-1]
                    data = parser.parse(uploaded_file, file_type)
                    
                    # 2. Score
                    # The ATSScorer evaluates the resume against standard criteria
                    # (e.g., presence of email, phone, skills) to generate a baseline score.
                    scorer = ATSScorer()
                    analysis = scorer.score_resume(data)
                    
                    # Store in session state
                    st.session_state['resume_data'] = data
                    st.session_state['resume_analysis'] = analysis
                    st.session_state['resume_id'] = None # Reset ID if new parse
                    
                except Exception as e:
                    st.error(f"Error processing file: {e}")

        # Check if data exists in session state
        if 'resume_data' in st.session_state:
            data = st.session_state['resume_data']
            analysis = st.session_state['resume_analysis']
            
            # 3. Display Results
            st.markdown("---")
            st.subheader("Analysis Results")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### Candidate Details")
                st.markdown(f"""
                <div style='background-color: rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 10px; border-left: 4px solid #1f77b4;'>
                    <p style='margin: 0.5rem 0;'><strong>Name:</strong> {data.get('name') or 'Not detected'}</p>
                    <p style='margin: 0.5rem 0;'><strong>Email:</strong> {data.get('email') or 'Not detected'}</p>
                    <p style='margin: 0.5rem 0;'><strong>Phone:</strong> {data.get('phone') or 'Not detected'}</p>
                    <p style='margin: 0.5rem 0;'><strong>Skills:</strong> {', '.join(data.get('skills', [])) or 'None detected'}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### ATS Analysis")
                score = analysis.get("ats_score")
                
                # Score with color coding
                if score >= 80:
                    score_color = "#28a745"
                    score_label = "Excellent"
                elif score >= 60:
                    score_color = "#ffc107"
                    score_label = "Good"
                else:
                    score_color = "#dc3545"
                    score_label = "Needs Improvement"
                
                st.markdown(f"""
                <div style='background-color: rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 10px; text-align: center;'>
                    <h1 style='color: {score_color}; margin: 0;'>{score}/100</h1>
                    <p style='color: {score_color}; font-weight: 600; margin: 0.5rem 0;'>{score_label}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.progress(score / 100)
                
                if analysis.get("feedback"):
                    st.markdown("**Areas for Improvement:**")
                    for tip in analysis.get("feedback"):
                        st.warning(f"{tip}")

            # 4. Save (Only if not already saved)
            # We check session_state to prevent duplicate insertions if the app reruns.
            if st.session_state.get('resume_id') is None:
                # Update name format: Name - Job Title
                # This "Smart Naming" convention helps recruiters quickly identify
                # candidates in the dashboard list without opening every profile.
                if data.get("job_title"):
                    data["name"] = f"{data.get('name')} - {data.get('job_title')}"
                
                data["ats_score"] = score
                data["ats_feedback"] = analysis.get("feedback")
                candidate_id = db.insert_candidate(data)
                st.session_state['resume_id'] = candidate_id
                st.success(f"Profile saved! ID: {candidate_id}")
            else:
                st.info(f"Profile saved (ID: {st.session_state['resume_id']})")
            
            # 5. AI Resume Critique
            st.markdown("---")
            st.subheader("AI Resume Critique")
            st.markdown("*Get detailed, personalized feedback from our AI career coach*")
            
            if st.button("Generate AI Feedback", use_container_width=True):
                # We use st.status to provide a detailed, step-by-step progress indicator.
                # This is crucial for UX as local LLM inference can take a few seconds.
                with st.status("AI Career Coach is thinking...", expanded=True) as status:
                    st.write("Initializing local AI model...")
                    from src.llm_analyser import LLMAnalyser
                    llm = LLMAnalyser()
                    
                    st.write("Analyzing resume content and skills...")
                    critique = llm.analyze_resume(data.get("raw_text", ""))
                    
                    st.write("Formatting insights...")
                    status.update(label="Analysis Complete!", state="complete", expanded=False)
                    
                st.markdown(critique)

            # 6. Job Recommendations
            st.markdown("---")
            st.subheader("Job Recommendations")
            
            col_rec1, col_rec2 = st.columns(2)
            
            with col_rec1:
                st.markdown("#### Internal Matches (Semantic)")
                st.markdown("*AI-powered semantic job matching*")
                matcher = JobMatcher()
                jobs = db.get_all_jobs()
                if jobs:
                    matches = matcher.match_jobs(data, jobs)
                    if matches:
                        for job in matches[:3]:
                            match_score = job.get('match_score')
                            if match_score >= 80:
                                badge_color = "#28a745"
                            elif match_score >= 60:
                                badge_color = "#ffc107"
                            else:
                                badge_color = "#6c757d"
                                
                            with st.expander(f"**{job.get('title')}** - Match: {match_score}%"):
                                st.markdown(f"<span style='background-color: {badge_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem;'>{match_score}% Match</span>", unsafe_allow_html=True)
                                st.write(job.get('description'))
                                st.caption(f"**Skills:** {', '.join(job.get('required_skills', []))}")
                    else:
                        st.info("No matching internal jobs found.")
                else:
                    st.info("No internal jobs in database.")

            with col_rec2:
                st.markdown("#### External Opportunities")
                st.markdown("*Search across LinkedIn, Indeed, and more*")
                if st.button("Search Online Jobs", use_container_width=True):
                    with st.spinner("Searching job portals..."):
                        from src.external_search import ExternalJobSearch
                        ext_search = ExternalJobSearch()
                        ext_jobs = ext_search.recommend_jobs(data.get("skills", []))
                        
                        if ext_jobs:
                            for job in ext_jobs:
                                st.markdown(f"**[{job.get('title')}]({job.get('link')})**")
                                st.caption(job.get('snippet')[:150] + "...")
                                st.markdown("---")
                        else:
                            st.warning("No external jobs found.")

elif page_name == "Candidate Dashboard":
    st.header("Candidate Dashboard")
    st.markdown("View and manage all candidate profiles")
    st.markdown("---")
    
    candidates = db.get_all_candidates()
    if candidates:
        df = pd.DataFrame(candidates)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Candidates", len(candidates))
        with col2:
            avg_score = df['ats_score'].mean() if 'ats_score' in df.columns else 0
            st.metric("Avg ATS Score", f"{avg_score:.1f}")
        with col3:
            high_scorers = len(df[df['ats_score'] >= 80]) if 'ats_score' in df.columns else 0
            st.metric("High Scorers (80+)", high_scorers)
        
        st.markdown("---")
        st.markdown("#### All Candidates")
        
        # Display candidates with management options
        # We iterate through candidates and use columns to create a grid-like layout.
        # Each row has the candidate's info, score, and action buttons.
        for idx, candidate in enumerate(candidates):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                # Make name clickable to show details
                if st.button(f"{candidate.get('name', 'Unknown')}", key=f"view_{idx}", help="Click to view full details"):
                    st.session_state['selected_candidate'] = candidate
                    st.rerun()
                st.caption(candidate.get('email', 'No email'))
            
            with col2:
                score = candidate.get('ats_score', 0)
                if score >= 80:
                    color = "green"
                elif score >= 60:
                    color = "orange"
                else:
                    color = "red"
                st.markdown(f":{color}[ATS Score: {score}]")
            
            with col3:
                # Edit Name
                with st.popover("Edit"):
                    new_name = st.text_input("New Name", value=candidate.get('name', ''), key=f"edit_{idx}")
                    if st.button("Save", key=f"save_{idx}"):
                        db.update_candidate_name(candidate['_id'], new_name)
                        st.success("Updated!")
                        st.rerun()
            
            with col4:
                # Delete Candidate
                if st.button("Delete", key=f"del_{idx}"):
                    db.delete_candidate(candidate['_id'])
                    st.success("Deleted!")
                    st.rerun()
            
            st.divider()

        # Show selected candidate details in a modal/expander
        if 'selected_candidate' in st.session_state:
            cand = st.session_state['selected_candidate']
            with st.expander(f"Full Profile: {cand.get('name', 'Unknown')}", expanded=True):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### Contact Info")
                    st.write(f"**Email:** {cand.get('email', 'N/A')}")
                    st.write(f"**Phone:** {cand.get('phone', 'N/A')}")
                    st.markdown("#### Skills")
                    st.write(", ".join(cand.get('skills', [])))
                
                with c2:
                    st.markdown("#### ATS Analysis")
                    st.metric("Score", f"{cand.get('ats_score', 0)}/100")
                    if cand.get('feedback'):
                        st.write("**Feedback:**")
                        for tip in cand.get('feedback', []):
                            st.warning(tip)
                
                st.markdown("#### Resume Text")
                st.text_area("Raw Text", cand.get('raw_text', ''), height=200, disabled=True)
                
                if st.button("Close Details"):
                    del st.session_state['selected_candidate']
                    st.rerun()
        
        st.markdown("---")
        st.markdown("#### Job Matching")
        selected_candidate_index = st.selectbox(
            "Select Candidate",
            range(len(candidates)),
            format_func=lambda x: f"{candidates[x].get('name', 'Unknown')} ({candidates[x].get('ats_score', 0)}/100)"
        )
        
        if st.button("Find Matching Jobs", use_container_width=True):
            candidate = candidates[selected_candidate_index]
            matcher = JobMatcher()
            jobs = db.get_all_jobs()
            
            if not jobs:
                st.warning("No jobs found in database. Please add jobs first.")
            else:
                matches = matcher.match_jobs(candidate, jobs)
                st.subheader(f"Recommended Jobs for {candidate.get('name')}")
                for job in matches:
                    match_score = job.get('match_score')
                    if match_score >= 80:
                        badge_color = "#28a745"
                    elif match_score >= 60:
                        badge_color = "#ffc107"
                    else:
                        badge_color = "#6c757d"
                        
                    with st.expander(f"**{job.get('title')}** - {match_score}% Match"):
                        st.markdown(f"<span style='background-color: {badge_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem;'>{match_score}% Match</span>", unsafe_allow_html=True)
                        st.write(f"**Department:** {job.get('department')}")
                        st.write(f"**Description:** {job.get('description')}")
                        st.write(f"**Required Skills:** {', '.join(job.get('required_skills', []))}")
    else:
        st.info("No candidates found. Upload a resume to get started!")

elif page_name == "Job Management":
    st.header("Job Management")
    st.markdown("Create and manage job postings")
    st.markdown("---")
    
    st.subheader("Post New Job")
    with st.form("job_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Job Title *", placeholder="e.g., Senior Software Engineer")
            department = st.text_input("Department *", placeholder="e.g., Engineering")
        with col2:
            skills = st.text_input("Required Skills (comma separated) *", placeholder="Python, React, AWS")
        
        description = st.text_area("Job Description *", placeholder="Describe the role, responsibilities, and requirements...", height=150)
        
        submitted = st.form_submit_button("Post Job", use_container_width=True)
        
        if submitted:
            if title and department and description and skills:
                job_data = {
                    "title": title,
                    "department": department,
                    "description": description,
                    "required_skills": [s.strip() for s in skills.split(",") if s.strip()]
                }
                db.insert_job(job_data)
                st.success("Job posted successfully!")
            else:
                st.error("Please fill in all required fields.")
    
    st.markdown("---")
    st.subheader("Current Openings")
    jobs = db.get_all_jobs()
    if jobs:
        for idx, job in enumerate(jobs):
            with st.expander(f"**{job.get('title')}** - {job.get('department')}"):
                st.write(f"**Description:** {job.get('description')}")
                st.write(f"**Required Skills:** {', '.join(job.get('required_skills', []))}")
    else:
        st.info("No job postings yet. Create one above!")

