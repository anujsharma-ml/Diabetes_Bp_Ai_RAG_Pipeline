import streamlit as st
import requests
import os
from styles import CUSTOM_CSS, NAVBAR_HTML, WELCOME_HERO_HTML, FOOTER_HTML

# --- Page Configuration ---
st.set_page_config(
    page_title="MediPulse AI | Clinical Intelligence",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Apply Aesthetic CSS ---
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- Backend API Configuration ---
BACKEND_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# --- Custom Avatar Icons ---
USER_AVATAR_URL = "https://img.icons8.com/?size=100&id=EllnQXZglUAE&format=png&color=000000"
DOCTOR_AI_AVATAR_URL = "https://img.icons8.com/?size=100&id=DHJCUP779OXh&format=png&color=000000"

# --- Session Memory Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Header & Compact Dustbin Clear Icon Layout ---
col_nav, col_clear = st.columns([0.92, 0.08], vertical_alignment="center")
with col_nav:
    st.markdown(NAVBAR_HTML, unsafe_allow_html=True)
with col_clear:
    if st.button("🗑️", help="Clear chat history", use_container_width=False):
        st.session_state.messages = []
        st.rerun()

# --- Welcome Dashboard ---
if len(st.session_state.messages) == 0:
    st.markdown(WELCOME_HERO_HTML, unsafe_allow_html=True)
    
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

# --- Handle Query Input & API Request ---
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
        with st.spinner("Synthesizing clinical insights..."):
            response = requests.post(f"{BACKEND_URL}/chat", json=payload, stream=True, timeout=60)

        if response.status_code == 200:
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
        answer = f"**Connection Error:** Unable to reach backend server at `{BACKEND_URL}/chat`."
        with st.chat_message("assistant", avatar=DOCTOR_AI_AVATAR_URL):
            st.error(answer)
    except requests.exceptions.Timeout:
        answer = "**Timeout Error:** Request timed out. Please try again."
        with st.chat_message("assistant", avatar=DOCTOR_AI_AVATAR_URL):
            st.error(answer)
    except Exception as e:
        answer = f"**System Error:** {e}"
        with st.chat_message("assistant", avatar=DOCTOR_AI_AVATAR_URL):
            st.error(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()

# --- Render Footer ---
st.markdown(FOOTER_HTML, unsafe_allow_html=True)