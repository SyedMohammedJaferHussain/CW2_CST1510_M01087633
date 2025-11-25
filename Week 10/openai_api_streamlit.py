import streamlit as st
from openai import OpenAI

# initialise openai client
client = OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

st.subheader('CatGPT - Open AI API')

# Initialise session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
prompt = st.chat_input("Say Something")

if prompt:

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Send to OpenAI
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=st.session_state.messages,
        temperature=1,
        stream=True
    )


    # Display streaming assistant output
    with st.chat_message("assistant"):
        container = st.empty()
        full_reply = ""

        for chunk in completion:
            delta = chunk.choices[0].delta
            if delta.content:
                full_reply += delta.content
                container.markdown(full_reply)

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_reply})