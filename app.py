import streamlit as st
import google.generativeai as genai
import time

# 1. Page Configuration
st.set_page_config(page_title="Silent Cat Movie Maker", layout="wide")
st.title("🐱 Silent Cat Movie Maker (Visual Script Only)")

# 2. API Key Setup
# Secrets ထဲမှာ မရှိရင် Sidebar မှာ တောင်းမယ်
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("⚙️ Settings")

# Model စာရင်း (ဒီကောင်အရင်လာမှ အောက်က selectbox အလုပ်လုပ်မှာပါ)
model_options = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "models/gemini-2.5-pro",
    "models/gemini-3-flash-preview",
    "models/gemini-3-pro-preview"
]

# Model ရွေးခိုင်းမယ်
selected_model = st.sidebar.selectbox("Select Model:", model_options, index=0)

# Scene အရေအတွက် ရွေးခိုင်းမယ် (Variable define လုပ်ထားခြင်း)
num_scenes_input = st.sidebar.slider("Scene Count:", 4, 15, 8)

st.sidebar.info("Note: No Audio (TTS) - Visual Script Only")

# 3. Session State Initialization
if 'step' not in st.session_state: st.session_state.step = 1
if 'burmese_story' not in st.session_state: st.session_state.burmese_story = ""
if 'scenes_data' not in st.session_state: st.session_state.scenes_data = [] 
if 'final_data' not in st.session_state: st.session_state.final_data = []

# --- Functions ---

def generate_visual_script(topic, model_name):
    """Step 1: Silent Movie Script"""
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        You are a Video Scriptwriter for a viral 'Silent Cat Movie'.
        Topic: '{topic}'
        Rules:
        1. NO Dialogue. NO Narration.
        2. Focus ONLY on Visual Actions.
        3. Language: Write the visual description in Burmese.
        4. Length: Create enough content for a 3-minute video.
        Output: Just write the visual story flow in Burmese paragraphs.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Script Error: {e}")
        return None

def generate_scene_breakdown(script_text, model_name, scene_count):
    """Step 2: Breakdown into Scenes"""
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Visual Script (Burmese): "{script_text}"
        Task:
        1. Split this script into exactly {scene_count} distinct scenes.
        2. For each scene, provide Burmese Visual Action text & English Image Prompt.
        Output format:
        Burmese: [Action Text]
        English_Prompt: [Image Prompt]
        ###
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Breakdown Error: {e}")
        return None

def generate_preview_image(prompt):
    """Image Preview"""
    try:
        # Priority 1: Imagen 3
        model = genai.GenerativeModel("imagen-3.0-generate-001")
        result = model.generate_images(prompt=prompt + ", 3D render, cute cat", number_of_images=1)
        return result.images[0]
    except:
        # Priority 2: Fallback
        try:
             model = genai.GenerativeModel("models/gemini-3-pro-image-preview")
             result = model.generate_images(prompt=prompt, number_of_images=1)
             return result.images[0]
        except Exception as e:
            st.warning(f"Image Gen Error (Check API Access): {e}")
            return None

def generate_final_prompts(image_prompt, model_name):
    """Step 3: Final Prompts"""
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Based on: "{image_prompt}"
        Generate 3 prompts:
        IMAGE: Optimized for DALL-E 3
        VIDEO: Optimized for Luma
        MUSIC: Optimized for Suno
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- Main Workflow ---

if not api_key:
    st.warning("Please enter Gemini API Key to start.")
    st.stop()

genai.configure(api_key=api_key)

steps = ["Visual Script", "Scene Breakdown", "Final Output"]
st.progress(st.session_state.step / 3)
st.subheader(f"Step {st.session_state.step}: {steps[st.session_state.step-1]}")

# STEP 1
if st.session_state.step == 1:
    with st.form("s1"):
        topic = st.text_input("Story Topic", "မိုးရွာထဲ ကျန်ခဲ့တဲ့ ကြောင်လေး")
        if st.form_submit_button("Write Script"):
            with st.spinner("Writing..."):
                res = generate_visual_script(topic, selected_model)
                if res:
                    st.session_state.burmese_story = res
                    st.rerun()
    
    if st.session_state.burmese_story:
        st.session_state.burmese_story = st.text_area("Edit Script:", st.session_state.burmese_story, height=300)
        if st.button("Next >"):
            st.session_state.step = 2
            st.rerun()

# STEP 2
elif st.session_state.step == 2:
    if not st.session_state.scenes_data:
        with st.spinner(f"Splitting into {num_scenes_input} scenes..."):
            raw = generate_scene_breakdown(st.session_state.burmese_story, selected_model, num_scenes_input)
            if raw:
                scenes = []
                for s in raw.split('###'):
                    if "Burmese:" in s:
                        txt, prmpt = "", ""
                        for line in s.split('\n'):
                            if "Burmese:" in line: txt = line.replace("Burmese:", "").strip()
                            if "English_Prompt:" in line: prmpt = line.replace("English_Prompt:", "").strip()
                        if txt: scenes.append({"text": txt, "prompt": prmpt, "img": None})
                st.session_state.scenes_data = scenes
                st.rerun()

    for i, sc in enumerate(st.session_state.scenes_data):
        with st.expander(f"Scene {i+1}", expanded=True):
            c1, c2 = st.columns([1,2])
            with c1:
                st.write(sc['text'])
                if st.button(f"Generate Image {i+1}", key=f"b{i}"):
                    img = generate_preview_image(sc['prompt'])
                    if img: 
                        st.session_state.scenes_data[i]['img'] = img
                        st.rerun()
                if sc['img']: st.image(sc['img'])
            with c2:
                st.session_state.scenes_data[i]['prompt'] = st.text_area("Prompt", sc['prompt'], key=f"p{i}")

    c1, c2 = st.columns(2)
    if c1.button("< Back"): 
        st.session_state.step = 1
        st.session_state.scenes_data = []
        st.rerun()
    if c2.button("Final >"): 
        st.session_state.step = 3
        st.rerun()

# STEP 3
elif st.session_state.step == 3:
    if not st.session_state.final_data:
        with st.spinner("Finalizing..."):
            finals = []
            for sc in st.session_state.scenes_data:
                res = generate_final_prompts(sc['prompt'], selected_model)
                p_img, p_vid, p_mus = "", "", ""
                if res:
                    for l in res.split('\n'):
                        if "IMAGE:" in l: p_img = l.replace("IMAGE:", "").strip()
                        if "VIDEO:" in l: p_vid = l.replace("VIDEO:", "").strip()
                        if "MUSIC:" in l: p_mus = l.replace("MUSIC:", "").strip()
                finals.append({**sc, "p_img": p_img, "p_vid": p_vid, "p_mus": p_mus})
            st.session_state.final_data = finals
            st.rerun()

    for i, item in enumerate(st.session_state.final_data):
        st.divider()
        st.subheader(f"Scene {i+1}")
        c1, c2 = st.columns([1,2])
        c1.info(item['text'])
        if item['img']: c1.image(item['img'])
        c2.text_area("Image Prompt", item['p_img'], key=f"fi{i}")
        c2.text_area("Video Prompt", item['p_vid'], key=f"fv{i}")
        c2.text_area("Music Prompt", item['p_mus'], key=f"fm{i}")

    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()
