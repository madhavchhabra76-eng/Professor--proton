import streamlit as st
from groq import Groq
import json

# -----------------------------------------------------------
# PROFESSOR PROTON - TEXT LAYOUT FIX (JSON) 📝
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️", layout="centered")

# --- 1. CSS (The Separation Logic) ---
st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #ffffff; }
    
    /* Force Black Text everywhere */
    p, h1, h2, h3, li, div, span {
        color: #000000 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* BOX STYLES - This physically forces separation */
    
    .definition-box {
        background-color: #e3f2fd; /* Soft Blue */
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px; /* Big gap below */
        border-left: 5px solid #2196f3;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .points-box {
        background-color: #f5f5f5; /* Light Grey */
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #9e9e9e;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .formula-box {
        background-color: #fff3e0; /* Soft Orange */
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #ff9800;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }
    
    .example-box {
        background-color: #e8f5e9; /* Soft Green */
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #4caf50;
    }

    /* List styling inside boxes */
    li {
        margin-bottom: 10px; /* Space between bullet points */
    }
    
    /* Input field styling */
    .stTextInput input {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SETUP ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ Groq API Key is missing!")
    st.stop()
    
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. UI HEADER ---
st.title("Professor Proton ⚛️")

with st.expander("⚙️ Settings", expanded=False):
    selected_class = st.selectbox("Class", [6, 7, 8, 9, 10])
    language = st.radio("Language", ["English", "Punjabi"])
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 4. CHAT ENGINE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # Render HTML content safely
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
        placeholder = st.empty()
        
        with st.spinner("Thinking..."):
            try:
                # --- THE BRAIN: Forces JSON Output ---
                # This guarantees the AI cannot write a paragraph.
                # It MUST give us separate strings.
                
                prompt = f"""
                Act as a Science Teacher for Class {selected_class}.
                Topic: "{user_input}"
                
                You must return valid JSON strictly. 
                Structure:
                {{
                    "definition": "A clear, simple definition.",
                    "points": ["Point 1", "Point 2", "Point 3"],
                    "formula": "The formula or equation (or 'None')",
                    "example": "A real world example."
                }}
                
                Language Rule: {"English" if language == "English" else "Punjabi (Gurmukhi)"}
                """
                
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"} # FORCE JSON MODE
                )
                
                # Parse the JSON
                data = json.loads(completion.choices[0].message.content)
                
                # --- BUILD THE UI MANUALLY ---
                # We build HTML strings. This ensures exact layout control.
                
                # 1. Definition (Blue)
                html_output = f"""
                <div class='definition-box'>
                    <b>📖 Definition:</b><br>{data['definition']}
                </div>
                """
                
                # 2. Key Points (Grey) - We loop through the list to make bullets
                html_output += "<div class='points-box'><b>⚡ Key Points:</b><ul>"
                for p in data['points']:
                    html_output += f"<li>{p}</li>"
                html_output += "</ul></div>"
                
                # 3. Formula (Orange) - Only show if it exists
                if data['formula'] and data['formula'] != "None":
                    html_output += f"<div class='formula-box'><b>🧮 Formula:</b><br>{data['formula']}</div>"
                
                # 4. Example (Green)
                html_output += f"<div class='example-box'><b>🌍 Real World Example:</b><br>{data['example']}</div>"
                
                # Render the final HTML
                st.markdown(html_output, unsafe_allow_html=True)
                
                # Save to memory
                st.session_state.messages.append({"role": "assistant", "content": html_output})
                            
            except Exception as e:
                st.error("I couldn't process that. Please try again.")
