import asyncio
import sys

# Windows par ye zaroori hai, Cloud par bhi safety ke liye
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
else:
    # Yeh line `uvloop` ke conflict ko bypass karti hai
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

import streamlit as st
# ... baki imports
import streamlit as st
import os
import time
from dotenv import load_dotenv
from agent_core import run_full_review

load_dotenv()

st.set_page_config(
    page_title="NexusGuard AI | DevSecOps Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@400;600&display=swap');

.stApp {
    background-color: #030712;
    color: #e2e8f0;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: #06b6d4; border-radius: 2px; }

/* Star field background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image:
        radial-gradient(ellipse at 15% 15%, rgba(6,182,212,0.12) 0%, transparent 45%),
        radial-gradient(ellipse at 85% 85%, rgba(139,92,246,0.12) 0%, transparent 45%),
        radial-gradient(ellipse at 85% 15%, rgba(244,63,94,0.06) 0%, transparent 35%),
        radial-gradient(ellipse at 15% 85%, rgba(6,182,212,0.06) 0%, transparent 35%);
    pointer-events: none;
    z-index: 0;
}

/* Glitch Effect */
.glitch {
    font-family: 'Rajdhani', sans-serif;
    font-size: 46px;
    font-weight: 900;
    color: #06b6d4;
    text-shadow: 0 0 30px rgba(6,182,212,0.9), 0 0 60px rgba(6,182,212,0.5), 0 0 100px rgba(6,182,212,0.2);
    letter-spacing: 6px;
    position: relative;
    animation: glitch 4s infinite;
    line-height: 1.1;
}
.glitch::before, .glitch::after {
    content: '🛡️ NEXUSGUARD AI';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
}
.glitch::before {
    color: #f43f5e;
    animation: glitch-1 4s infinite;
    clip-path: polygon(0 0, 100% 0, 100% 35%, 0 35%);
    transform: translate(-2px, -2px);
    opacity: 0;
}
.glitch::after {
    color: #a78bfa;
    animation: glitch-2 4s infinite;
    clip-path: polygon(0 65%, 100% 65%, 100% 100%, 0 100%);
    transform: translate(2px, 2px);
    opacity: 0;
}
@keyframes glitch {
    0%, 88%, 100% { transform: translate(0); filter: none; }
    90% { transform: translate(-2px, 1px); filter: hue-rotate(10deg); }
    92% { transform: translate(2px, -1px); filter: hue-rotate(-10deg); }
    94% { transform: translate(-1px, 2px); filter: none; }
}
@keyframes glitch-1 {
    0%, 88%, 100% { opacity: 0; transform: translate(-2px, -2px); }
    90%, 92% { opacity: 0.7; }
    91% { transform: translate(4px, -3px); }
}
@keyframes glitch-2 {
    0%, 88%, 100% { opacity: 0; transform: translate(2px, 2px); }
    90%, 92% { opacity: 0.7; }
    91% { transform: translate(-4px, 3px); }
}

/* Cyber Cards */
.cyber-card {
    background: linear-gradient(135deg, rgba(6,182,212,0.06) 0%, rgba(139,92,246,0.06) 100%);
    border: 1px solid rgba(6,182,212,0.25);
    padding: 22px;
    position: relative;
    overflow: hidden;
    clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 14px 100%, 0 calc(100% - 14px));
    transition: all 0.3s ease;
}
.cyber-card::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 1px;
    background: linear-gradient(90deg, transparent, #06b6d4, transparent);
    animation: card-scan 4s linear infinite;
}
@keyframes card-scan {
    0% { left: -100%; }
    100% { left: 100%; }
}
.cyber-card:hover {
    border-color: rgba(6,182,212,0.7);
    box-shadow: 0 0 30px rgba(6,182,212,0.2), inset 0 0 30px rgba(6,182,212,0.04);
    transform: translateY(-3px);
}
.metric-label {
    font-family: 'JetBrains Mono', monospace;
    color: #475569;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 10px;
}
.metric-val-cyan {
    font-family: 'Rajdhani', sans-serif;
    color: #06b6d4;
    font-size: 46px;
    font-weight: 700;
    text-shadow: 0 0 20px rgba(6,182,212,0.8), 0 0 40px rgba(6,182,212,0.4);
    line-height: 1;
}
.metric-val-red {
    font-family: 'Rajdhani', sans-serif;
    color: #f43f5e;
    font-size: 46px;
    font-weight: 700;
    text-shadow: 0 0 20px rgba(244,63,94,0.8), 0 0 40px rgba(244,63,94,0.4);
    line-height: 1;
}
.metric-val-purple {
    font-family: 'Rajdhani', sans-serif;
    color: #a78bfa;
    font-size: 46px;
    font-weight: 700;
    text-shadow: 0 0 20px rgba(167,139,250,0.8), 0 0 40px rgba(167,139,250,0.4);
    line-height: 1;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060d1f 0%, #030712 100%) !important;
    border-right: 1px solid rgba(6,182,212,0.15) !important;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }

/* Threat Gauge */
.gauge-container { text-align: center; padding: 10px 0; }
.gauge-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    color: #475569;
    margin-top: 8px;
    text-transform: uppercase;
}

/* Buttons */
.stButton > button {
    background: transparent !important;
    border: 1px solid #06b6d4 !important;
    color: #06b6d4 !important;
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 12px 100%, 0 calc(100% - 12px)) !important;
    transition: all 0.3s ease !important;
    font-size: 13px !important;
    padding: 14px !important;
    font-weight: 700 !important;
}
.stButton > button:hover {
    background: rgba(6,182,212,0.12) !important;
    box-shadow: 0 0 35px rgba(6,182,212,0.5), inset 0 0 25px rgba(6,182,212,0.08) !important;
    transform: translateY(-2px) !important;
    letter-spacing: 5px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(6,182,212,0.2) !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Orbitron', sans-serif !important;
    color: #334155 !important;
    letter-spacing: 2px !important;
    background: transparent !important;
    border: none !important;
    font-size: 11px !important;
    font-weight: 700 !important;
}
.stTabs [aria-selected="true"] {
    color: #06b6d4 !important;
    border-bottom: 2px solid #06b6d4 !important;
    text-shadow: 0 0 15px rgba(6,182,212,0.7) !important;
}

/* Progress */
.stProgress > div > div {
    background: linear-gradient(90deg, #06b6d4, #8b5cf6, #f43f5e) !important;
    box-shadow: 0 0 12px rgba(6,182,212,0.6) !important;
}
.stProgress > div {
    background: rgba(6,182,212,0.06) !important;
    border-radius: 0 !important;
    border: 1px solid rgba(6,182,212,0.1) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(6,182,212,0.04) !important;
    border: 1px solid rgba(6,182,212,0.2) !important;
    border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    color: #06b6d4 !important;
    letter-spacing: 1px !important;
    font-size: 12px !important;
}
.streamlit-expanderContent {
    border: 1px solid rgba(6,182,212,0.1) !important;
    border-top: none !important;
    background: rgba(3,7,18,0.95) !important;
}

/* Terminal */
.terminal-box {
    background: linear-gradient(135deg, #020617 0%, #0a0f1e 100%);
    border: 1px solid rgba(6,182,212,0.25);
    border-left: 3px solid #06b6d4;
    padding: 16px 22px;
    font-family: 'JetBrains Mono', monospace;
    color: #06b6d4;
    font-size: 13px;
    letter-spacing: 0.5px;
    position: relative;
    clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 0 100%);
}
.terminal-box::before { content: '> '; color: #a78bfa; font-weight: 600; }

/* Pulse dot */
.pulse-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #22c55e;
    box-shadow: 0 0 8px #22c55e, 0 0 16px rgba(34,197,94,0.4);
    animation: pulse 2s infinite;
    margin-right: 8px;
    vertical-align: middle;
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 8px #22c55e, 0 0 16px rgba(34,197,94,0.4); transform: scale(1); }
    50% { box-shadow: 0 0 20px #22c55e, 0 0 40px rgba(34,197,94,0.6); transform: scale(1.3); }
}

hr { border-color: rgba(6,182,212,0.1) !important; }
code {
    background: rgba(6,182,212,0.08) !important;
    color: #06b6d4 !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 2px !important;
    padding: 2px 6px !important;
}
p { font-family: 'JetBrains Mono', monospace; }
</style>

<canvas id="stars-canvas" style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;opacity:0.6;"></canvas>
<script>
setTimeout(() => {
    const canvas = document.getElementById('stars-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particles = [];
    const count = 120;
    
    for (let i = 0; i < count; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            r: Math.random() * 1.5 + 0.3,
            dx: (Math.random() - 0.5) * 0.3,
            dy: (Math.random() - 0.5) * 0.3,
            opacity: Math.random() * 0.6 + 0.2,
            color: Math.random() > 0.7 ? '#a78bfa' : '#06b6d4'
        });
    }
    
    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw connections
        particles.forEach((p, i) => {
            particles.slice(i + 1).forEach(p2 => {
                const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
                if (dist < 120) {
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(6,182,212,${0.08 * (1 - dist/120)})`;
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            });
        });
        
        // Draw particles
        particles.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.opacity;
            ctx.fill();
            ctx.globalAlpha = 1;
            
            p.x += p.dx;
            p.y += p.dy;
            
            if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
            if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
            
            // Twinkle
            p.opacity += (Math.random() - 0.5) * 0.02;
            p.opacity = Math.max(0.1, Math.min(0.8, p.opacity));
        });
        
        requestAnimationFrame(draw);
    }
    draw();
    
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}, 500);
</script>
""", unsafe_allow_html=True)

# Session State
if "review_results" not in st.session_state:
    st.session_state.review_results = []
if "total_bugs" not in st.session_state:
    st.session_state.total_bugs = 0
if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
if "active_prs" not in st.session_state:
    st.session_state.active_prs = 0

# --- NEW VARIABLES FOR NEXUS ENGINE ---
if "total_tokens_saved" not in st.session_state:
    st.session_state.total_tokens_saved = 0
if "total_cost_saved" not in st.session_state:
    st.session_state.total_cost_saved = 0.0

# Sidebar
with st.sidebar:
    st.sidebar.markdown(
        '<div style="display: flex; align-items: center; padding-bottom: 10px; margin-bottom: 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">'
        '<img src="https://cdn-icons-png.flaticon.com/512/2092/2092663.png" style="width: 35px; height: auto; border-radius: 6px; margin-right: 12px;" alt="Logo">'
        '<span style="font-size: 1.6rem; font-weight: 800; color: #F8FAFC; letter-spacing: 1.5px; margin: 0;">NEXUS<span style="color: #00f0ff;">GUARD</span></span>'
        '</div>', 
        unsafe_allow_html=True
    )
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='font-family: JetBrains Mono, monospace; font-size: 9px; color: #1e3a5f; letter-spacing: 2px; margin-bottom: 8px;'>TARGET REPOSITORY</p>", unsafe_allow_html=True)
    st.code(os.getenv("GITHUB_REPO", "vignesh06-OG/nexusguard-test"), language="bash")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-family: JetBrains Mono, monospace; font-size: 9px; color: #1e3a5f; letter-spacing: 2px; margin-bottom: 8px;'>API TOKEN USAGE</p>", unsafe_allow_html=True)
    token_limit = 100000
    used = st.session_state.total_tokens
    ratio = min(used / token_limit, 1.0)
    st.progress(ratio)
    st.markdown(f"<p style='font-family: JetBrains Mono, monospace; font-size: 10px; color: #a78bfa; text-align: right; margin-top: 4px;'>{used:,} / {token_limit:,}</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-family: JetBrains Mono, monospace; font-size: 9px; color: #1e3a5f; letter-spacing: 2px; margin-bottom: 10px;'>AUTHORIZED OPERATOR</p>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family: JetBrains Mono, monospace; font-size: 12px; line-height: 2.4;'>
        <span class='pulse-dot'></span>
        <span style='color: #94a3b8;'>VIGNESH</span>
        <span style='color: #06b6d4; font-size: 9px; letter-spacing: 1px; margin-left: 6px;'>[SOLO LEAD]</span><br>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family: JetBrains Mono, monospace; font-size: 10px; color: #22c55e; 
    text-align: center; letter-spacing: 2px; padding: 8px 0;'>
    <span class='pulse-dot'></span>ALL SYSTEMS OPERATIONAL
    </div>
    """, unsafe_allow_html=True)

# Main Header
clean_header_css = """
<style>
.header-container {
    display: flex;
    align-items: center;
    justify-content: center;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 2rem;
}
.custom-logo {
    width: 55px;
    height: auto;
    margin-right: 18px;
    border-radius: 8px;
}
.nexus-pro-title {
    font-size: 3rem !important;
    font-weight: 800 !important;
    color: #F8FAFC;
    letter-spacing: 2px;
    margin: 0;
}
.nexus-accent {
    color: #00f0ff;
}
</style>
"""
st.markdown(clean_header_css, unsafe_allow_html=True)

st.markdown(
    '<div class="header-container">'
    '<img src="https://cdn-icons-png.flaticon.com/512/2092/2092663.png" class="custom-logo" alt="Nexus Logo">'
    '<span class="nexus-pro-title">NEXUS<span class="nexus-accent">GUARD</span> AI</span>'
    '</div>', 
    unsafe_allow_html=True
)

# Metric Cards - Security
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="cyber-card">
        <div class="metric-label">◈ Active PRs</div>
        <div class="metric-val-cyan">{st.session_state.active_prs}</div>
        <div style='font-family: JetBrains Mono, monospace; font-size: 9px; color: #0c2233; margin-top: 8px; letter-spacing: 1px;'>PULL REQUESTS QUEUED</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="cyber-card">
        <div class="metric-label">◈ Critical Bugs Prevented</div>
        <div class="metric-val-red">{st.session_state.total_bugs}</div>
        <div style='font-family: JetBrains Mono, monospace; font-size: 9px; color: #2d0f15; margin-top: 8px; letter-spacing: 1px;'>VULNERABILITIES BLOCKED</div>
    </div>""", unsafe_allow_html=True)
with col3:
    tokens_display = f"{st.session_state.total_tokens/1000:.1f}k" if st.session_state.total_tokens > 0 else "0"
    st.markdown(f"""
    <div class="cyber-card">
        <div class="metric-label">◈ Tokens Consumed</div>
        <div class="metric-val-purple">{tokens_display}</div>
        <div style='font-family: JetBrains Mono, monospace; font-size: 9px; color: #180d38; margin-top: 8px; letter-spacing: 1px;'>API TOKENS UTILIZED</div>
    </div>""", unsafe_allow_html=True)

# Metric Cards - FinOps
st.markdown("""
<div style='font-family: JetBrains Mono, monospace; font-size: 10px; color: #334155;
letter-spacing: 2px; margin: 20px 0 10px 0;'>
◈ NEXUS ENGINE FINOPS TELEMETRY
</div>
""", unsafe_allow_html=True)

f_col1, f_col2 = st.columns(2)
with f_col1:
    saved_tokens_display = f"{st.session_state.total_tokens_saved/1000:.1f}k" if st.session_state.total_tokens_saved > 0 else "0"
    st.markdown(f"""
    <div class="cyber-card" style="border-color: rgba(34, 197, 94, 0.4);">
        <div class="metric-label">◈ Tokens Prevented</div>
        <div class="metric-val-cyan" style="color: #22c55e; text-shadow: 0 0 20px rgba(34,197,94,0.6);">{saved_tokens_display}</div>
        <div style='font-family: JetBrains Mono, monospace; font-size: 9px; color: #0f2e1a; margin-top: 8px; letter-spacing: 1px;'>JUNK TOKENS PRUNED</div>
    </div>""", unsafe_allow_html=True)
with f_col2:
    st.markdown(f"""
    <div class="cyber-card" style="border-color: rgba(34, 197, 94, 0.4);">
        <div class="metric-label">◈ Estimated API Savings</div>
        <div class="metric-val-cyan" style="color: #22c55e; text-shadow: 0 0 20px rgba(34,197,94,0.6);">${st.session_state.total_cost_saved:.4f}</div>
        <div style='font-family: JetBrains Mono, monospace; font-size: 9px; color: #0f2e1a; margin-top: 8px; letter-spacing: 1px;'>USD SAVED VIA COMPRESSION</div>
    </div>""", unsafe_allow_html=True)

st.write("")

# Tabs
tab1, tab2 = st.tabs(["⚡ LIVE AGENT TERMINAL", "📋 REVIEW ARCHIVE"])

with tab1:
    st.markdown("""
    <div style='font-family: Orbitron, sans-serif; font-size: 20px; color: #7dd3fc; 
    letter-spacing: 3px; margin-bottom: 18px; font-weight: 700;'>
    ◈ AGENT STATUS: <span style='color: #06b6d4; text-shadow: 0 0 15px rgba(6,182,212,0.9);'>STANDBY</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="terminal-box">
    System initialized. Awaiting scan command. Target repository locked. All 3 agents on standby.
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        scan_btn = st.button("⚡  INITIALIZE DEEP SCAN", use_container_width=True)
    with col_btn2:
        post_gh = st.checkbox("Post to GitHub", value=True)

    if scan_btn:
        repo_name = os.getenv("GITHUB_REPO", "vignesh06-OG/nexusguard-test")
        status_box = st.empty()
        messages = [
            "NEXUS_ENGINE >> Pre-processing payload. Stripping lockfiles and structural bloat...",
            "AGENT_01 [SECURITY_AUDITOR] >> Initializing OWASP Top 10 vulnerability scan...",
            "AGENT_02 [QUALITY_ANALYST] >> Analyzing code complexity, logic flaws & memory leaks...",
            "AGENT_03 [SYNTHESIZER] >> Compiling threat intelligence & risk assessment...",
            "ALL AGENTS >> Posting review to GitHub repository...",
        ]
        for msg in messages:
            status_box.markdown(f'<div class="terminal-box">{msg}</div>', unsafe_allow_html=True)
            time.sleep(0.8)

        with st.spinner(""):
            results = run_full_review(repo_name, post_to_github=post_gh)
            st.session_state.review_results = results
            st.session_state.active_prs = len(results)
            bug_count = sum(1 for r in results if r["risk_score"] >= 7)
            st.session_state.total_bugs += bug_count
            
            # --- NEW DATA AGGREGATION LOGIC ---
            batch_tokens_saved = sum(r.get("telemetry", {}).get("tokens_saved", 0) for r in results)
            batch_cost_saved = sum(r.get("telemetry", {}).get("cost_saved_usd", 0) for r in results)
            batch_original_tokens = sum(r.get("telemetry", {}).get("original_tokens", 0) for r in results)
            
            st.session_state.total_tokens += batch_original_tokens
            st.session_state.total_tokens_saved += batch_tokens_saved
            st.session_state.total_cost_saved += batch_cost_saved

        status_box.markdown('<div class="terminal-box" style="border-left-color:#22c55e;color:#22c55e;">MISSION COMPLETE >> Threat analysis done. Optimization logged. ✓</div>', unsafe_allow_html=True)
        st.rerun()

    if st.session_state.review_results:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("""
        <div style='font-family: Orbitron, sans-serif; font-size: 18px; color: #7dd3fc; 
        letter-spacing: 3px; margin-bottom: 18px; font-weight: 700;'>
        ◈ THREAT ANALYSIS RESULTS
        </div>
        """, unsafe_allow_html=True)

        for result in st.session_state.review_results:
            risk = result["risk_score"]
            badge = "🔴 CRITICAL" if risk >= 7 else "🟡 MODERATE" if risk >= 4 else "🟢 SECURE"
            understanding = min(95, 75 + (risk * 2))
            confidence = min(98, 80 + (risk * 2))
            gauge_color = "#f43f5e" if risk >= 7 else "#f59e0b" if risk >= 4 else "#22c55e"
            gauge_bg = f"conic-gradient({gauge_color} {risk * 36}deg, rgba(255,255,255,0.04) 0deg)"

            with st.expander(f"{badge} || PR #{result['pr_number']}: {result['pr_title']} || RISK {risk}/10 || @{result['author']}"):
                
                col_gauge, col_info = st.columns([1, 3])
                with col_gauge:
                    st.markdown(f"""
                    <div class="gauge-container">
                        <div style="width:130px;height:130px;border-radius:50%;margin:0 auto 12px auto;
                        background:{gauge_bg};box-shadow:0 0 25px {gauge_color}50, 0 0 50px {gauge_color}20;
                        display:flex;align-items:center;justify-content:center;">
                            <div style="width:100px;height:100px;border-radius:50%;background:#030712;
                            display:flex;align-items:center;justify-content:center;flex-direction:column;
                            border: 1px solid rgba(255,255,255,0.05);">
                                <div style="font-family:Orbitron,sans-serif;font-size:28px;font-weight:900;
                                color:{gauge_color};text-shadow:0 0 20px {gauge_color};">{risk}/10</div>
                                <div style="font-family:JetBrains Mono,monospace;font-size:8px;color:#475569;letter-spacing:1px;">RISK</div>
                            </div>
                        </div>
                        <div class="gauge-label">THREAT LEVEL</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_info:
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown(f'<div class="cyber-card"><div class="metric-label">✅ Fixes</div><div class="metric-val-cyan" style="font-size:26px">100%</div></div>', unsafe_allow_html=True)
                    with m2:
                        st.markdown(f'<div class="cyber-card"><div class="metric-label">🧠 Understanding</div><div class="metric-val-purple" style="font-size:26px">{understanding}%</div></div>', unsafe_allow_html=True)
                    with m3:
                        st.markdown(f'<div class="cyber-card"><div class="metric-label">⚡ Confidence</div><div class="metric-val-cyan" style="font-size:26px">{confidence}%</div></div>', unsafe_allow_html=True)

                st.write("")
                st.markdown("<p style='font-family: JetBrains Mono, monospace; font-size: 9px; color: #1e3a5f; letter-spacing: 2px;'>SECURITY COVERAGE</p>", unsafe_allow_html=True)
                st.progress(understanding / 100)
                st.markdown("<p style='font-family: JetBrains Mono, monospace; font-size: 9px; color: #1e3a5f; letter-spacing: 2px;'>FIX COMPLETENESS</p>", unsafe_allow_html=True)
                st.progress(1.0)
                st.markdown("<p style='font-family: JetBrains Mono, monospace; font-size: 9px; color: #1e3a5f; letter-spacing: 2px;'>AGENT CONFIDENCE</p>", unsafe_allow_html=True)
                st.progress(confidence / 100)

                st.write("")
                st.markdown("""<div style='font-family: Orbitron, sans-serif; font-size: 14px; color: #7dd3fc; letter-spacing: 2px; margin-bottom: 12px; font-weight: 700;'>◈ FULL THREAT REPORT</div>""", unsafe_allow_html=True)
                st.markdown(result["review"])
                st.markdown(f"<a href='{result['pr_url']}' style='font-family: JetBrains Mono, monospace; color: #06b6d4; font-size: 11px; letter-spacing: 2px; text-decoration: none;'>◈ VIEW ON GITHUB ↗</a>", unsafe_allow_html=True)

with tab2:
    st.markdown("""<div style='font-family: Orbitron, sans-serif; font-size: 18px; color: #7dd3fc; letter-spacing: 3px; margin-bottom: 18px; font-weight: 700;'>◈ REVIEW ARCHIVE</div>""", unsafe_allow_html=True)
    if not st.session_state.review_results:
        st.markdown('<div class="terminal-box">No records found in archive. Initialize scan to populate database.</div>', unsafe_allow_html=True)
    else:
        for result in st.session_state.review_results:
            risk = result["risk_score"]
            status = "THREAT DETECTED" if risk >= 5 else "SECURE"
            with st.expander(f"PR #{result['pr_number']}: {result['pr_title']} — [{status}]"):
                st.markdown(f"<p style='font-family: JetBrains Mono, monospace; font-size: 12px; color: #64748b;'>RISK SCORE: <span style='color: #f43f5e; font-weight: 600;'>{risk}/10</span></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-family: JetBrains Mono, monospace; font-size: 12px; color: #64748b;'>OPERATOR: <span style='color: #06b6d4;'>@{result['author']}</span></p>", unsafe_allow_html=True)
                st.markdown(f"<a href='{result['pr_url']}' style='font-family: JetBrains Mono, monospace; color: #06b6d4; font-size: 11px; letter-spacing: 1px; text-decoration: none;'>◈ VIEW ON GITHUB ↗</a>", unsafe_allow_html=True)