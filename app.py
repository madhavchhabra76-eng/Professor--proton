import streamlit as st
from groq import Groq
import time

# -----------------------------------------------------------
# PROFESSOR PROTON - STRUCTURED LEARNING EDITION 📝
# -----------------------------------------------------------

st.set_page_config(
    page_title="Professor Proton", 
    page_icon="⚛️", 
    layout="centered"
)

# --- 1. CSS FOR READABILITY ---
st.markdown("""
<style>
    /* Clean White Background */
    .stApp {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    header, footer {visibility: hidden;}
    
    /* Typography Fixes */
    h1 { color: #1a1a1a; font-family: 'Helvetica Neue', sans-serif; }
    
    /* FORCE BLACK TEXT & SPACING */
    p, li, .stMarkdown {
        color: #2c3e50 !important;
        font-family: 'Segoe UI', sans-serif;
        line-height: 1.7; /* More space between lines */
        font-size: 1.1em;
    }
    
    /* Math Equations Style */
    .katex { font-size: 1.2em; color: #d63031; }
    
    /* Chat Bubbles */
    .stChatMessage {
        background-color: white;
        border: 1px solid #e1e4e8;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. BACKEND ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("API Key Error. Check Secrets.")
    st.stop()

# --- 3. HEADER & SETTINGS ---
st.title("Professor Proton ⚛️")
st.markdown("<div style='text-align: center; color: #555; margin-bottom: 20px;'>Structured Syllabus Tutor</div>", unsafe_allow_html=True)

with st.expander("⚙️ Session Settings", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        selected_class = st.selectbox("Class Level", [6, 7, 8, 9, 10])
    with c2:
        language = st.radio("Language", ["English", "Punjabi"])
        
    if st.button("New Topic ⟳", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown("---")

# --- 4. CHAT ENGINE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    icon = "🧑‍🎓" if msg["role"] == "user" else "⚛️"
    with st.chat_message(msg["role"], avatar=icon):
        st.write(msg["text"])

# Input
user_input = st.chat_input("Enter a topic (e.g., Force, Photosynthesis)...")

if user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.write(user_input)

    # Response Generation
    with st.chat_message("assistant", avatar="⚛️"):
        placeholder = st.empty()
        full_response = ""
        
        # LOGIC: Force Structure
        if language == "English":
            lang_instruction = "Answer in clear English."
        else:
            lang_instruction = "Answer in Punjabi (Gurmukhi). Keep terms in English brackets."

        with st.spinner("Structuring answer..."):
            try:
                # --- THE STRUCTURED PROMPT ---
                prompt = f"""
                Act as a Science Teacher for Class {selected_class} (NCERT India).
                Topic: "{user_input}"
                
                STRICT FORMATTING RULES:
                1. CHECK SYLLABUS: If not in Class {selected_class}, refuse politely.
                2. NO PARAGRAPHS: Do not write big blocks of text.
                3. USE BULLET POINTS: Break down every explanation into points.
                4. MATH MODE: Write all formulas/equations on a separate line using LaTeX format. 
                   Example: $$ F = m \\times a $$
                
                OUTPUT STRUCTURE:
                **Definition:** (1 sentence)
                
                **Key Points:**
                * Point 1
                * Point 2
                
                **Formula/Equation:** (If applicable, else skip)
                $$ equation $$
                
                **Real World Example:** (1 sentence)
                
                LANGUAGE: {lang_instruction}
                """
                
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.2, # Strict adherence to format
                )
                
                response = completion.choices[0].message.content
                
                # Streaming
                for word in response.split():
                    full_response += word + " "
                    time.sleep(0.01)
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                
            except Exception as e:
                placeholder.error("Error generating response.")
                full_response = "Error"

    st.session_state.messages.append({"role": "assistant", "text": full_response})
