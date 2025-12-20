import streamlit as st
from groq import Groq
import json
import time

# -----------------------------------------------------------
# PROFESSOR PROTON - ANIMATED LAYOUT FIX 🎬
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️", layout="centered")

# --- 1. CSS (Layout Separation) ---
st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #ffffff; }
    
    /* Force Black Text */
    p, h1, h2, h3, li, div, span {
        color: #000000 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* SEPARATE BOXES */
    .definition-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #2196f3;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .points-box {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #9e9e9e;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .formula-box {
        background-color: #fff3e0;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #ff9800;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }
    
    .example-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #4caf50;
    }
    
    /* Button */
    .stButton button {
        border-radius: 20px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SETUP ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ Groq API Key is missing!")
    st.stop()
    
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. HELPER FUNCTION: ANIMATE TEXT INSIDE HTML BOX ---
def stream_section(placeholder, box_class, title, content):
    """
    Animates text appearing inside a specific colored box.
    """
    full_html = ""
    # We animate the content word by word
    words = content.split()
    current_text = ""
    
    for word in words:
        current_text += word + " "
        # Update the placeholder with the current text inside the box
        # We add the ▌ cursor to make it look like typing
        html = f"""
        <div class='{box_class}'>
            <b>{title}</b><br>
            {current_text} ▌
        </div>
        """
        placeholder.markdown(html, unsafe_allow_html=True)
        time.sleep(0.02) # Typing Speed
        
    # Final render without cursor
    final_html = f"""
    <div class='{box_class}'>
        <b>{title}</b><br>
        {current_text}
    </div>
    """
    placeholder.markdown(final_html, unsafe_allow_html=True)
    return final_html

# --- 4. UI HEADER ---
st.title("Professor Proton ⚛️")

with st.expander("⚙️ Settings", expanded=False):
    selected_class = st.selectbox("Class", [6, 7, 8, 9, 10])
    language = st.radio("Language", ["English", "Punjabi"])
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 5. CHAT ENGINE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# User Input
user_input = st.chat_input("Ask a question (e.g. Force)...")

if user_input:
    # 1. Show User Input
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 2. Generate Structured Answer
    with st.chat_message("assistant"):
        # We create empty placeholders for each section so they appear in order
        def_placeholder = st.empty()
        points_placeholder = st.empty()
        formula_placeholder = st.empty()
        ex_placeholder = st.empty()
        
        full_final_html = ""
        
        with st.spinner("Thinking..."):
            try:
                # --- BRAIN ---
                prompt = f"""
                Act as a Science Teacher for Class {selected_class}.
                Topic: "{user_input}"
                
                Return JSON.
                Structure:
                {{
                    "definition": "Definition text.",
                    "points": ["Point 1", "Point 2", "Point 3"],
                    "formula": "Formula or None",
                    "example": "Real world example."
                }}
                
                Language Rule: {"English" if language == "English" else "Punjabi (Gurmukhi)"}
                """
                
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                
                data = json.loads(completion.choices[0].message.content)
                
                # --- ANIMATION PHASE ---
                
                # 1. Animate Definition
                html_1 = stream_section(def_placeholder, "definition-box", "📖 Definition:", data['definition'])
                full_final_html += html_1
                
                # 2. Animate Points (Convert list to string for animation)
                points_html_list = "<ul>" + "".join([f"<li>{p}</li>" for p in data['points']]) + "</ul>"
                # For points, we just fade them in or type them quickly. 
                # Typing HTML lists word-by-word is buggy, so we show the points box with a slight delay.
                final_points_html = f"<div class='points-box'><b>⚡ Key Points:</b>{points_html_list}</div>"
                points_placeholder.markdown(final_points_html, unsafe_allow_html=True)
                full_final_html += final_points_html
                time.sleep(0.5) # Pause for effect
                
                # 3. Animate Formula
                if data['formula'] and data['formula'] != "None":
                    html_3 = stream_section(formula_placeholder, "formula-box", "🧮 Formula:", data['formula'])
                    full_final_html += html_3
                
                # 4. Animate Example
                html_4 = stream_section(ex_placeholder, "example-box", "🌍 Real World Example:", data['example'])
                full_final_html += html_4
                
                # Save complete HTML to history
                st.session_state.messages.append({"role": "assistant", "content": full_final_html})
                            
            except Exception as e:
                st.error("I couldn't process that. Please try again.")
