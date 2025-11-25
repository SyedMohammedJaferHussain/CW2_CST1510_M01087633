import streamlit as st

st.title('Chat elements')

# 1. st.chat_input
# 2. st.chat_message

# define session state to sore historical information for a given session
if 'message' not in st.session_state:
    st.session_state.message = []



# to display the historical data
for message in st.session_state.message:
    with st.chat_message('user'):
        st.markdown(message)


prompt = st.chat_input('Hello, how can I help you today?')

if prompt:
    st.session_state.message.append(prompt)

    # this will execute if we recive some input 
    with st.chat_message('user'):
        st.markdown(prompt)

