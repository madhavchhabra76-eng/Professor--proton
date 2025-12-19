import streamlit as st
import google.generativeai as genai

# -----------------------------------------------------------
# PROFESSOR PROTON - SMART MODE (Debug Version)
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️")

# 1. SETUP GOOGLE AI
# I check if the key exists to prevent crashing
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Error: API Key is missing. Please check Streamlit Secrets.")
    st.stop()

# 2. UI SETUP
st.title("👨‍🏫 Professor Proton")
st.caption("Powered by Gemini Knowledge 🧠")

st.sidebar.header("Settings")
selected_class = st.sidebar.selectbox("Class", [6, 7, 8, 9, 10])
language = st.sidebar.radio("Language", ["English", "Punjabi"])

if st.sidebar.button("Clear History"):
    st.session_state.messages = []
    st.rerun()

# 3. CHAT LOGIC
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display old messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])

# User Input
user_input = st.chat_input("Ask any Science question...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # GENERATE ANSWER
    with st.spinner("Professor Proton is thinking..."):
        
        # This prompt forces the AI to check the syllabus virtually
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
            # THIS IS THE NEW PART: It will show us the real error code
            final_response = f"DEBUG ERROR: {str(e)}"

    # Show Answer
    st.session_state.messages.append({"role": "assistant", "text": final_response})
    with st.chat_message("assistant"):
        st.write(final_response)
