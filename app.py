import streamlit as st
from groq import Groq
import time

# -----------------------------------------------------------
# PROFESSOR PROTON - ACADEMIC EDITION 📚
# -----------------------------------------------------------

st.set_page_config(
    page_title="Professor Proton", 
    page_icon="⚛️", 
    layout="centered"
)

# --- 1. PROFESSIONAL CSS (Clean & Serious) ---
st.markdown("""
<style>
    /* Background - Clean Academic White/Grey */
    .stApp {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Header/Footer hidden */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Typography */
    h1 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #1a1a1a;
        font-weight: 700;
        text-align: center;
    }
    
    /* FORCE BLACK TEXT (Dark Mode Fix) */
    p, .stMarkdown, h1, h2, h3, li {
        color: #1a1a1a !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
    }
    
    /* Settings Box */
    [data-testid="stExpander"] {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Chat Bubbles - Academic Style */
    .stChatMessage {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    
    /* User Avatar Color */
    [data-testid="chatAvatarIcon-user"] {
        background-color: #2c3e50;
    }
    
    /* AI Avatar Color */
    [data-testid="chatAvatarIcon-assistant"] {
        background-color: #2980b9;
    }

</style>
""", unsafe_allow_html=True)

# --- 2. BACKEND ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("API Key Error. Check Secrets.")
    st.stop()

# --- 3. UI LAYOUT ---

st.title("Professor Proton ⚛️")
st.markdown("<div style='text-align: center; color: #555; margin-bottom: 20px; font-size: 0.9em;'>Advanced Syllabus Inference Engine</div>", unsafe_allow_html=True)

with st.expander("⚙️ Configure Session", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Target Class")
        selected_class = st.selectbox("Class", [6, 7, 8, 9, 10], label_visibility="collapsed")
    with c2:
        st.caption("Output Language")
        language = st.radio("Lang", ["English", "Punjabi"], label_visibility="collapsed")
        
    if st.button("Start New Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown("---")

# --- 4. INTELLIGENCE ENGINE ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# History
for msg in st.session_state.messages:
    icon = "🧑‍🎓" if msg["role"] == "user" else "⚛️"
    with st.chat_message(msg["role"], avatar=icon):
        st.write(msg["text"])

# Input
user_input = st.chat_input("Enter your scientific query...")

if user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.write(user_input)

    # Response Generation
    with st.chat_message("assistant", avatar="⚛️"):
        placeholder = st.empty()
        full_response = ""
        
        # LOGIC: STRICT vs DETAILED
        if language == "English":
            lang_instruction = "Answer in formal, academic English."
        else:
            lang_instruction = "Answer in Punjabi (Gurmukhi script). Keep technical terms in English brackets."

        with st.spinner("Retrieving detailed explanation..."):
            try:
                # --- THE BRAIN UPGRADE ---
                prompt = f"""
                Act as an expert Science Tutor for Class {selected_class} (NCERT Syllabus India).
                
                User Query: "{user_input}"
                
                INSTRUCTIONS:
                1. SYLLABUS CHECK: Verify if this topic exists in Class {selected_class} Science. 
                   - If NO: Refuse politely and suggest the correct class level.
                   - If YES: Proceed to step 2.
                
                2. EXPLANATION QUALITY:
                   - Provide a detailed, comprehensive answer.
                   - Start with a clear DEFINITION.
                   - Explain the MECHANISM (How it works).
                   - Provide a REAL-WORLD EXAMPLE.
                   - Use Bullet Points for key features.
                
                3. TONE:
                   - Professional, Academic, and Clear.
                   - NO EMOJIS. Avoid slang.
                
                4. LANGUAGE: {lang_instruction}
                """
                
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.1, # Low temp = More factual, less creative
                    max_tokens=1024  # Allow longer answers
                )
                
                response = completion.choices[0].message.content
                
                # Streaming
                for word in response.split():
                    full_response += word + " "
                    time.sleep(0.01) # Faster typing
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                
            except Exception as e:
                placeholder.error("System Error. Please refresh.")
                full_response = "Error"

    st.session_state.messages.append({"role": "assistant", "text": full_response})
