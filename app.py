import streamlit as st
import google.generativeai as genai

# -----------------------------------------------------------
# PROFESSOR PROTON - SMART MODE (v4)
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️")

# 1. SETUP GOOGLE AI
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Error: API Key is missing. Check Streamlit Secrets.")
    st.stop()

# 2. UI SETUP
st.title("👨‍🏫 Professor Proton")
st.caption("Now powered by Gemini Knowledge 🧠")

st.sidebar.header("Settings")
selected_class = st.sidebar.selectbox("Class", [6, 7, 8, 9, 10])
language = st.sidebar.radio("Language", ["English", "Punjabi"])

if st.sidebar.button("Clear History"):
    st.session_state.messages = []
    st.rerun()

# 3. CHAT LOGIC
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])

user_input = st.chat_input("Ask any Science question...")

if user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # GENERATE ANSWER
    with st.spinner("Professor Proton is thinking..."):
        
        # This is the "Smart Prompt" 
        # It allows the AI to use its own knowledge, but tells it to be strict.
        prompt = f"""
        Act as a strict Science teacher for Class {selected_class} in India (NCERT Syllabus).
        
        User Question: "{user_input}"
        
        INSTRUCTIONS:
        1. FIRST, check if this topic is actually in the Class {selected_class} Science syllabus.
        2. IF NOT in syllabus: Politely refuse. Say "This topic is not in the Class {selected_class} syllabus."
        3. IF YES: Explain it simply in {language}.
        4. If {language} is Punjabi, write in Gurmukhi script.
        """
        
        try:
            response = model.generate_content(prompt)
            final_response = response.text
        except Exception as e:
            final_response = "Error: Could not connect to Google AI."

    # Show Answer
    st.session_state.messages.append({"role": "assistant", "text": final_response})
    with st.chat_message("assistant"):
        st.write(final_response)
