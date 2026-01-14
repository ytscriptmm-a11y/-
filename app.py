import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import time

# 1. Page Configuration
st.set_page_config(page_title="Cat Story Generator", layout="wide")
st.title("🐱 Cat Story Generator (Advanced Models)")
st.caption("Select your preferred Gemini Model for storytelling")

# 2. API Key Handling (Secrets First)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")
    if not api_key:
        st.sidebar.warning("Please enter API Key to proceed.")

# --- Model Selection (Sidebar) ---
st.sidebar.header("Model Settings")

# User's requested model list
model_options = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "models/gemini-2.5-pro",
    "models/gemini-3-flash-preview",
    "models/gemini-3-pro-preview"
]

selected_text_model = st.sidebar.selectbox(
    "Choose Story Model:", 
    model_options,
    index=0 # Default to first option
)

st.sidebar.info(f"Using for Image: models/gemini-3-pro-image-preview")

# 3. User Inputs
col1, col2 = st.columns(2)
with col1:
    story_topic = st.text_input("ဇာတ်လမ်းခေါင်းစဉ်", "A tiny cat with a huge backpack travelling the world")
with col2:
    num_scenes = st.slider("Scenes အရေအတွက်", 3, 10, 4)

# --- Functions ---

def generate_story(topic, scenes, model_name):
    """ရွေးထားသော Model ဖြင့် ဇာတ်လမ်းရေးခိုင်းခြင်း"""
    try:
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        Write a short, viral 'Cat Meme' story based on: '{topic}'.
        Split it into exactly {scenes} scenes.
        
        Output Format (Strictly follow this):
        Scene 1:
        Narration: [Story text in English]
        Prompt: [Detailed image description for a 3D Pixar-style cute cat]
        ###
        Scene 2:
        Narration: [Story text in English]
        Prompt: [Image description]
        ###
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Story Gen Error ({model_name}): {e}")
        return None

def generate_image_with_gemini(prompt):
    """Gemini 3 Image Preview ကိုသုံးပြီး ပုံထုတ်ခြင်း"""
    try:
        # User သတ်မှတ်ထားသော Image Model
        model = genai.GenerativeModel('models/gemini-3-pro-image-preview')
        
        result = model.generate_images(
            prompt=prompt + ", 3D render, cute, viral cat meme style, high quality, soft lighting",
            number_of_images=1,
        )
        return result.images[0] # Returns PIL Image
    except Exception as e:
        # Error တက်ရင် Placeholder လေးပြပါမယ် (App မပျက်သွားအောင်လို့ပါ)
        st.warning(f"Image Gen Error: {e}. Showing placeholder instead.")
        return None

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
    """Backup ယာယီပုံ"""
    ts = int(time.time() * 1000)
    return f"https://cataas.com/cat?width=500&height=400&t={ts}"

# --- Main Logic ---

if st.button("Generate Story"):
    if not api_key:
        st.error("API Key မရှိပါ။")
    else:
        genai.configure(api_key=api_key)
        
        with st.spinner(f'Writing story with {selected_text_model}...'):
            story_text = generate_story(story_topic, num_scenes, selected_text_model)
            
            if story_text:
                scenes = story_text.split('###')
                st.success("ဇာတ်လမ်းရပါပြီ! ပုံနှင့် အသံ ဖန်တီးနေပါသည်...")
                
                for i, scene in enumerate(scenes):
                    if "Scene" in scene:
                        # Parsing Logic
                        lines = scene.strip().split('\n')
                        narration = ""
                        img_prompt = ""
                        
                        for line in lines:
                            if "Narration:" in line:
                                narration = line.replace("Narration:", "").strip()
                            if "Prompt:" in line:
                                img_prompt = line.replace("Prompt:", "").strip()
                        
                        if narration:
                            st.divider()
                            c1, c2 = st.columns([1.5, 1])
                            
                            # Left: Script & Audio
                            with c1:
                                st.subheader(f"Scene {i+1}")
                                st.markdown(f"**Script:** {narration}")
                                if img_prompt:
                                    st.caption(f"🎨 Prompt: {img_prompt}")
                                
                                audio_bytes = text_to_speech(narration)
                                if audio_bytes:
                                    st.audio(audio_bytes, format='audio/mp3')
                            
                            # Right: Image Generation
                            with c2:
                                with st.spinner('Generating Image...'):
                                    # ပုံထုတ်ဖို့ ကြိုးစားမယ်
                                    if img_prompt:
                                        img = generate_image_with_gemini(img_prompt)
                                        if img:
                                            st.image(img, use_container_width=True)
                                        else:
                                            # မရရင် Placeholder ပြမယ်
                                            st.image(get_placeholder_cat(), caption="Image Error - Placeholder Used", use_container_width=True)
