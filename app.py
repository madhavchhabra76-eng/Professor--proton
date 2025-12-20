import streamlit as st
from groq import Groq
import time

# -----------------------------------------------------------
# PROFESSOR PROTON - KID FRIENDLY EDITION 🎨
# -----------------------------------------------------------

st.set_page_config(
    page_title="Professor Proton", 
    page_icon="🧪", 
    layout="centered"
)

# --- 1. FUN CSS STYLING (Duolingo Style) ---
st.markdown("""
<style>
    /* Fun Background */
    .stApp {
        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
    }
    
    /* Hide standard header */
    header {visibility: hidden;}
    
    /* Title Styling - Big & Bubbly */
    h1 {
        font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif;
        color: #4a4e69;
        text-shadow: 2px 2px 0px #ffffff;
    }
    
    /* Chat Bubbles - Round & Friendly */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 20px;
        border: 2px solid #ffffff;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        padding: 15px;
        margin-bottom: 15px;
    }
    
    /* Sidebar - Clean White */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 3px solid #c9d6df;
    }
    
    /* Input Box - Pill Shape */
    .stTextInput input {
        border-radius: 25px;
        border: 2px solid #8ec5fc;
        padding: 10px;
    }
    
    /* Buttons */
    div.stButton > button {
        border-radius: 20px;
        background-color: #ff9a9e;
        color: white;
        border: none;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. BACKEND SETUP ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ Ask your teacher to check the API Key!")
    st.stop()

# --- 3. SIDEBAR (SIMPLE & CLEAN) ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/test-tube.png", width=100)
    st.title("Settings")
    
    st.markdown("### 🎓 Pick Your Class")
    selected_class = st.selectbox("Class Level", [6, 7, 8, 9, 10], label_visibility="collapsed")
    
    st.markdown("### 🗣️ Language")
    language = st.radio("Language", ["English", "Punjabi"], label_visibility="collapsed")
    
    st.markdown("---")
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 4. MAIN INTERFACE ---

# Fun Header
col1, col2 = st.columns([0.2, 0.8])
with col1:
    st.write("") # Spacer
with col2:
    st.title("Professor Proton 🧪")
    st.markdown("**Your AI Science Buddy!**")

st.markdown("---")

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    # Fun Avatars
    if msg["role"] == "user":
        avatar = "🎒" # Backpack for student
    else:
        avatar = "🤖" # Robot for Professor
        
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["text"])

# User Input
user_input = st.chat_input("Ask me anything about Science! 🚀")

if user_input:
    # 1. Show User Message
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user", avatar="🎒"):
        st.write(user_input)

    # 2. Generate AI Response
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        
        # --- STRICT LANGUAGE LOGIC (Hidden from UI) ---
        if language == "English":
            lang_instruction = "Answer strictly in English. Do not use any other language."
        else:
            lang_instruction = "Answer in Punjabi using Gurmukhi script."

        with st.spinner("Checking the Science book... 📖"):
            try:
                prompt = f"""
                Act as a friendly but educational Science teacher for Class {selected_class} (NCERT India).
                
                User Question: "{user_input}"
                
                INSTRUCTIONS:
                1. CHECK: Is this topic in the Class {selected_class} Science syllabus?
                2. IF NO: Say "Oops! That's not in our class syllabus yet!" politely.
                3. IF YES: Explain it simply and clearly.
                4. LANGUAGE RULE: {lang_instruction}
                
                FORMAT:
                - Use emojis to make it fun.
                - Use bullet points.
                - Keep it simple for a {selected_class}th grader.
                """
                
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.3
                )
                response_text = completion.choices[0].message.content
                
                # Typing Animation
                for chunk in response_text.split(" "):
                    full_response += chunk + " "
                    time.sleep(0.03) 
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                response_text = "⚠️ My brain is tired! Try again."
                message_placeholder.markdown(response_text)

    # Save to memory
    st.session_state.messages.append({"role": "assistant", "text": response_text})
