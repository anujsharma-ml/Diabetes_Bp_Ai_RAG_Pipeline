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

# --- Elite Recruiter-Winning CSS (Compact Vercel / Linear Aesthetic) ---
st.markdown("""
    <style>
        /* Hide Default Streamlit Elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Matte Obsidian Vercel Theme */
        .stApp {
            background: #09090B;
            color: #F4F4F5;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }

        /* Compact Top Workspace Navbar */
        .workspace-header {
            background: rgba(17, 17, 19, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 12px 20px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }

        .header-brand {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .brand-icon {
            width: 34px;
            height: 34px;
            background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
            border-radius: 9px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.35);
        }

        .brand-text h2 {
            font-size: 0.95rem;
            font-weight: 700;
            color: #FAFAFA;
            margin: 0;
            letter-spacing: -0.2px;
        }

        .brand-text p {
            font-size: 0.7rem;
            color: #A1A1AA;
            margin: 0;
        }

        /* Live Status Badge */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.25);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.72rem;
            color: #34D399;
            font-weight: 500;
        }

        .status-dot {
            width: 5px;
            height: 5px;
            background-color: #34D399;
            border-radius: 50%;
            box-shadow: 0 0 6px #34D399;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 10px #34D399; }
            100% { transform: scale(0.95); opacity: 0.8; }
        }

        /* Compact Welcome Hero Card */
        .dashboard-welcome {
            background: linear-gradient(145deg, rgba(24, 24, 27, 0.7) 0%, rgba(17, 17, 19, 0.9) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 24px 20px;
            text-align: center;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.3);
            margin-bottom: 16px;
        }

        .dashboard-welcome h1 {
            font-size: 1.35rem;
            font-weight: 700;
            color: #FAFAFA;
            margin-bottom: 6px;
        }

        .dashboard-welcome p {
            font-size: 0.85rem;
            color: #A1A1AA;
            max-width: 500px;
            margin: 0 auto;
            line-height: 1.4;
        }

        /* Suggestion Grid Buttons */
        div.stButton > button {
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            background: #18181B !important;
            color: #D4D4D8 !important;
            padding: 10px 14px !important;
            font-size: 0.82rem !important;
            transition: all 0.2s ease !important;
        }

        div.stButton > button:hover {
            border-color: #8B5CF6 !important;
            background: rgba(139, 92, 246, 0.12) !important;
            color: #FFFFFF !important;
            transform: translateY(-1px);
        }

        /* Chat Message Bubbles */
        .stChatMessage[data-testid="stChatMessage-user"] {
            background: linear-gradient(135deg, #7C3AED 0%, #6366F1 100%) !important;
            border-radius: 12px 12px 4px 12px !important;
            padding: 12px 16px;
            color: #FFFFFF !important;
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2);
            max-width: 75%;
            margin-left: auto !important;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        
        .stChatMessage[data-testid="stChatMessage-user"] p,
        .stChatMessage[data-testid="stChatMessage-user"] span {
            color: #FFFFFF !important;
        }

        .stChatMessage[data-testid="stChatMessage-assistant"] {
            background: #121215 !important;
            border-radius: 12px 12px 12px 4px !important;
            padding: 16px !important;
            color: #F4F4F5 !important;
            border: 1px solid rgba(139, 92, 246, 0.25) !important;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
            max-width: 80%;
            margin-right: auto !important;
        }
        
        .stChatMessage[data-testid="stChatMessage-assistant"] p,
        .stChatMessage[data-testid="stChatMessage-assistant"] li,
        .stChatMessage[data-testid="stChatMessage-assistant"] span {
            color: #E4E4E7 !important;
            font-size: 0.92rem !important;
            line-height: 1.5 !important;
        }

        /* Chat Input Box Styling */
        div[data-testid="stChatInputContainer"] {
            background: #09090B !important;
            padding-bottom: 10px !important;
            max-width: 780px !important;
            margin: 0 auto !important;
        }

        div[data-testid="stChatInput"] {
            background-color: #121215 !important;
            border-radius: 12px !important;
            border: 1px solid rgba(139, 92, 246, 0.4) !important;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5) !important;
            padding: 2px 6px !important;
            transition: all 0.3s ease !important;
        }

        div[data-testid="stChatInput"]:focus-within {
            border-color: #8B5CF6 !important;
            box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.25), 0 6px 24px rgba(0, 0, 0, 0.7) !important;
        }

        div[data-testid="stChatInput"] textarea {
            color: #F4F4F5 !important;
            font-size: 0.92rem !important;
            background: transparent !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }

        div[data-testid="stChatInput"] textarea::placeholder {
            color: #71717A !important;
        }

        div[data-testid="stChatInput"] button {
            background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%) !important;
            border: none !important;
            border-radius: 8px !important;
            color: #FFFFFF !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stChatInput"] button:hover {
            opacity: 0.9 !important;
            transform: scale(1.05);
        }

        /* Professional Footer Section */
        .app-footer {
            text-align: center;
            padding: 16px 12px;
            font-size: 0.75rem;
            color: #71717A;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            margin-top: 30px;
            line-height: 1.4;
        }
    </style>
""", unsafe_allow_html=True)

# --- Backend API Connection Configuration ---
BACKEND_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# --- Custom Image URLs (Icons provided by user) ---
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
            <span>Online</span>
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