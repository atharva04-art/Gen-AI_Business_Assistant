import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="GenAI Business Assistant", page_icon="🚀", layout="centered")
st.title("🚀 Smart GenAI Business Assistant")
st.caption("Built with Groq • Prompt Engineering + Multi-mode LLM Workflows")

# Show current mode prominently
st.markdown(f"**Current Mode:** `{st.session_state.get('mode', 'Customer Support')}`")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# System prompts
system_prompts = {
    "Customer Support": "You are a friendly, professional, and empathetic customer support agent. Be clear, solution-oriented, and helpful. If you don't know something, say so politely and suggest next steps.",
    "Content Creation": "You are a creative marketing content writer. Produce engaging, concise, and brand-friendly content. Structure responses with headline, body, and relevant calls-to-action or hashtags when suitable.",
    "Brainstorming": "You are an innovative business strategist and idea generator. Provide creative, practical ideas. Think step by step and give multiple options with pros/cons where helpful."
}

# Sidebar
with st.sidebar:
    mode = st.selectbox(
        "Select Mode", 
        ["Customer Support", "Content Creation", "Brainstorming"]
    )
    # Save current mode
    st.session_state.mode = mode
    
    model_name = st.selectbox(
        "Groq Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mistral-8x7b-32768"]
    )
    
    temperature = st.slider("Temperature (Creativity)", 0.0, 1.0, 0.7, 0.1)
    
    structured_output = st.checkbox("Enable Structured JSON Output", value=False)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Regenerate"):
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
                st.session_state.messages.pop()
                st.session_state.regenerate_flag = True
                st.rerun()
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    if st.button("📥 Export Chat"):
        if st.session_state.messages:
            chat_text = "\n\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in st.session_state.messages])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="Download Chat as TXT",
                data=chat_text,
                file_name=f"genai_chat_{timestamp}.txt",
                mime="text/plain"
            )

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Normal user input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.regenerate_flag = False
    
    with st.chat_message("user"):
        st.markdown(prompt)

    current_system = system_prompts.get(mode, "You are a helpful AI assistant.")
    if structured_output:
        current_system += "\n\nAlways respond ONLY in valid JSON with keys: 'answer' and 'suggestion'."

    messages = [{"role": "system", "content": current_system}]
    for msg in st.session_state.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})

    with st.chat_message("assistant"):
        with st.spinner("Thinking with Groq..."):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=900
                )
                assistant_reply = response.choices[0].message.content.strip()

                if structured_output:
                    try:
                        json_data = json.loads(assistant_reply)
                        st.json(json_data)
                        assistant_reply = json.dumps(json_data, indent=2)
                    except:
                        st.markdown(assistant_reply)
                else:
                    st.markdown(assistant_reply)

            except Exception as e:
                error_msg = str(e)
                st.error(f"Groq API Error: {error_msg}")
                assistant_reply = f"Error: {error_msg[:200]}"

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

# Regenerate Logic
if st.session_state.get("regenerate_flag", False):
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        prompt = st.session_state.messages[-1]["content"]

        current_system = system_prompts.get(mode, "You are a helpful AI assistant.")
        if structured_output:
            current_system += "\n\nAlways respond ONLY in valid JSON with keys: 'answer' and 'suggestion'."

        messages = [{"role": "system", "content": current_system}]
        for msg in st.session_state.messages:
            messages.append({"role": msg["role"], "content": msg["content"]})

        with st.chat_message("assistant"):
            with st.spinner("Regenerating with Groq..."):
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=900
                    )
                    assistant_reply = response.choices[0].message.content.strip()

                    if structured_output:
                        try:
                            json_data = json.loads(assistant_reply)
                            st.json(json_data)
                            assistant_reply = json.dumps(json_data, indent=2)
                        except:
                            st.markdown(assistant_reply)
                    else:
                        st.markdown(assistant_reply)

                except Exception as e:
                    error_msg = str(e)
                    st.error(f"Groq API Error: {error_msg}")
                    assistant_reply = f"Error: {error_msg[:200]}"

        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        st.session_state.regenerate_flag = False

# Footer
st.markdown("---")
st.markdown("Smart GenAI Business Assistant")