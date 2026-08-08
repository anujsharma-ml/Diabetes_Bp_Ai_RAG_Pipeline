import streamlit as st
import requests
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="MediCare AI Assistant",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for Perfect Centered Input Box & Glassmorphism UI ---
st.markdown("""
    <style>
        /* Hide Streamlit Default Header, Footer, and Menu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Vibrant & Colorful Medical Background Gradient */
        .stApp {
            background: linear-gradient(135deg, #e0f7fa 0%, #e8f5e9 50%, #e3f2fd 100%);
            color: #0f172a;
        }

        /* Sticky Glassmorphism Header (Blur Effect when content goes behind it) */
        .header-container {
            position: sticky;
            top: 0;
            z-index: 999;
            background: rgba(224, 247, 250, 0.85);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 15px 0;
            border-bottom: 1px solid rgba(13, 148, 136, 0.2);
            text-align: center;
        }

        /* Super Large H1 Style Colorful Gradient Title */
        .main-title {
            font-size: 3.5rem !important;
            font-weight: 900 !important;
            background: linear-gradient(90deg, #0284c7, #0d9488, #16a34a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0px;
            letter-spacing: -1px;
            line-height: 1.2;
        }
        
        .sub-title {
            color: #334155;
            font-size: 1.1rem !important;
            margin-top: 5px;
            margin-bottom: 0px;
            font-weight: 600 !important;
        }

        /* Make All Chat Text Clear, Large, Bold & Black */
        .stMarkdown p, .stMarkdown {
            font-size: 1.15rem !important;
            line-height: 1.6 !important;
            color: #0f172a !important;
        }

        /* User Chat Box Styling - Vibrant Blue Gradient Card */
        .stChatMessage[data-testid="stChatMessage-user"] {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
            border-radius: 16px;
            padding: 15px;
            color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25);
            border: none;
        }
        
        .stChatMessage[data-testid="stChatMessage-user"] p {
            color: #ffffff !important;
        }

        /* Assistant Chat Box Styling - Clean White Card with Black Text */
        .stChatMessage[data-testid="stChatMessage-assistant"] {
            background: #ffffff !important;
            border-radius: 16px;
            padding: 15px;
            color: #000000 !important;
            border: 2px solid #ccfbf1;
            box-shadow: 0 4px 15px rgba(13, 148, 136, 0.1);
        }
        
        .stChatMessage[data-testid="stChatMessage-assistant"] p {
            color: #000000 !important;
            font-weight: 500;
        }

        /* --- PROPER FIX FOR INPUT BOX (Full Width & Clean Look) --- */
        section[data-testid="stBottom"] {
            background: transparent !important;
        }

        div[data-testid="stChatInputContainer"] {
            background-color: transparent !important;
            border: none !important;
            max-width: 100% !important;
        }

        div[data-testid="stChatInput"] textarea {
            background-color: #ffffff !important;
            color: #0f172a !important;
            font-size: 1.1rem !important;
            padding: 12px 18px !important;
        }

        div[data-testid="stChatInput"] {
            border-radius: 18px !important;
            border: 2.5px solid #0d9488 !important;
            background-color: #ffffff !important;
            box-shadow: 0 6px 25px rgba(13, 148, 136, 0.3) !important;
        }

        /* Custom Glowing Red Spinner */
        .stSpinner > div {
            border-top-color: #ef4444 !important;
            animation: spin 0.8s linear infinite;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sticky Glassmorphism Header Section ---
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">MEDI-PULSE AI</h1>
        <p class="sub-title">Advanced Intelligent Assistant for Diabetes & Hypertension Care</p>
    </div>
""", unsafe_allow_html=True)

BACKEND_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------printing the previous chat on the screen ---------


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input & Backend Integration ---
if query := st.chat_input("Type your medical question here..."):
    
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Prepare Payload
    payload_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]

    payload = {
        "query": query,
        "history": payload_history
    }

    try:
        # Spinner with Custom Red Glow Effect
        with st.spinner("Analyzing medical databases..."):
            response = requests.post(f"{BACKEND_URL}/chat", json=payload)

        if response.status_code == 200:
            answer = response.json().get("answer")
        else:
            answer = f"Backend Error: {response.text}"

    except Exception as e:
        answer = f"Could not connect to FastAPI server. Make sure it's running! Error: {e}"

    # Append Assistant Response
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})