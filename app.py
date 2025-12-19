import streamlit as st
import google.generativeai as genai

# -----------------------------------------------------------
# PROFESSOR PROTON - FINAL VERSION
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️")

# 1. SETUP GOOGLE AI
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # I changed this to the model we found in your Green List
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
else:
    st.error("Error: API Key is missing. Check Streamlit Secrets.")
    st.stop()

# 2. UI SETUP
st.title("👨‍🏫 Professor Proton")
st.caption("Powered by Gemini 2.0 Flash ⚡")

st.sidebar.header("Settings")
selected_class = st.sidebar.selectbox("Class", [6, 7, 8, 9, 10])
language = st.sidebar.radio("Language", ["English", "Punjabi"])

if st.sidebar.button("Clear History"):
    st.session_state.messages = []
    st.rerun()

# 3. CHAT LOGIC
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])

# Input
user_input = st.chat_input("Ask a Science question...")

if user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # GENERATE ANSWER
    with st.spinner("Thinking..."):
        try:
            # The "Strict Teacher" Prompt
            prompt = f"""
            Act as a strict Science teacher for Class {selected_class} (NCERT Syllabus India).
            
            User Question: "{user_input}"
            
            Rules:
            1. Check if the topic is in the Class {selected_class} syllabus.
            2. If NO: Refuse politely.
            3. If YES: Explain simply in {language}.
            4. If Punjabi: Use Gurmukhi script.
            """
            
            response = model.generate_content(prompt)
            final_response = response.text
            
        except Exception as e:
            final_response = f"Error: {str(e)}"

    # Show Answer
    st.session_state.messages.append({"role": "assistant", "text": final_response})
    with st.chat_message("assistant"):
        st.write(final_response)
