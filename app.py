import streamlit as st
from groq import Groq
import json
import urllib.parse

# -----------------------------------------------------------
# PROFESSOR PROTON - CLEAN SCHEMATIC EDITION 🧹
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️", layout="centered")

# --- 1. CSS ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    p, h1, h2, h3, li, div, span, b { color: #000000 !important; font-family: 'Helvetica Neue', sans-serif; }
    
    .definition-box { background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #2196f3; }
    .points-box { background-color: #f5f5f5; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #9e9e9e; }
    .formula-box { background-color: #fff3e0; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #ff9800; font-family: 'Courier New', monospace; font-weight: bold; }
    .example-box { background-color: #e8f5e9; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #4caf50; }
    
    .stButton button { border-radius: 20px; width: 100%; font-weight: bold; }
    button[kind="primary"] { background-color: #2e86de !important; border: none; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. KEYS ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ Groq API Key missing.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. DIAGRAM GENERATOR (With Cleaning Logic) ---
def get_diagram_url(dot_code):
    base_url = "https://quickchart.io/graphviz"
    
    # 🧹 CLEANER FUNCTION: Removes Markdown backticks if the AI adds them
    clean_dot = dot_code.replace("```dot", "").replace("```", "").strip()
    
    encoded_dot = urllib.parse.quote(clean_dot)
    return f"{base_url}?graph={encoded_dot}&width=500&height=300&format=png"

# --- 4. UI HEADER ---
st.title("Professor Proton ⚛️")
with st.expander("⚙️ Settings", expanded=False):
    selected_class = st.selectbox("Class", [6, 7, 8, 9, 10])
    language = st.radio("Language", ["English", "Punjabi"])
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.pop("pending_diagram_code", None)
        st.rerun()

# --- 5. HISTORY ---
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["type"] == "text":
            st.markdown(msg["content"], unsafe_allow_html=True)
        elif msg["type"] == "image":
            st.image(msg["content"], caption="Process Diagram")

# --- 6. MAIN LOGIC ---
user_input = st.chat_input("Ask a question (e.g. Photosynthesis)...")

if user_input:
    st.session_state.pop("pending_diagram_code", None)
    st.session_state.messages.append({"role": "user", "type": "text", "content": user_input})
    with st.chat_message("user"): st.write(user_input)

    with st.chat_message("assistant"):
        def_ph = st.empty()
        points_ph = st.empty()
        formula_ph = st.empty()
        ex_ph = st.empty()
        full_final_html = ""

        with st.spinner("Thinking..."):
            try:
                prompt = f"""
                Act as a Science Teacher for Class {selected_class}. Topic: "{user_input}"
                
                1. Content: Standard JSON structure.
                2. Diagram: Write RAW 'graphviz_dot' code for a FLOWCHART.
                   - START with 'digraph G {{'
                   - DO NOT use markdown backticks.
                   - Use rankdir=LR;
                   - Use rectangular nodes: node [shape=box, style=filled, fillcolor="#E3F2FD"];
                   
                Return JSON:
                {{
                    "definition": "...",
                    "points": ["..."],
                    "formula": "...",
                    "example": "...",
                    "graphviz_dot": "digraph G {{ ... }}"
                }}
                
                Language: {"English" if language == "English" else "Punjabi (Gurmukhi)"}
                """
                
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                data = json.loads(completion.choices[0].message.content)
                
                st.session_state["pending_diagram_code"] = data.get("graphviz_dot", None)

                full_final_html += f"<div class='definition-box'><b>📖 Definition:</b><br>{data['definition']}</div>"
                def_ph.markdown(full_final_html, unsafe_allow_html=True)
                
                points_html = "<ul>" + "".join([f"<li>{p}</li>" for p in data['points']]) + "</ul>"
                full_final_html += f"<div class='points-box'><b>⚡ Key Points:</b>{points_html}</div>"
                points_ph.markdown(full_final_html, unsafe_allow_html=True)
                
                if data['formula'] and data['formula'] != "None":
                    full_final_html += f"<div class='formula-box'><b>🧮 Formula:</b><br>{data['formula']}</div>"
                    formula_ph.markdown(full_final_html, unsafe_allow_html=True)
                
                full_final_html += f"<div class='example-box'><b>🌍 Example:</b><br>{data['example']}</div>"
                ex_ph.markdown(full_final_html, unsafe_allow_html=True)
                
                st.session_state.messages.append({"role": "assistant", "type": "text", "content": full_final_html})
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- 7. BUTTON ---
if "pending_diagram_code" in st.session_state:
    st.write("") 
    if st.button("📊 Show Process Diagram (Perfect Text)", type="primary"):
        with st.spinner("Generating schematic..."):
            dot_code = st.session_state["pending_diagram_code"]
            if dot_code:
                img_url = get_diagram_url(dot_code)
                st.image(img_url, caption="Flowchart Schematic")
                st.session_state.messages.append({"role": "assistant", "type": "image", "content": img_url})
                del st.session_state["pending_diagram_code"]
                st.rerun()
