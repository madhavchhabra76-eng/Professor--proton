import streamlit as st
from groq import Groq
import time

# -----------------------------------------------------------
# PROFESSOR PROTON - PROFESSIONAL MOBILE EDITION 📱
# -----------------------------------------------------------

st.set_page_config(
    page_title="Professor Proton", 
    page_icon="⚛️", 
    layout="centered"
)

# --- 1. CSS STYLING (High Contrast & Professional) ---
st.markdown("""
<style>
    /* Background - Professional Soft Gradient */
    .stApp {
        background: linear-gradient(180deg, #f3f4f6 0%, #ffffff 100%);
    }
    
    /* Hide standard header/footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Title Styling - Clean & Modern */
    h1 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #1f2937;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0px;
    }
    
    /* Text Visibility Fix (Force Black Text) */
    p, .stMarkdown, h1, h2, h3 {
        color: #1f2937 !important;
    }
    
    /* Settings Box - Clean Card Style */
    [data-testid="stExpander"] {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        color: #000000 !important;
    }
    
    /* Fix text inside the expander specifically */
    .streamlit-expanderContent p {
        color: #000000 !important;
        text-align: left !important;
    }
    
    /* Dropdown/Input Styling */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #f9fafb;
        color: black;
        border-radius: 8px;
    }

    /* Chat Bubbles - Professional Alignment */
    .stChatMessage {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* User Bubble (Right Sideish feel) */
    [data-testid="chatAvatarIcon-user"] {
        background-color: #3b82f6;
    }
    
    /* Bot Bubble */
    [data-testid="chatAvatarIcon-assistant"] {
        background-color: #10b981;
    }

</style>
""", unsafe_allow_html=True)

# --- 2. BACKEND SETUP ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ API Key Error. Check Secrets.")
    st.stop()

# --- 3. UI LAYOUT ---

# Header
st.title("Professor Proton ⚛️")
st.markdown("<div style='text-align: center; color: #6b7280; margin-bottom: 20px;'>Syllabus-Aligned AI Tutor</div>", unsafe_allow_html=True)

# Settings (Expander)
with st.expander("⚙️ Configure Settings", expanded=True):
    # Using columns for better layout
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Select Class Level")
        selected_class = st.selectbox("Class", [6, 7, 8, 9, 10], label_visibility="collapsed")
    with c2:
        st.caption("Select Language")
        language = st.radio("Lang", ["English", "Punjabi"], label_visibility="collapsed")
        
    if st.button("Refresh Chat ⟳", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown("---")

# --- 4. CHAT ENGINE ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for msg in st.session_state.messages:
    icon = "🧑‍🎓" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=icon):
        st.write(msg["text"])

# Input
user_input = st.chat_input("Ask a question...")

if user_input:
    # 1. User Message
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.write(user_input)

    # 2. AI Logic
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""
        
        # Language Rule
        lang_rule = "Answer strictly in English." if language == "English" else "Answer in Punjabi (Gurmukhi)."

        with st.spinner("Thinking..."):
            try:
                # Prompt Engineering
                prompt = f"""
                Act as a Science teacher for Class {selected_class} (NCERT India).
                Question: "{user_input}"
                Rules:
                1. Check if valid for Class {selected_class} syllabus.
                2. If NO: Politely decline.
                3. If YES: Explain clearly.
                4. {lang_rule}
                Format: Use bullet points.
                """
                
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.3
                )
                
                # Streaming Effect
                response = completion.choices[0].message.content
                for word in response.split():
                    full_response += word + " "
                    time.sleep(0.02)
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                
            except Exception as e:
                placeholder.error("Connection Error. Please try again.")
                response = "Error"

    st.session_state.messages.append({"role": "assistant", "text": full_response})
