import streamlit as st
import requests
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="MediPulse AI | Clinical Intelligence",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Elite Eye-Friendly Responsive CSS with Visible 3D Blood Vessel Animation ---
st.markdown("""
    <style>
        /* Hide Default Streamlit Elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Matte Obsidian Base Theme */
        .stApp {
            background: #040406 !important;
            color: #F4F4F5 !important;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }

        /* --- 3D Glowing Blood Vessel & Pulse Background Animation --- */
        .stApp::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: 
                radial-gradient(circle at 15% 25%, rgba(239, 68, 68, 0.12) 0%, transparent 50%),
                radial-gradient(circle at 85% 75%, rgba(59, 130, 246, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.05) 0%, transparent 60%);
            z-index: 0;
            pointer-events: none;
            animation: ambientGlow 8s ease-in-out infinite alternate;
        }

        @keyframes ambientGlow {
            0% { transform: scale(1); opacity: 0.8; }
            100% { transform: scale(1.05); opacity: 1; }
        }

        /* Prominent 3D Flowing Blood Vessel / Pulse Wave Animation */
        .stApp::after {
            content: "";
            position: fixed;
            bottom: 0;
            left: 0;
            width: 200vw;
            height: 220px;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 140" preserveAspectRatio="none"><path d="M0,30 C150,110 350,-20 500,50 C650,120 950,10 1200,70 L1200,140 L0,140 Z" fill="rgba(239, 68, 68, 0.07)"/><path d="M0,60 C200,10 400,130 600,60 C800,-10 1000,110 1200,40 L1200,140 L0,140 Z" fill="rgba(59, 130, 246, 0.04)"/></svg>') repeat-x;
            background-size: 50% 140px;
            animation: vesselFlow 12s linear infinite;
            z-index: 0;
            pointer-events: none;
        }

        @keyframes vesselFlow {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }

        /* Fix Streamlit Container Layering over Background */
        .main .block-container {
            position: relative;
            z-index: 2;
            max-width: 800px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        /* Fully Responsive Top Workspace Navbar */
        .workspace-header {
            background: rgba(12, 12, 16, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: clamp(10px, 2vw, 14px) clamp(16px, 3vw, 22px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
            width: 100%;
            box-sizing: border-box;
        }

        .header-brand {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .brand-icon {
            width: clamp(32px, 4vw, 38px);
            height: clamp(32px, 4vw, 38px);
            background: linear-gradient(135deg, #EF4444 0%, #3B82F6 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 14px rgba(239, 68, 68, 0.4);
        }

        .brand-text h2 {
            font-size: clamp(0.88rem, 2vw, 1rem);
            font-weight: 700;
            color: #FAFAFA;
            margin: 0;
            letter-spacing: -0.2px;
        }

        .brand-text p {
            font-size: clamp(0.65rem, 1.5vw, 0.72rem);
            color: #A1A1AA;
            margin: 0;
        }

        /* Red Pulsing LIVE Status Badge */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.35);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: clamp(0.68rem, 1.5vw, 0.75rem);
            color: #F87171;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .status-dot {
            width: 6px;
            height: 6px;
            background-color: #EF4444;
            border-radius: 50%;
            box-shadow: 0 0 8px #EF4444;
            animation: redPulse 1.5s infinite;
        }

        @keyframes redPulse {
            0% { transform: scale(0.9); opacity: 0.6; box-shadow: 0 0 2px #EF4444; }
            50% { transform: scale(1.35); opacity: 1; box-shadow: 0 0 10px #EF4444; }
            100% { transform: scale(0.9); opacity: 0.6; box-shadow: 0 0 2px #EF4444; }
        }

        /* Responsive Welcome Hero Card */
        .dashboard-welcome {
            background: linear-gradient(145deg, rgba(18, 18, 24, 0.85) 0%, rgba(8, 8, 12, 0.95) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: clamp(20px, 4vw, 28px) clamp(16px, 3vw, 24px);
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            margin-bottom: 16px;
        }

        .dashboard-welcome h1 {
            font-size: clamp(1.15rem, 3vw, 1.45rem);
            font-weight: 700;
            color: #FAFAFA;
            margin-bottom: 8px;
        }

        .dashboard-welcome p {
            font-size: clamp(0.8rem, 2vw, 0.88rem);
            color: #A1A1AA;
            max-width: 520px;
            margin: 0 auto;
            line-height: 1.5;
        }

        /* Suggestion Grid Buttons */
        div.stButton > button {
            width: 100% !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            background: #111115 !important;
            color: #D4D4D8 !important;
            padding: clamp(8px, 2vw, 12px) 14px !important;
            font-size: clamp(0.78rem, 1.8vw, 0.85rem) !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }

        div.stButton > button:hover {
            border-color: #EF4444 !important;
            background: rgba(239, 68, 68, 0.12) !important;
            color: #FFFFFF !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 14px rgba(239, 68, 68, 0.25);
        }

        /* Responsive Chat Message Bubbles */
        .stChatMessage[data-testid="stChatMessage-user"] {
            background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%) !important;
            border-radius: 14px 14px 4px 14px !important;
            padding: clamp(10px, 2vw, 14px) clamp(12px, 2.5vw, 18px);
            color: #FFFFFF !important;
            box-shadow: 0 4px 16px rgba(220, 38, 38, 0.3);
            max-width: 85%;
            margin-left: auto !important;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .stChatMessage[data-testid="stChatMessage-user"] p,
        .stChatMessage[data-testid="stChatMessage-user"] span {
            color: #FFFFFF !important;
            font-size: clamp(0.85rem, 2vw, 0.94rem) !important;
        }

        .stChatMessage[data-testid="stChatMessage-assistant"] {
            background: #0D0D11 !important;
            border-radius: 14px 14px 14px 4px !important;
            padding: clamp(12px, 2.5vw, 18px) !important;
            color: #F4F4F5 !important;
            border: 1px solid rgba(239, 68, 68, 0.25) !important;
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.6) !important;
            max-width: 90%;
            margin-right: auto !important;
        }
        
        .stChatMessage[data-testid="stChatMessage-assistant"] p,
        .stChatMessage[data-testid="stChatMessage-assistant"] li,
        .stChatMessage[data-testid="stChatMessage-assistant"] span {
            color: #E4E4E7 !important;
            font-size: clamp(0.85rem, 2vw, 0.94rem) !important;
            line-height: 1.6 !important;
        }

        /* --- Sleek Custom Chat Input Box --- */
        div[data-testid="stChatInputContainer"] {
            background: rgba(4, 4, 6, 0.9) !important;
            backdrop-filter: blur(12px);
            padding: 10px 0 16px 0 !important;
            width: 100% !important;
            max-width: 800px !important;
            margin: 0 auto !important;
        }

        div[data-testid="stChatInput"] {
            background-color: #0D0D11 !important;
            border-radius: 14px !important;
            border: 1px solid rgba(239, 68, 68, 0.4) !important;
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.7) !important;
            padding: 4px 10px !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stChatInput"]:focus-within {
            border-color: #EF4444 !important;
            box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.25), 0 8px 30px rgba(0, 0, 0, 0.9) !important;
        }

        div[data-testid="stChatInput"] textarea {
            color: #F4F4F5 !important;
            font-size: clamp(0.88rem, 2vw, 0.95rem) !important;
            background: transparent !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }

        div[data-testid="stChatInput"] textarea::placeholder {
            color: #71717A !important;
        }

        div[data-testid="stChatInput"] button {
            background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%) !important;
            border: none !important;
            border-radius: 10px !important;
            color: #FFFFFF !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stChatInput"] button:hover {
            opacity: 0.95 !important;
            transform: scale(1.06);
            box-shadow: 0 0 12px rgba(239, 68, 68, 0.5);
        }

        /* Professional Footer Section */
        .app-footer {
            text-align: center;
            padding: 20px 12px;
            font-size: clamp(0.7rem, 1.5vw, 0.78rem);
            color: #71717A;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            margin-top: 32px;
            line-height: 1.5;
        }
    </style>
""", unsafe_allow_html=True)

# --- Backend API Connection Configuration ---
BACKEND_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# --- Custom Image URLs ---
USER_AVATAR_URL = "https://img.icons8.com/?size=100&id=EllnQXZglUAE&format=png&color=000000"
DOCTOR_AI_AVATAR_URL = "https://img.icons8.com/?size=100&id=DHJCUP779OXh&format=png&color=000000"

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Main Workspace Navbar ---
st.markdown("""
    <div class="workspace-header">
        <div class="header-brand">
            <div class="brand-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M19.5 13.5C19.5 17.6421 16.1421 21 12 21C7.85786 21 4.5 17.6421 4.5 13.5C4.5 9.35786 7.85786 6 12 6" stroke="white" stroke-width="2" stroke-linecap="round"/>
                    <path d="M12 2V6" stroke="white" stroke-width="2" stroke-linecap="round"/>
                    <path d="M9 13.5H11L12.5 10.5L14 16.5L15.5 13.5H17.5" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="12" cy="2" r="1.5" fill="white"/>
                </svg>
            </div>
            <div class="brand-text">
                <h2>MediPulse AI</h2>
                <p>Clinical Intelligence Assistant</p>
            </div>
        </div>
        <div class="status-badge">
            <div class="status-dot"></div>
            <span>LIVE</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Welcome Dashboard ---
if len(st.session_state.messages) == 0:
    st.markdown("""
        <div class="dashboard-welcome">
            <h1>Clinical Intelligence at Your Fingertips</h1>
            <p>Query evidence-based medical protocols, diagnostic threshold ranges, and clinical guidelines instantly.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🩺 Explain HbA1c threshold ranges", use_container_width=True):
            st.session_state.pending_query = "Explain HbA1c threshold ranges"
            st.rerun()
        if st.button("🥗 Evidence-based diabetic nutrition", use_container_width=True):
            st.session_state.pending_query = "Give me some evidence-based diabetic nutrition tips"
            st.rerun()
    with col2:
        if st.button("❤️ Standard blood pressure guidelines", use_container_width=True):
            st.session_state.pending_query = "What are the standard blood pressure guidelines?"
            st.rerun()
        if st.button("🏃‍♂️ Hypertension lifestyle modifications", use_container_width=True):
            st.session_state.pending_query = "What lifestyle changes help manage hypertension?"
            st.rerun()

# --- Render Chat History ---
for message in st.session_state.messages:
    role = message["role"]
    if role == "user":
        with st.chat_message(role, avatar=USER_AVATAR_URL):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar=DOCTOR_AI_AVATAR_URL):
            st.markdown(message["content"])

# --- Handle Query Input & API Request with Spinner -> AI Avatar Transition ---
chat_input_query = st.chat_input("Consult MediPulse AI...")

query = None
if chat_input_query:
    query = chat_input_query
elif "pending_query" in st.session_state and st.session_state.pending_query:
    query = st.session_state.pending_query
    del st.session_state.pending_query

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar=USER_AVATAR_URL):
        st.markdown(query)

    payload_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]

    payload = {
        "query": query,
        "history": payload_history
    }

    try:
        # Step 1: Show Spinner while waiting for initial response connection/tokens
        with st.spinner("Synthesizing clinical insights..."):
            response = requests.post(f"{BACKEND_URL}/chat", json=payload, stream=True, timeout=60)

        if response.status_code == 200:
            # Step 2: Once connection is active, render with the AI Avatar and stream text chunk-by-chunk
            with st.chat_message("assistant", avatar=DOCTOR_AI_AVATAR_URL):
                def generate_stream():
                    for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
                        if chunk:
                            yield chunk

                answer = st.write_stream(generate_stream())
        else:
            answer = f"**System Notice:** Clinical gateway returned status code `{response.status_code}`."
            with st.chat_message("assistant", avatar=DOCTOR_AI_AVATAR_URL):
                st.markdown(answer)

    except requests.exceptions.ConnectionError:
        answer = f"**Connection Error:** Unable to reach the backend server at `{BACKEND_URL}/chat`."
        with st.chat_message("assistant", avatar=DOCTOR_AI_AVATAR_URL):
            st.error(answer)
    except requests.exceptions.Timeout:
        answer = "**Timeout Error:** The clinical request took too long to process. Please try again."
        with st.chat_message("assistant", avatar=DOCTOR_AI_AVATAR_URL):
            st.error(answer)
    except Exception as e:
        answer = f"**System Error:** {e}"
        with st.chat_message("assistant", avatar=DOCTOR_AI_AVATAR_URL):
            st.error(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()

# --- Professional Footer Section ---
st.markdown("""
    <div class="app-footer">
        <p>⚠️ <b>MediPulse AI</b> provides clinical decision support and is not a substitute for professional medical diagnosis.<br>
        © 2026 MediPulse AI. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)
