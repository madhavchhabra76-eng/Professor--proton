import streamlit as st
from groq import Groq
import json
import time
import requests
import io
import urllib.parse
from PIL import Image

# -----------------------------------------------------------
# PROFESSOR PROTON - AI ARTIST EDITION (Flux) 🎨
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
    button[kind="primary"] { background-color: #6c5ce7 !important; border: none; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. KEYS ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ Groq API Key missing.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. POLLINATIONS AI (FLUX MODEL) ---
def generate_image(visual_description):
    # We explicitly tell the AI to focus on VISUALS, not TEXT.
    # 'nologo=true' removes watermarks.
    # 'model=flux' is the high-quality mode.
    
    prompt = f"A high-quality, 4k, cinematic educational illustration of {visual_description}. Scientific accuracy, detailed textures, dramatic lighting, photorealistic or 3D render style. No text labels."
    
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&model=flux&nologo=true&enhance=true"
    
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        return None
    except:
        return None

# --- 4. UI ---
st.title("Professor Proton ⚛️")
with st.expander("⚙️ Settings", expanded=False):
    selected_class = st.selectbox("Class", [6, 7, 8, 9, 10])
    language = st.radio("Language", ["English", "Punjabi"])
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.pop("pending_image_prompt", None)
        st.rerun()

# --- 5. HISTORY ---
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], str):
            st.markdown(msg["content"], unsafe_allow_html=True)
        elif isinstance(msg["content"], Image.Image):
            st.image(msg["content"], caption="AI Generated Image", use_column_width=True)

# --- 6. LOGIC ---
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
                # Ask Groq for the text content AND a visual description
                prompt = f"""
                Act as a Science Teacher for Class {selected_class}. Topic: "{user_input}"
                
                1. Content: Standard JSON (definition, points, formula, example).
                2. Visual: Create a 'image_prompt' that describes the OBJECTS only. 
                   - Example: "A close up of a green leaf with sun rays hitting it."
                   - DO NOT ask for text labels or arrows.
                   
                Return JSON:
                {{
                    "definition": "...",
                    "points": ["..."],
                    "formula": "...",
                    "example": "...",
                    "image_prompt": "..."
                }}
                
                Language: {"English" if language == "English" else "Punjabi (Gurmukhi)"}
                """
                
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                data = json.loads(completion.choices[0].message.content)
                
                st.session_state["pending_image_prompt"] = data.get("image_prompt", user_input)

                # Render text boxes
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
                
                st.session_state.messages.append({"role": "assistant", "content": full_final_html})
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- 7. BUTTON ---
if "pending_image_prompt" in st.session_state:
    st.write("") 
    if st.button("🎨 Generate AI Image (Flux)", type="primary"):
        with st.spinner("Painting image (Wait ~15s)..."):
            visual_prompt = st.session_state["pending_image_prompt"]
            img = generate_image(visual_prompt)
            if img:
                st.session_state.messages.append({"role": "assistant", "content": img})
                del st.session_state["pending_image_prompt"]
                st.rerun()
            else:
                st.error("Server busy. Click again.")
