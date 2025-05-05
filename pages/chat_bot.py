import streamlit as st
import openai
import os

# Set your OpenAI API key
client = openai.OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY")))

st.title("💬 ChatGPT Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Display previous messages
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input prompt
prompt = st.chat_input("Type your message...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call OpenAI chat endpoint using the v1 API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            chat_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages
            )
            msg = chat_response.choices[0].message.content
            st.markdown(msg)

    st.session_state.messages.append({"role": "assistant", "content": msg})
