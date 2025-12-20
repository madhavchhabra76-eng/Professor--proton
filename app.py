import streamlit as st
from groq import Groq
import time

# -----------------------------------------------------------
# PROFESSOR PROTON - FORMATTING FIX 🛠️
# -----------------------------------------------------------

st.set_page_config(
    page_title="Professor Proton", 
    page_icon="⚛️", 
    layout="centered"
)

# --- 1. CSS (Force Line Breaks) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Force readable spacing */
    p, li {
        color: #1a1a1a !important;
        font-family: 'Segoe UI', sans-serif;
        line-height: 1.8 !important; /* Extra space between lines */
        margin-bottom: 12px !important; /* Space between paragraphs */
        font-size: 1.1em;
    }
    
    /* Bullet Points Spacing */
    ul {
        margin-top: 10px !important;
        margin-bottom: 10px !important;
    }
    
    /* Math Equations - Make them pop */
    .katex-display {
        margin: 20px 0 !important;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
        border-left: 3px solid #d63031;
    }
    
    /* Chat Bubbles */
    .stChatMessage {
        background-color: white;
        border: 1px solid #e1e4e8;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    
    /* Header/Footer hidden */
    header, footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- 2. BACKEND ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("API Key Error.")
    st.stop()

# --- 3. UI LAYOUT ---
st.title("Professor Proton ⚛️")
st.markdown("<div style='text-align: center; color: #555; margin-bottom: 20px;'>Structured Syllabus Tutor</div>", unsafe_allow_html=True)

with st.expander("⚙️ Settings", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        selected_class = st.selectbox("Class Level", [6, 7, 8, 9, 10])
    with c2:
        language = st.radio("Language", ["English", "Punjabi"])
    
    if st.button("Clear Chat", use_container_width=True):
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
user_input = st.chat_input("Enter topic (e.g., Photosynthesis)...")

if user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.write(user_input)

    with st.chat_message("assistant", avatar="⚛️"):
        placeholder = st.empty()
        full_response = ""
        
        # LOGIC
        lang_rule = "Answer in English." if language == "English" else "Answer in Punjabi (Gurmukhi)."

        with st.spinner("Structuring..."):
            try:
                # --- THE "ANTI-PARAGRAPH" PROMPT ---
                prompt = f"""
                Act as a Science Teacher for Class {selected_class} (NCERT India).
                Topic: "{user_input}"
                
                STRICT FORMATTING RULES (DO NOT IGNORE):
                1. DO NOT write big paragraphs. 
                2. USE MARKDOWN LISTS: Start every point with a dash "- " or asterisk "* ".
                3. NEW LINE FOR EVERY POINT: Put a blank line between every bullet point.
                4. FORMULAS: Write every formula on its own line using $$ ... $$.
                
                REQUIRED OUTPUT STRUCTURE:
                
                ### Definition
                (1 Clear Sentence)
                
                ### Key Points
                - Point 1 (Concept)
                
                - Point 2 (Mechanism)
                
                - Point 3 (Function)
                
                ### Formula
                (If valid, else write "N/A")
                $$ Formula $$
                
                ### Example
                (1 Real life example)
                
                LANGUAGE RULE: {lang_rule}
                """
                
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.1, 
                )
                
                response = completion.choices[0].message.content
                
                # Streaming
                for word in response.split():
                    full_response += word + " "
                    time.sleep(0.01)
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                
            except Exception as e:
                placeholder.error("Error.")
                full_response = "Error"

    st.session_state.messages.append({"role": "assistant", "text": full_response})
