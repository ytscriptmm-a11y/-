import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import time

# 1. Page Configuration
st.set_page_config(page_title="Cat Story Generator", layout="wide")
st.title("🐱 Cat Story Generator (Internal Team)")
st.caption("Auto-Story, Audio & Scenes powered by Gemini")

# 2. API Key Handling (Secrets First)
# Server ရဲ့ Secrets ထဲမှာ Key ရှိရင် အဲ့ဒါကို တန်းသုံးမယ်။
# မရှိရင် (Local မှာ run ရင်) Sidebar ကနေ တောင်းမယ်။

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    if not api_key:
        st.sidebar.warning("Please enter API Key to proceed.")

# 3. User Inputs
col1, col2 = st.columns(2)
with col1:
    story_topic = st.text_input("ဇာတ်လမ်းခေါင်းစဉ်", "A tiny cat with a huge backpack travelling the world")
with col2:
    num_scenes = st.slider("Scenes အရေအတွက်", 3, 10, 4)

# --- Functions ---

def generate_story(topic, scenes):
    """Gemini ကိုသုံးပြီး ဇာတ်လမ်းရေးခိုင်းခြင်း"""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Write a short, viral 'Cat Meme' story based on: '{topic}'.
    Split it into exactly {scenes} scenes.
    
    Output Format (Strictly follow this):
    Scene 1:
    Narration: [Story text in English]
    ###
    Scene 2:
    Narration: [Story text in English]
    ###
    """
    response = model.generate_content(prompt)
    return response.text

def text_to_speech(text):
    """စာသားကို အသံပြောင်းခြင်း (gTTS)"""
    try:
        tts = gTTS(text=text, lang='en')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        return audio_fp
    except Exception as e:
        st.error(f"Audio Error: {e}")
        return None

def get_placeholder_cat():
    """ယာယီ ကြောင်ပုံစံ (Placeholder) ယူခြင်း"""
    # Timestamp ထည့်ထားတာက ပုံမထပ်အောင်လို့ပါ
    ts = int(time.time() * 1000)
    # Random size to make it look dynamic
    return f"https://cataas.com/cat?width=500&height=400&t={ts}"

# --- Main Logic ---

if st.button("Generate Story"):
    if not api_key:
        st.error("API Key မရှိပါ။ Local မှာ run နေရင် Sidebar မှာထည့်ပါ။ Server ပေါ်မှာဆိုရင် Secrets မှာ ထည့်ထားပါ (Settings > Secrets)။")
    else:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        with st.spinner('ဇာတ်လမ်း စဉ်းစားနေပါသည်...'):
            try:
                # 1. Story Generation
                story_text = generate_story(story_topic, num_scenes)
                
                # Split scenes by '###'
                scenes = story_text.split('###')
                
                st.success("ဇာတ်လမ်းရပါပြီ!")
                
                # 2. Display Loop
                for i, scene in enumerate(scenes):
                    if "Scene" in scene:
                        # Extract Narration Text
                        lines = scene.strip().split('\n')
                        narration = ""
                        for line in lines:
                            if "Narration:" in line:
                                narration = line.replace("Narration:", "").strip()
                        
                        if narration:
                            st.divider()
                            c1, c2 = st.columns([1.5, 1])
                            
                            # Left Column: Text & Audio
                            with c1:
                                st.subheader(f"Scene {i+1}")
                                st.markdown(f"**Script:** {narration}")
                                
                                # Generate Audio on the fly
                                audio_bytes = text_to_speech(narration)
                                if audio_bytes:
                                    st.audio(audio_bytes, format='audio/mp3')
                            
                            # Right Column: Placeholder Image
                            with c2:
                                # Add a small delay so timestamps differ for images
                                time.sleep(0.1) 
                                st.image(get_placeholder_cat(), caption=f"Scene {i+1} Visual", use_container_width=True)
                                
            except Exception as e:
                st.error(f"Error ဖြစ်သွားပါတယ်: {e}")