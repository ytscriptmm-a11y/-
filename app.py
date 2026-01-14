import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# 1. Page Configuration
st.set_page_config(page_title="Burmese Cat Story Workflow", layout="wide")
st.title("🐱 Burmese Cat Story Creator (Professional Workflow)")

# 2. API Key Setup
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

# 3. Session State Initialization (အဆင့်ဆင့်မှတ်ထားဖို့အတွက်)
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'burmese_story' not in st.session_state:
    st.session_state.burmese_story = ""
if 'scenes_data' not in st.session_state:
    st.session_state.scenes_data = [] # Stores (text, audio, initial_prompt)
if 'final_data' not in st.session_state:
    st.session_state.final_data = []

# --- Functions ---

def generate_burmese_story(topic, model_name="gemini-1.5-flash"):
    """အဆင့် (၁) - မြန်မာလို ဇာတ်လမ်းရေးခြင်း"""
    model = genai.GenerativeModel(model_name)
    prompt = f"""
    You are a creative writer for TikTok/YouTube Shorts.
    Write a viral, emotional, or funny 'Cat Story' in Burmese language based on: '{topic}'.
    The story should be about 4 to 6 sentences long. 
    Just write the story narration in Burmese text directly. Do not add 'Scene 1' labels yet.
    """
    response = model.generate_content(prompt)
    return response.text

def generate_initial_prompts(burmese_text, model_name="gemini-1.5-flash"):
    """အဆင့် (၂) - ဇာတ်လမ်းကို အပိုင်းခွဲပြီး ပုံ Prompt ထုတ်ခြင်း"""
    model = genai.GenerativeModel(model_name)
    prompt = f"""
    I have a story in Burmese: "{burmese_text}"
    
    1. Split this story into 4 distinct scenes.
    2. For each scene, write a visual image prompt in English describing a cute 3D Pixar-style cat scene that matches the text.
    
    Output format strictly like this:
    Burmese: [Burmese sentence]
    English_Prompt: [English Image Prompt]
    ###
    Burmese: [Next Burmese sentence]
    English_Prompt: [Next English Image Prompt]
    ###
    """
    response = model.generate_content(prompt)
    return response.text

def generate_final_3_prompts(image_prompt, model_name="gemini-1.5-flash"):
    """အဆင့် (၃) - Prompt ၃ မျိုး ခွဲထုတ်ခြင်း"""
    model = genai.GenerativeModel(model_name)
    prompt = f"""
    Based on this image description: "{image_prompt}"
    
    Generate 3 specific prompts for content creation:
    1. Image Prompt: Optimized for DALL-E 3 / Midjourney (High quality, 3D render, cute cat).
    2. Video Prompt: Optimized for Runway/Luma (Describe camera movement, zoom, action).
    3. Music Prompt: Optimized for Suno/Udio (Describe mood, instruments, tempo).
    
    Output strictly in this format:
    IMAGE: [Content]
    VIDEO: [Content]
    MUSIC: [Content]
    """
    response = model.generate_content(prompt)
    return response.text

def text_to_speech_mm(text):
    """မြန်မာစာကို အသံပြောင်းခြင်း"""
    try:
        # lang='my' သည် မြန်မာဘာသာစကားအတွက်ဖြစ်သည်
        tts = gTTS(text=text, lang='my') 
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        return audio_fp
    except Exception as e:
        return None

# --- Main Workflow ---

if not api_key:
    st.warning("Please enter Gemini API Key to start.")
    st.stop()

genai.configure(api_key=api_key)

# Progress Bar
steps = ["၁. ဇာတ်လမ်းရေး", "၂. ပုံ Prompt နှင့် အသံ", "၃. Final Output"]
current_progress = (st.session_state.step / 3)
st.progress(current_progress)
st.subheader(f"အဆင့် {st.session_state.step}: {steps[st.session_state.step-1]}")

# ----------------------------------------------------------------
# STEP 1: Story Generation (Burmese)
# ----------------------------------------------------------------
if st.session_state.step == 1:
    with st.form("step1_form"):
        topic = st.text_input("ဇာတ်လမ်းခေါင်းစဉ် (Topic)", "ကျောပိုးအိတ်နဲ့ ခရီးသွားတဲ့ ကြောင်လေး")
        submitted = st.form_submit_button("ဇာတ်လမ်း စတင်ရေးသားရန်")
        
        if submitted:
            with st.spinner("မြန်မာလို ဇာတ်လမ်းစဉ်းစားနေပါသည်..."):
                story = generate_burmese_story(topic)
                st.session_state.burmese_story = story
                st.rerun()

    if st.session_state.burmese_story:
        st.info("အောက်ပါ ဇာတ်လမ်းကို ဖတ်ရှုပြီး ပြင်ဆင်လိုက ပြင်ဆင်နိုင်ပါသည်။")
        # User can edit the story here
        edited_story = st.text_area("ဇာတ်လမ်း (မြန်မာ)", st.session_state.burmese_story, height=200)
        st.session_state.burmese_story = edited_story
        
        if st.button("ဇာတ်လမ်းအဆင်ပြေပြီ > နောက်တစ်ဆင့်သွားမယ်"):
            st.session_state.step = 2
            st.rerun()

# ----------------------------------------------------------------
# STEP 2: Generate Audio & Draft Prompts
# ----------------------------------------------------------------
elif st.session_state.step == 2:
    # Generate Data only if empty (to avoid regenerating on every edit)
    if not st.session_state.scenes_data:
        with st.spinner("အသံဖိုင်များနှင့် ပုံ Prompt များ ဖန်တီးနေပါသည်..."):
            raw_data = generate_initial_prompts(st.session_state.burmese_story)
            # Parse the raw data
            scenes = raw_data.split('###')
            parsed_scenes = []
            for scene in scenes:
                if "Burmese:" in scene:
                    lines = scene.strip().split('\n')
                    burmese_text = ""
                    eng_prompt = ""
                    for line in lines:
                        if "Burmese:" in line:
                            burmese_text = line.replace("Burmese:", "").strip()
                        if "English_Prompt:" in line:
                            eng_prompt = line.replace("English_Prompt:", "").strip()
                    
                    if burmese_text:
                        audio = text_to_speech_mm(burmese_text)
                        parsed_scenes.append({
                            "text": burmese_text,
                            "audio": audio,
                            "prompt": eng_prompt
                        })
            st.session_state.scenes_data = parsed_scenes
            st.rerun()

    st.write("### အသံဖိုင်နှင့် ပုံ Prompt များကို စစ်ဆေးပါ")
    
    # Loop through scenes for editing
    for i, scene in enumerate(st.session_state.scenes_data):
        with st.expander(f"Scene {i+1}", expanded=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write(f"**Text:** {scene['text']}")
                if scene['audio']:
                    st.audio(scene['audio'], format='audio/mp3')
            with col2:
                # User can edit the prompt here
                new_prompt = st.text_area(f"Visual Prompt (English) for Scene {i+1}", scene['prompt'], key=f"prompt_{i}")
                st.session_state.scenes_data[i]['prompt'] = new_prompt

    col1, col2 = st.columns(2)
    with col1:
        if st.button("< ရှေ့တဆင့်သို့ ပြန်သွားရန်"):
            st.session_state.step = 1
            st.session_state.scenes_data = [] # Clear data to regenerate if story changes
            st.rerun()
    with col2:
        if st.button("Prompt များအဆင်ပြေပြီ > Final Output ထုတ်မယ်"):
            st.session_state.step = 3
            st.rerun()

# ----------------------------------------------------------------
# STEP 3: Final 3-Prompt Generation
# ----------------------------------------------------------------
elif st.session_state.step == 3:
    if not st.session_state.final_data:
        with st.spinner("Final Image, Video, Music Prompt များ ခွဲထုတ်နေပါသည်..."):
            final_results = []
            for scene in st.session_state.scenes_data:
                three_prompts = generate_final_3_prompts(scene['prompt'])
                
                # Parse the 3 prompts
                p_image, p_video, p_music = "", "", ""
                lines = three_prompts.split('\n')
                for line in lines:
                    if "IMAGE:" in line: p_image = line.replace("IMAGE:", "").strip()
                    if "VIDEO:" in line: p_video = line.replace("VIDEO:", "").strip()
                    if "MUSIC:" in line: p_music = line.replace("MUSIC:", "").strip()
                
                final_results.append({
                    "text": scene['text'],
                    "audio": scene['audio'],
                    "p_image": p_image,
                    "p_video": p_video,
                    "p_music": p_music
                })
            st.session_state.final_data = final_results
            st.rerun()

    st.success("🎉 အားလုံးပြီးပါပြီ။ အောက်ပါအချက်အလက်များကို Copy ယူပြီး အသုံးပြုနိုင်ပါပြီ။")

    for i, item in enumerate(st.session_state.final_data):
        st.divider()
        st.subheader(f"🎬 Scene {i+1}")
        
        # Audio Section
        c1, c2 = st.columns([1, 3])
        with c1:
            st.info("🔊 Narration (Burmese)")
            if item['audio']:
                st.audio(item['audio'], format='audio/mp3')
            st.write(f"_{item['text']}_")
            
        with c2:
            st.markdown("#### 🛠️ Prompts for Creation")
            
            # 1. Image Prompt
            st.text_input(f"🖼️ 1. Image Prompt (Midjourney/DALL-E)", value=item['p_image'], key=f"fin_img_{i}")
            
            # 2. Video Prompt
            st.text_input(f"🎥 2. Video Prompt (Runway/Luma)", value=item['p_video'], key=f"fin_vid_{i}")
            
            # 3. Music Prompt
            st.text_input(f"🎵 3. Music Prompt (Suno/Udio)", value=item['p_music'], key=f"fin_mus_{i}")

    if st.button("စက္က ပြန်စမယ် (Start Over)"):
        st.session_state.clear()
        st.rerun()
