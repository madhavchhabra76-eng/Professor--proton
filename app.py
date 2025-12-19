import streamlit as st
from groq import Groq

# -----------------------------------------------------------
# PROFESSOR PROTON - HIGH SPEED BUILD (GROQ)
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️")

# 1. SETUP AI CLIENT
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Error: API Key is missing. Please update Secrets.")
    st.stop()

# 2. UI SETUP (Custom Branding)
st.title("👨‍🏫 Professor Proton")
st.caption("Your Personal AI Science Tutor") 
# ^^^ No "Powered by" text here. Clean and professional.

st.sidebar.header("Configuration")
selected_class = st.sidebar.selectbox("Class", [6, 7, 8, 9, 10])
language = st.sidebar.radio("Language", ["English", "Punjabi"])

if st.sidebar.button("Clear Chat"):
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
            
            # Using Llama 3 (Fastest Model)
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192", 
            )
            
            final_response = chat_completion.choices[0].message.content
            
        except Exception as e:
            final_response = f"System Error: {str(e)}"

    # Show Answer
    st.session_state.messages.append({"role": "assistant", "text": final_response})
    with st.chat_message("assistant"):
        st.write(final_response)
