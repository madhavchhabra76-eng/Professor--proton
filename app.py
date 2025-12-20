import streamlit as st
from groq import Groq
import time

# -----------------------------------------------------------
# PROFESSOR PROTON - MOBILE READY EDITION 📱
# -----------------------------------------------------------

st.set_page_config(
    page_title="Professor Proton", 
    page_icon="🧪", 
    layout="centered"
)

# --- 1. FUN CSS STYLING (Mobile Optimized) ---
st.markdown("""
<style>
    /* Fun Background */
    .stApp {
        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
    }
    
    /* Hide standard header */
    header {visibility: hidden;}
    
    /* Title Styling */
    h1 {
        font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif;
        color: #4a4e69;
        text-shadow: 2px 2px 0px #ffffff;
        text-align: center;
    }
    
    /* Chat Bubbles */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        padding: 10px;
        margin-bottom: 10px;
    }
    
    /* Make the Settings Box stand out */
    [data-testid="stExpander"] {
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. BACKEND SETUP ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ Ask your teacher to check the API Key!")
    st.stop()

# --- 3. MAIN UI (No Sidebar needed) ---

# Title Section
st.title("Professor Proton 🧪")
st.markdown("<h4 style='text-align: center; color: #4a4e69;'>Your AI Science Buddy! 🤖</h4>", unsafe_allow_html=True)

# --- SETTINGS MOVED HERE (Always Visible) ---
with st.expander("⚙️ CLICK HERE to Change Class & Language", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎓 Class Level**")
        selected_class = st.selectbox("Select Class", [6, 7, 8, 9, 10], label_visibility="collapsed")
        
    with col2:
        st.markdown("**🗣️ Language**")
        language = st.radio("Select Language", ["English", "Punjabi"], label_visibility="collapsed")

    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown("---")

# --- 4. CHAT LOGIC ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        avatar = "🎒"
    else:
        avatar = "🤖" 
        
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
        
        # Language Logic
        if language == "English":
            lang_instruction = "Answer strictly in English. Do not use any other language."
        else:
            lang_instruction = "Answer in Punjabi using Gurmukhi script."

        with st.spinner("Thinking... ⚡"):
            try:
                prompt = f"""
                Act as a friendly Science teacher for Class {selected_class} (NCERT India).
                User Question: "{user_input}"
                INSTRUCTIONS:
                1. CHECK: Is this topic in Class {selected_class} syllabus?
                2. IF NO: Say "Oops! That's not in our class syllabus yet!"
                3. IF YES: Explain simply.
                4. LANGUAGE RULE: {lang_instruction}
                FORMAT: Use emojis and bullet points.
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
