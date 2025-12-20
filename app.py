import streamlit as st
from groq import Groq
import json
import time
from huggingface_hub import InferenceClient
from PIL import Image
import io

# -----------------------------------------------------------
# PROFESSOR PROTON - PUBLIC MODEL FIX 🔓
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️", layout="centered")

# --- 1. CSS & STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    p, h1, h2, h3, li, div, span { color: #000000 !important; font-family: 'Helvetica Neue', sans-serif; }
    
    .definition-box { background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #2196f3; }
    .points-box { background-color: #f5f5f5; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #9e9e9e; }
    .formula-box { background-color: #fff3e0; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #ff9800; font-family: 'Courier New', monospace; font-weight: bold; }
    .example-box { background-color: #e8f5e9; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #4caf50; }
    
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

# --- 3. OFFICIAL IMAGE GENERATOR (Public Model) ---

def generate_image(prompt_text):
    if "HF_API_KEY" not in st.secrets: return None
    
    hf_client = InferenceClient(token=st.secrets["HF_API_KEY"])
    
    # 🚨 CHANGED MODEL: This one is 100% Public and Free (No legal gate)
    model_id = "runwayml/stable-diffusion-v1-5"
    
    for i in range(5): 
        try:
            image = hf_client.text_to_image(
                f"educational science textbook diagram, white background, clear, high quality: {prompt_text}",
                model=model_id
            )
            return image
                
        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg:
                st.toast("💤 AI is waking up... (waiting 10s)")
                time.sleep(10)
                continue
            else:
                st.error(f"Image Error: {error_msg}")
                return None
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
            st.image(msg["content"], caption="Generated Diagram", use_column_width=True)

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
                st.session_state["pending_image_prompt"] = data.get("image_description", user_input + " diagram")

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
    if st.button("🎨 Generate Diagram for this Topic", type="primary"):
        with st.spinner("Drawing diagram (Wait ~15s)..."):
            prompt = st.session_state["pending_image_prompt"]
            img = generate_image(prompt)
            if img:
                st.session_state.messages.append({"role": "assistant", "content": img})
                del st.session_state["pending_image_prompt"]
                st.rerun()
            else:
                st.error("Still loading or Error. Try again in 10s.")
