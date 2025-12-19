import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="System Check")
st.title("🛠️ Professor Proton System Check")

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    st.write("### Attempting to connect to Google...")
    
    try:
        # Ask Google for a list of available models
        found_any = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                st.success(f"✅ Found Model: {m.name}")
                found_any = True
        
        if not found_any:
            st.error("Connection successful, but no models found. (Rare error)")
            
    except Exception as e:
        st.error(f"❌ Connection Failed: {str(e)}")
else:
    st.error("API Key missing.")
