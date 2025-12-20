import streamlit as st
from groq import Groq
import json
import time
import requests
import io
from PIL import Image

# -----------------------------------------------------------
# PROFESSOR PROTON - BUTTON FIX EDITION 🛠️
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️", layout="centered")

# --- 1. CSS & STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    p, h1, h2, h3, li, div, span { color: #000000 !important; font-family: 'Helvetica Neue', sans-serif; }
    
    /* SEPARATE LAYOUT BOXES */
    .definition-box { background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #2196f3; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .points-box { background-color: #f5f5f5; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #9e9e9e; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .formula-box { background-color: #fff3e0; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #ff9800; font-family: 'Courier New', monospace; font-weight: bold; }
    .example-box { background-color: #e8f5e9; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #4caf50; }
    
    /* Button Styling */
    .stButton button { border-radius: 20px; width: 100%; font-weight: bold; }
    button[kind="primary"] { background-color: #6c5ce7 !important; border: none; }
</style>
""", unsafe_allow_html=True)

# --- 2. SETUP API KEYS ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ Groq API Key missing.")
    st.stop()
if "HF_API_KEY" not in st.secrets:
    st.warning("⚠️ HF_API_KEY missing. Images won't work.")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. HELPER FUNCTIONS ---

def generate_image(prompt_text):
    """Brain 2: Calls Hugging Face to draw the diagram."""
    if "HF_API_KEY" not in st.secrets: return None
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {st.secrets['HF_API_KEY']}"}
    payload = {"inputs": f"educational science textbook diagram, clear labels, white background, high quality, accurate: {prompt_text}"}
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        image = Image.open(io.BytesIO(response.content))
        return image
    except: return None

def stream_section(placeholder, box_class, title, content):
    """Animates text typing inside a box."""
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
        st.session_state.pop("pending_image_prompt", None) # Clear pending button
        st.rerun()

# --- 5. CHAT HISTORY DISPLAY ---
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], str):
            st.markdown(msg["content"], unsafe_allow_html=True)
        elif isinstance(msg["content"], Image.Image):
            st.image(msg["content"], caption="Generated Diagram", use_column_width=True)

# --- 6. MAIN CHAT LOGIC ---
user_input = st.chat_input("Ask a question (e.g. Photosynthesis)...")

if user_input:
    # 1. Clear any old pending buttons from previous turns
    st.session_state.pop("pending_image_prompt", None)
    
    # 2. Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.write(user_input)

    # 3. Generate Answer
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
                Return strict JSON.
                Structure: {{
                    "definition": "Text", "points": ["p1", "p2"], "formula": "Text or None", 
                    "example": "Text", 
                    "image_description": "A detailed physical description for a scientific diagram of this topic for an artist."
                }}
                Language: {"English" if language == "English" else "Punjabi (Gurmukhi)"}
                """
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                data = json.loads(completion.choices[0].message.content)
                
                # SAVE THE IMAGE PROMPT TO MEMORY (This fixes the bug!)
                st.session_state["pending_image_prompt"] = data.get("image_description", user_input + " diagram")

                # Animation
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
                
                # FORCE RERUN to show the button below immediately
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- 7. THE PERSISTENT BUTTON (Outside the input loop) ---
# This checks memory to see if a button should exist, even if user_input is gone.

if "pending_image_prompt" in st.session_state:
    st.write("") # Spacer
    if st.button("🎨 Generate Diagram for this Topic", type="primary"):
        with st.spinner("Brain 2 is drawing... (Wait ~15s)"):
            prompt = st.session_state["pending_image_prompt"]
            img = generate_image(prompt)
            if img:
                # Add image to history
                st.session_state.messages.append({"role": "assistant", "content": img})
                # Remove the pending button state so it doesn't stay forever
                del st.session_state["pending_image_prompt"]
                st.rerun()
            else:
                st.error("Could not generate image. Check HF_API_KEY.")
