import streamlit as st
import pathlib
import pandas as pd

st.set_page_config(
    page_title="Workforce Intelligence Platform | Enterprise AI",
    page_icon="\U0001f6e1\ufe0f",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "page" not in st.session_state:
    st.session_state.page = "cover"

if st.session_state.page == "dashboard":
    from dashboard_page import render as render_dashboard
    render_dashboard()
    st.stop()

# --- COVER PAGE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%); }
    .block-container { padding: 2rem 4rem !important; }
    a { text-decoration: none; }
    .hero-icon { font-size: 4rem; text-align: center; margin-bottom: 0.5rem; }
    .hero-title {
        font-size: 3.2rem; font-weight: 800; text-align: center;
        background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 50%, #F472B6 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        line-height: 1.2; margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.15rem; text-align: center; color: #94A3B8;
        max-width: 720px; margin: 0 auto 2rem auto; line-height: 1.6;
    }
    .stat-grid { display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin: 2rem 0; }
    .stat-card {
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; padding: 1.2rem 2rem; text-align: center; min-width: 140px;
        backdrop-filter: blur(8px);
    }
    .stat-value { font-size: 1.8rem; font-weight: 700; color: #F8FAFC; }
    .stat-label { font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }
    .section-title { font-size: 1.5rem; font-weight: 700; color: #F1F5F9; margin-bottom: 0.5rem; }
    .section-sub { color: #64748B; font-size: 0.9rem; margin-bottom: 1.5rem; }
    .feature-card {
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px; padding: 1.5rem; height: 100%;
        transition: border-color 0.2s, background 0.2s;
    }
    .feature-card:hover { border-color: rgba(96,165,250,0.3); background: rgba(255,255,255,0.05); }
    .feature-icon { font-size: 1.8rem; margin-bottom: 0.6rem; }
    .feature-name { font-size: 1rem; font-weight: 600; color: #F1F5F9; margin-bottom: 0.4rem; }
    .feature-desc { font-size: 0.82rem; color: #94A3B8; line-height: 1.5; }
    .divider { border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent); margin: 2.5rem 0; }
    .footer { text-align: center; color: #475569; font-size: 0.75rem; padding: 2rem 0 0 0; }
    .arch-box {
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px; padding: 1rem; text-align: center; min-height: 80px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .arch-label { font-size: 0.75rem; color: #94A3B8; margin-top: 0.3rem; }
    .arch-arrow { text-align: center; color: #475569; font-size: 1.2rem; padding: 0.3rem 0; }
    .launch-btn {
        display: inline-flex; align-items: center; gap: 0.5rem;
        background: linear-gradient(135deg, #3B82F6, #8B5CF6);
        color: white !important; font-weight: 600; font-size: 1rem;
        padding: 0.75rem 2rem; border-radius: 8px; transition: opacity 0.2s, transform 0.2s;
        border: none; cursor: pointer;
    }
    .launch-btn:hover { opacity: 0.9; transform: translateY(-1px); }
</style>
""", unsafe_allow_html=True)

base_dir = pathlib.Path(__file__).parent
datasets_dir = base_dir / "datasets" / "clean"

emp_count = 0
dept_count = 0
try:
    df = pd.read_csv(datasets_dir / "employees.csv")
    emp_count = len(df)
    dept_count = df["department"].nunique() if "department" in df.columns else 0
except Exception:
    pass

st.markdown("<div class='hero-icon'>\U0001f6e1\ufe0f</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-title'>AI Workforce Intelligence<br>Platform</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='hero-subtitle'>"
    "An autonomous multi-agent system that analyzes workforce data, forecasts capacity gaps, "
    "and delivers executive-ready strategic recommendations \u2014 powered by a cascading agent "
    "orchestration framework with deterministic fallback."
    "</div>",
    unsafe_allow_html=True
)

if st.button("🚀 Launch AI Workforce Intelligence", use_container_width=True, type="primary"):
    st.session_state.page = "dashboard"
    st.rerun()

st.markdown('<div class="stat-grid">', unsafe_allow_html=True)
cols = st.columns(4)
metrics = [
    ("🤖", f"{emp_count}", "Employees Tracked"),
    ("📊", f"{dept_count}", "Departments"),
    ("⚡", "7", "Autonomous Agents"),
    ("📋", "4", "Report Types"),
]
for i, (icon, val, label) in enumerate(metrics):
    with cols[i]:
        st.markdown(
            f'<div class="stat-card">'
            f'<div class="stat-value">{icon} {val}</div>'
            f'<div class="stat-label">{label}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

st.markdown('<div class="section-title">🏗️ Architecture Overview</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">A cascading multi-agent pipeline \u2014 each agent delegates to specialized sub-agents, '
    'producing a routed report tailored to the user query.</div>',
    unsafe_allow_html=True
)

layers = [
    [("💬", "User Query"), ("🔍", "Intent Router")],
    [("🧠", "Manager Agent")],
    [("🔎", "Workforce\nAgent"), ("📈", "Utilization\nAgent"), ("📊", "Forecast\nAgent"), ("💡", "Recommendation\nAgent")],
    [("🔧", "Employee\nTool"), ("📂", "Allocation\nTool"), ("⏳", "Worklog\nTool"), ("📅", "Capacity\nTool")],
    [("📋", "Report Engine"), ("✅", "Validator"), ("📤", "Exporter")],
]

for layer in layers:
    cols = st.columns(len(layer))
    for i, (icon, label) in enumerate(layer):
        with cols[i]:
            st.markdown(
                f'<div class="arch-box"><div style="font-size:1.5rem;">{icon}</div>'
                f'<div class="arch-label">{label}</div></div>',
                unsafe_allow_html=True
            )
    if layer != layers[-1]:
        st.markdown('<div class="arch-arrow">▼</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

st.markdown('<div class="section-title">⚡ Key Capabilities</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Intelligent features designed for enterprise workforce planning.</div>',
    unsafe_allow_html=True
)

features = [
    ("🧠", "Multi-Agent Orchestration",
     "Manager Agent delegates queries to specialized sub-agents (Workforce, Utilization, Forecast, Recommendation) based on detected intent."),
    ("📊", "Executive Reporting Engine",
     "Intelligent Report Engine produces routed reports \u2014 Employee Lookup, Utilization, Forecast, Executive Briefing, and Strategic Recommendations."),
    ("🔮", "Capacity Forecasting",
     "Analyzes historical capacity data against projected demand to identify FTE gaps, hiring needs, and workload imbalances."),
    ("⚖️", "Utilization Analysis",
     "Evaluates department and individual allocation rates, flags overallocation (>90%) and underutilization (<70%) risks."),
    ("🛡️", "Deterministic Fallback",
     "Full mock-response mode without API keys \u2014 all agent orchestration, routing, and reporting remain fully operational for demos."),
    ("📋", "Evidence & Traceability",
     "Every report includes an evidence card showing primary/supporting agents, datasets used, rows processed, validation status, and confidence score."),
]

for i in range(0, len(features), 3):
    cols = st.columns(3)
    for j, (icon, name, desc) in enumerate(features[i:i+3]):
        with cols[j]:
            st.markdown(
                f'<div class="feature-card">'
                f'<div class="feature-icon">{icon}</div>'
                f'<div class="feature-name">{name}</div>'
                f'<div class="feature-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

st.markdown('<div class="section-title">📋 Report Types</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">The Report Router dispatches to the appropriate report engine based on query intent.</div>',
    unsafe_allow_html=True
)

report_types = [
    ("💼", "Employee Lookup", "Individual profile details, role, department, skills, project allocations, and personalized recommendations."),
    ("📊", "Utilization Report", "Department-level utilization, overallocated/underutilized employees, risks, and rebalancing recommendations."),
    ("🔮", "Forecast Report", "Capacity vs. demand analysis, FTE gap quantification, hiring recommendations, and timeline projections."),
    ("📋", "Executive Briefing", "Full workforce health assessment, multi-agent synthesized narratives, strategic recommendations, and decision framework."),
]

cols = st.columns(2)
for i, (icon, name, desc) in enumerate(report_types):
    with cols[i % 2]:
        st.markdown(
            f'<div class="feature-card" style="margin-bottom: 1rem;">'
            f'<div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.4rem;">'
            f'<span style="font-size:1.3rem;">{icon}</span>'
            f'<span class="feature-name" style="margin-bottom:0;">{name}</span>'
            f'</div>'
            f'<div class="feature-desc">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

st.markdown('<div class="section-title">🛠️ Tech Stack</div>', unsafe_allow_html=True)
techs = [
    ("🐍", "Python 3.11+", "Core language"),
    ("⚡", "Streamlit", "UI framework"),
    ("🤖", "LangChain / Gemini", "Agent orchestration & LLM"),
    ("📊", "Pandas / Plotly", "Data analysis & visualization"),
    ("🧪", "Pytest", "Testing framework"),
]
cols = st.columns(len(techs))
for i, (icon, name, desc) in enumerate(techs):
    with cols[i]:
        st.markdown(
            f'<div style="text-align:center; padding:0.8rem;">'
            f'<div style="font-size:1.5rem;">{icon}</div>'
            f'<div style="font-size:0.85rem; font-weight:600; color:#F1F5F9; margin-top:0.2rem;">{name}</div>'
            f'<div style="font-size:0.72rem; color:#64748B;">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

if st.button("🚀 Launch AI Workforce Intelligence", use_container_width=True, type="primary"):
    st.session_state.page = "dashboard"
    st.rerun()

st.caption("No API keys required \u2014 runs in Enterprise Demo Environment mode")

st.markdown(
    '<div class="footer">'
    'AI Workforce Intelligence Platform \u2022 Built with Streamlit \u2022 '
    '<a href="https://github.com/kristlingr/ai-workforce-intelligence-platform" '
    'style="color:#60A5FA;">GitHub</a>'
    '</div>',
    unsafe_allow_html=True
)
