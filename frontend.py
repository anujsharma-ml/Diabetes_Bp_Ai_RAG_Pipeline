import streamlit as st
import requests

st.title("🩺 Medical Assistant Chatbot")


BACKEND_URL = "http://127.0.0.1:8000/chat"


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if query := st.chat_input("Ask your medical question here..."):
    
    
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
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
        
        with st.spinner("Thinking..."):
            response = requests.post(BACKEND_URL, json=payload)

        
        if response.status_code == 200:
            answer = response.json().get("answer")
        else:
            answer = f"Backend Error: {response.text}"

    except Exception as e:
        answer = f"Could not connect to FastAPI server. Make sure it's running! Error: {e}"

    
    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})