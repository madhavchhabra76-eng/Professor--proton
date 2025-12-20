import streamlit as st
from groq import Groq
import time

# -----------------------------------------------------------
# PROFESSOR PROTON - CLEAN TEXT FIX 🧹
# -----------------------------------------------------------

st.set_page_config(
    page_title="Professor Proton", 
    page_icon="⚛️", 
    layout="centered"
)

# --- 1. CSS (Standard Size, No Giant Text) ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #f0f2f6 100%);
    }
    
    /* Reset text size to normal */
    p, li, div {
        color: #1f2937 !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 16px !important; /* Normal reading size */
        line-height: 1.6 !important;
    }
    
    /* Chat Bubbles */
    .stChatMessage {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. BACKEND ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("API Key Error.")
    st.stop()

# --- 3. UI HEADER ---
st.title("Professor Proton ⚛️")

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

# --- 4. CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    icon = "🧑‍🎓" if msg["role"] == "user" else "⚛️"
    with st.chat_message(msg["role"], avatar=icon):
        st.write(msg["text"])

# Input
user_input = st.chat_input("Enter topic...")

if user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.write(user_input)

    with st.chat_message("assistant", avatar="⚛️"):
        placeholder = st.empty()
        full_response = ""
        
        # LOGIC
        lang_rule = "Answer in English." if language == "English" else "Answer in Punjabi (Gurmukhi)."

        with st.spinner("Thinking..."):
            try:
                # --- PROMPT: NO HEADERS, JUST LABELS ---
                prompt = f"""
                Act as a Science Teacher for Class {selected_class} (NCERT India).
                Topic: "{user_input}"
                
                STRICT RULES:
                1. DO NOT use Markdown Headers (like ### or ##).
                2. ONLY use Bold Labels (like **Label:**).
                3. Keep it brief.
                
                OUTPUT FORMAT:
                
                **Definition:**
                (Write definition here)
                
                **Key Points:**
                - (Point 1)
                - (Point 2)
                
                **Formula:**
                $$ Formula $$ (or write None)
                
                **Example:**
                (Real life example)
                
                LANGUAGE: {lang_rule}
                """
                
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.1, 
                )
                
                raw_text = completion.choices[0].message.content
                
                # --- PYTHON CLEANER (The Fix) ---
                # This forces a double-enter before every bold label so they never stick together.
                clean_text = raw_text.replace("**Definition:**", "\n\n**Definition:**")
                clean_text = clean_text.replace("**Key Points:**", "\n\n**Key Points:**")
                clean_text = clean_text.replace("**Formula:**", "\n\n**Formula:**")
                clean_text = clean_text.replace("**Example:**", "\n\n**Example:**")
                
                # Streaming the CLEAN text
                for word in clean_text.split():
                    full_response += word + " "
                    time.sleep(0.01)
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                
            except Exception as e:
                placeholder.error("Error.")
                full_response = "Error"

    st.session_state.messages.append({"role": "assistant", "text": full_response})
