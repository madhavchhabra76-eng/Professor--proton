import streamlit as st
from groq import Groq
import json
import time
import requests
import io
import urllib.parse
from PIL import Image

# -----------------------------------------------------------
# PROFESSOR PROTON - FLUX EDITION (Best Quality) 💎
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️", layout="centered")

# --- 1. CSS & STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    p, h1, h2, h3, li, div, span, b { color: #000000 !important; font-family: 'Helvetica Neue', sans-serif; }
    
    .definition-box { background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #2196f3; }
    .points-box { background-color: #f5f5f5; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #9e9e9e; }
    .formula-box { background-color: #fff3e0; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #ff9800; font-family: 'Courier New', monospace; font-weight: bold; }
    .example-box { background-color: #e8f5e9; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #4caf50; }
    
    .stButton button { border-radius: 20px; width: 100%; font-weight: bold; }
    button[kind="primary"] { background-color: #6c5ce7 !important; border: none; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. SETUP API KEYS ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ Groq API Key missing.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. IMAGE GENERATOR (Using FLUX Model) ---

def generate_image(detailed_description):
    # We use a trick: We ask for "Infographic style" which usually cleans up the look.
    final_prompt = f"Educational infographic of {detailed_description}. Clean vector art style, white background, high definition, minimalistic, scientific accuracy. No garbled text."
    
    encoded_prompt = urllib.parse.quote(final_prompt)
    
    # WE USE 'model=flux' -> This is the smartest free model available right now.
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&model=flux&nologo=true"
    
    try:
        response = requests.get(url, timeout=25) # Give it time to think
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            return None
    except:
        return None

def stream_section(placeholder, box_class, title, content):
    current_text = ""
    for word in content.split():
        current_text += word + " "
        placeholder.markdown(f"<div class='{box_class}'><b>{title}</b><br>{current_text} ▌</div>", unsafe_allow_html=True)
        time.sleep(0.02)
    final_html = f"<div class='{box_class}'><b>{title}</b><br>{current_text}</div>"
    placeholder.markdown(final_html, unsafe_allow_html=True)
    return final_html

# --- 4. UI HEADER ---
st.title("Professor Proton ⚛️")
with st.expander("⚙️ Settings", expanded=False):
    selected_class = st.selectbox("Class", [6, 7, 8, 9, 10])
    language = st.radio("Language", ["English", "Punjabi"])
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.pop("pending_image_prompt", None)
        st.rerun()

# --- 5. CHAT HISTORY ---
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], str):
            st.markdown(msg["content"], unsafe_allow_html=True)
        elif isinstance(msg["content"], Image.Image):
            st.image(msg["content"], caption="AI Generated Diagram", use_column_width=True)

# --- 6. MAIN LOGIC ---
user_input = st.chat_input("Ask a question (e.g. Photosynthesis)...")

if user_input:
    st.session_state.pop("pending_image_prompt", None)
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.write(user_input)

    with st.chat_message("assistant"):
        def_ph = st.empty()
        points_ph = st.empty()
        formula_ph = st.empty()
        ex_ph = st.empty()
        full_final_html = ""

        with st.spinner("Thinking..."):
            try:
                # We ask Groq to describe the VISUALS, not the text labels.
                prompt = f"""
                Act as a Science Teacher for Class {selected_class}. Topic: "{user_input}"
                Return strict JSON.
                Structure: {{
                    "definition": "Text", "points": ["p1", "p2"], "formula": "Text or None", 
                    "example": "Text", 
                    "image_description": "A visual description of {user_input} focusing on shapes, objects, and actions. Do NOT ask for text labels."
                }}
                Language: {"English" if language == "English" else "Punjabi (Gurmukhi)"}
                """
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                data = json.loads(completion.choices[0].message.content)
                
                st.session_state["pending_image_prompt"] = data.get("image_description", user_input)

                full_final_html += stream_section(def_ph, "definition-box", "📖 Definition:", data['definition'])
                points_html = "<ul>" + "".join([f"<li>{p}</li>" for p in data['points']]) + "</ul>"
                final_points_html = f"<div class='points-box'><b>⚡ Key Points:</b>{points_html}</div>"
                points_ph.markdown(final_points_html, unsafe_allow_html=True)
                full_final_html += final_points_html
                time.sleep(0.3)

                if data['formula'] and data['formula'] != "None":
                    full_final_html += stream_section(formula_ph, "formula-box", "🧮 Formula:", data['formula'])
                
                full_final_html += stream_section(ex_ph, "example-box", "🌍 Example:", data['example'])
                st.session_state.messages.append({"role": "assistant", "content": full_final_html})
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- 7. BUTTON OUTSIDE LOOP ---
if "pending_image_prompt" in st.session_state:
    st.write("") 
    if st.button("🎨 Generate Diagram (Flux Model)", type="primary"):
        with st.spinner("Drawing high-quality diagram (~15s)..."):
            detailed_prompt = st.session_state["pending_image_prompt"]
            img = generate_image(detailed_prompt)
            if img:
                st.session_state.messages.append({"role": "assistant", "content": img})
                del st.session_state["pending_image_prompt"]
                st.rerun()
            else:
                st.error("Error generating image.")
