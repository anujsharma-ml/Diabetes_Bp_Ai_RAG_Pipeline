import streamlit as st
import requests
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Medi-Pulse AI Assistant",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Premium Medical SaaS Appearance ---
st.markdown("""
    <style>
        /* Hide Streamlit Default Header, Footer, and Menu */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Rich Dark Medical Background System */
        .stApp {
            background: #07111F;
            color: #F8FAFC;
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        /* Sticky Glassmorphism Header */
        .header-container {
            position: sticky;
            top: 0;
            z-index: 999;
            background: rgba(11, 23, 38, 0.85);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            padding: 16px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 0 0 20px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            margin-bottom: 24px;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        /* SVG Medical AI Logo Badge */
        .logo-badge {
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #10B981 0%, #0284C7 100%);
            width: 46px;
            height: 46px;
            border-radius: 16px;
            box-shadow: 0 0 16px rgba(16, 185, 129, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }

        .header-title-wrapper h1 {
            font-size: 1.25rem !important;
            font-weight: 700 !important;
            color: #F8FAFC !important;
            margin: 0px !important;
            letter-spacing: -0.3px;
        }

        .header-title-wrapper p {
            color: #94A3B8;
            font-size: 0.8rem !important;
            margin: 0px !important;
            font-weight: 400 !important;
        }

        /* Professional Online Status Indicator */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            padding: 6px 14px;
            border-radius: 30px;
            font-size: 0.75rem;
            color: #10B981;
            font-weight: 500;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #10B981;
            border-radius: 50%;
            box-shadow: 0 0 8px #10B981;
            animation: pulse-glow 2s infinite;
        }

        @keyframes pulse-glow {
            0% { transform: scale(0.95); opacity: 0.8; }
            50% { transform: scale(1.15); opacity: 1; box-shadow: 0 0 12px #10B981; }
            100% { transform: scale(0.95); opacity: 0.8; }
        }

        /* Empty State Welcome Screen */
        .welcome-container {
            text-align: center;
            padding: 24px 20px 14px 20px;
            max-width: 600px;
            margin: 0 auto;
            background: rgba(16, 28, 45, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 24px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
        }

        .welcome-logo {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #10B981 0%, #38BDF8 100%);
            width: 64px;
            height: 64px;
            border-radius: 20px;
            box-shadow: 0 8px 24px rgba(16, 185, 129, 0.25);
            margin-bottom: 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .welcome-title {
            font-size: 1.6rem;
            font-weight: 700;
            color: #F8FAFC;
            margin-bottom: 8px;
        }

        .welcome-subtitle {
            font-size: 0.9rem;
            color: #94A3B8;
            line-height: 1.5;
            margin-bottom: 10px;
        }

        /* Curved Suggestion Buttons */
        div.stButton > button {
            border-radius: 16px !important;
            border: 1px solid rgba(56, 189, 248, 0.2) !important;
            background: rgba(16, 28, 45, 0.8) !important;
            color: #E2E8F0 !important;
            padding: 12px 16px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        }

        div.stButton > button:hover {
            border-color: #10B981 !important;
            background: rgba(16, 185, 129, 0.15) !important;
            color: #FFFFFF !important;
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.25) !important;
            transform: translateY(-2px);
        }

        /* General Chat Text Adjustments */
        .stMarkdown p, .stMarkdown {
            font-size: 1rem !important;
            line-height: 1.6 !important;
        }

        /* User Message Styling (Curved Right Bubble) */
        .stChatMessage[data-testid="stChatMessage-user"] {
            background: linear-gradient(135deg, #10B981 0%, #0284C7 100%) !important;
            border-radius: 20px 20px 4px 20px !important;
            padding: 14px 18px;
            color: #FFFFFF !important;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.15);
            max-width: 75%;
            margin-left: auto !important;
            margin-right: 0 !important;
            direction: ltr;
        }
        
        .stChatMessage[data-testid="stChatMessage-user"] p {
            color: #FFFFFF !important;
        }

        /* Assistant Message Styling (Curved Left Slate Card) */
        .stChatMessage[data-testid="stChatMessage-assistant"] {
            background: #101C2D !important;
            border-radius: 20px 20px 20px 4px !important;
            padding: 18px;
            color: #F8FAFC !important;
            border: 1px solid rgba(56, 189, 248, 0.25);
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
            max-width: 80%;
            margin-right: auto !important;
            margin-left: 0 !important;
        }
        
        .stChatMessage[data-testid="stChatMessage-assistant"] p {
            color: #F8FAFC !important;
            font-weight: 400;
        }

        /* Custom Medical Spinner Styling */
        .stSpinner > div {
            border-top-color: #10B981 !important;
        }

        /* High-Contrast Curved Chat Input Box & Removing Default Streamlit Lines */
        div[data-testid="stChatInputContainer"] {
            background-color: transparent !important;
            padding-bottom: 16px;
            max-width: 780px;
            margin: 0 auto;
            border: none !important;
        }

        div[data-testid="stChatInputContainer"] > div {
            border: none !important;
            box-shadow: none !important;
        }

        div[data-testid="stChatInput"] {
            border-radius: 24px !important;
            border: 1.5px solid rgba(16, 185, 129, 0.4) !important;
            background-color: #0B1726 !important;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.3s ease;
            padding: 4px 8px;
            outline: none !important;
        }

        div[data-testid="stChatInput"]:focus-within {
            border-color: #00F2FE !important;
            box-shadow: 0 0 22px rgba(0, 242, 254, 0.3) !important;
            outline: none !important;
        }

        div[data-testid="stChatInput"] textarea {
            color: #F8FAFC !important;
            font-size: 0.95rem !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }

        div[data-testid="stChatInput"] textarea::placeholder {
            color: #94A3B8 !important;
        }

        /* Professional Footer Section */
        .app-footer {
            text-align: center;
            padding: 24px 20px;
            font-size: 0.78rem;
            color: #94A3B8;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            margin-top: 50px;
            line-height: 1.5;
        }

        /* Responsive Fixes for Mobile */
        @media (max-width: 640px) {
            .stChatMessage[data-testid="stChatMessage-user"],
            .stChatMessage[data-testid="stChatMessage-assistant"] {
                max-width: 90%;
            }
        }
    </style>
""", unsafe_allow_html=True)

# --- Header Section with Custom Medical AI Logo & Status ---
st.markdown("""
    <div class="header-container">
        <div class="header-left">
            <div class="logo-badge">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2V22M2 12H22" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
                    <path d="M4 12H8L10 7L14 17L16 12H20" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <div class="header-title-wrapper">
                <h1>MEDI-PULSE AI</h1>
                <p>Intelligent Clinical Assistant</p>
            </div>
        </div>
        <div class="status-badge">
            <div class="status-dot"></div>
            <span>AI Online</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Backend API Connection Configuration ---
BACKEND_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# --- SVG Icons for Chat Avatars ---
USER_AVATAR_SVG = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2'></path><circle cx='12' cy='7' r='4'></circle></svg>"

# Premium Doctor AI Avatar with Medical Cross (Electric Cyan #00F2FE)
DOCTOR_AI_AVATAR_SVG = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2300F2FE' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M16 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2'/><circle cx='10' cy='7' r='4'/><path d='M19 8v6'/><path d='M16 11h6'/></svg>"

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Empty State Welcome Screen (Shown only when chat is empty) ---
if len(st.session_state.messages) == 0:
    st.markdown("""
        <div class="welcome-container">
            <div class="welcome-logo">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2V22M2 12H22" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
                </svg>
            </div>
            <div class="welcome-title">How can I help you today?</div>
            <div class="welcome-subtitle">
                Ask Medi-Pulse AI about diabetes, hypertension, medications, nutrition, lifestyle, or general clinical health information.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Fully interactive suggestion buttons using proper Streamlit logic
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🩺 Explain HbA1c ranges", use_container_width=True):
            st.session_state.pending_query = "Explain HbA1c ranges"
            st.rerun()
        if st.button("🥗 Diabetes-friendly diet tips", use_container_width=True):
            st.session_state.pending_query = "Give me some diabetes-friendly diet tips"
            st.rerun()
    with col2:
        if st.button("❤️ Blood pressure guidelines", use_container_width=True):
            st.session_state.pending_query = "What are the standard blood pressure guidelines?"
            st.rerun()
        if st.button("🏃‍♂️ Hypertension lifestyle habits", use_container_width=True):
            st.session_state.pending_query = "What lifestyle changes help manage hypertension?"
            st.rerun()

# --- Render Chat History with Custom Professional Avatars ---
for message in st.session_state.messages:
    role = message["role"]
    
    if role == "user":
        with st.chat_message(role, avatar=USER_AVATAR_SVG):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar=DOCTOR_AI_AVATAR_SVG):
            st.markdown(message["content"])

# --- Handle Query Processing (from Chat Input or Clickable Suggestion Buttons) ---
chat_input_query = st.chat_input("Ask Medi-Pulse AI a health question...")

# Check if a suggestion button was clicked or text was typed into the chat input
query = None
if chat_input_query:
    query = chat_input_query
elif "pending_query" in st.session_state and st.session_state.pending_query:
    query = st.session_state.pending_query
    del st.session_state.pending_query

if query:
    # 1. Append & Display User Message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar=USER_AVATAR_SVG):
        st.markdown(query)

    # 2. Prepare Payload matching your exact FastAPI contract
    payload_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]

    payload = {
        "query": query,
        "history": payload_history
    }

    # 3. Call FastAPI Backend endpoint: {BACKEND_URL}/chat via POST
    try:
        with st.spinner("Analyzing clinical data vectors..."):
            response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer") if isinstance(data, dict) else str(data)
            if not answer:
                answer = "Received an empty response structure from clinical server."
        else:
            answer = f"**System Notice:** Clinical gateway returned status code `{response.status_code}`."

    except requests.exceptions.ConnectionError:
        answer = f"**Connection Error:** Unable to reach the Medi-Pulse AI backend server at `{BACKEND_URL}/chat`. Please ensure FastAPI is running."
    except requests.exceptions.Timeout:
        answer = "**Timeout Error:** The clinical request took too long to process. Please try again."
    except Exception as e:
        answer = f"**System Error:** An unexpected error occurred while communicating with the server: {e}"

    # 4. Append & Display Assistant Response
    with st.chat_message("assistant", avatar=DOCTOR_AI_AVATAR_SVG):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()

# --- Footer Section ---
st.markdown("""
    <div class="app-footer">
        <p>⚠️ <b>Medi-Pulse AI</b> provides informational support and does not replace professional medical advice.<br>
        © 2026 Medi-Pulse AI. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)