import streamlit as st
import google.generativeai as genai
import time

# 1. Page Configuration
st.set_page_config(page_title="Silent Cat Movie Maker", layout="wide")
st.title("🐱 Silent Cat Movie Maker (Internet Meme Style)")
st.caption("Creates stories/prompts for anthropomorphic cats (standing upright, wearing clothes).")

# 2. API Key Setup
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("⚙️ Settings")

model_options = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "models/gemini-2.5-pro",
    "models/gemini-3-flash-preview",
    "models/gemini-3-pro-preview"
]
selected_model = st.sidebar.selectbox("Select Model:", model_options, index=0)
num_scenes_input = st.sidebar.slider("Scene Count:", 4, 15, 8)

st.sidebar.info("Style: Cats act like humans (Viral Meme Style)")

# 3. Session State
if 'step' not in st.session_state: st.session_state.step = 1
if 'burmese_story' not in st.session_state: st.session_state.burmese_story = ""
if 'scenes_data' not in st.session_state: st.session_state.scenes_data = [] 
if 'final_data' not in st.session_state: st.session_state.final_data = []

# --- Functions (PROMPTS UPDATED HERE) ---

def generate_visual_script(topic, model_name):
    """Step 1: Silent Movie Script (Anthropomorphic Style)"""
    try:
        model = genai.GenerativeModel(model_name)
        
        # ▼▼▼ Prompt ကို ဒီလို ပြင်လိုက်ပါ ▼▼▼
        prompt = f"""
        You are a Video Scriptwriter for a viral 'Silent Cat Meme Movie'.
        Topic: '{topic}'
        
        KEY CHARACTER SETTING: 
        The main character is an ANTHROPOMORPHIC CAT. 
        - It stands upright on two legs like a human.
        - It wears human clothes (hoodies, tiny backpacks, shirts).
        - It uses its front paws like human hands.
        - It lives in a human-like world and does human activities (cooking, working, traveling).
        
        Rules for the Script:
        1. NO Dialogue. NO Narration/Voiceover.
        2. Focus ONLY on Visual Actions (Body language, facial expressions, interactions).
        3. Language: Write the visual action descriptions in Burmese.
        4. Length: Create enough scenes for a 3-minute video.
        
        Output: Just write the visual story flow in Burmese paragraphs.
        """
        # ▲▲▲ ဒီအထိ ပြင်ပါ ▲▲▲
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Script Error: {e}")
        return None

def generate_scene_breakdown(script_text, model_name, scene_count):
    """Step 2: Breakdown into Scenes"""
    try:
        model = genai.GenerativeModel(model_name)
        # ▼▼▼ PROMPT ပြင်ထားသည် ▼▼▼
        prompt = f"""
        Visual Script (Burmese): "{script_text}"
        Task:
        1. Split this script into exactly {scene_count} distinct scenes.
        2. For each scene, provide Burmese Visual Action text.
        3. For each scene, write a detailed English Image Prompt. 
           IMPORTANT: The prompt MUST specify that the cat is an "anthropomorphic character, standing upright like a human, wearing clothes" and doing the action in a cute 3D animation style.
        Output format:
        Burmese: [Action Text]
        English_Prompt: [Detailed Image Prompt forcing human-like cat style]
        ###
        """
        # ▲▲▲ PROMPT ပြင်ထားသည် ▲▲▲
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Breakdown Error: {e}")
        return None

def generate_preview_image(prompt):
    """Image Preview (Forcing Gemini 3 Pro Image Preview)"""
    
    # လူလိုကြောင်ဖြစ်အောင် Style Keywords တွေ ပေါင်းထည့်ခြင်း
    style_suffix = ", 3D animated character, anthropomorphic cute cat wearing clothes, standing upright, human-like poses, Pixar style render, expressive face, masterpiece"
    
    try:
        # Priority 1: User Requested Model
        model = genai.GenerativeModel("models/gemini-3-pro-image-preview")
        result = model.generate_images(
            prompt=prompt + style_suffix, 
            number_of_images=1
        )
        return result.images[0]
    except Exception as e1:
        # Priority 2: Fallback to Standard Imagen 3 (if Gemini 3 is busy/unavailable)
        try:
             print(f"Gemini 3 Preview failed ({e1}), trying Imagen 3...")
             model = genai.GenerativeModel("imagen-3.0-generate-001")
             result = model.generate_images(
                 prompt=prompt + style_suffix, 
                 number_of_images=1
             )
             return result.images[0]
        except Exception as e2:
            st.warning(f"Image Gen Error: {e2}")
            return None

def generate_final_prompts(image_prompt, model_name):
    """Step 3: Final Prompts"""
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Based on: "{image_prompt}"
        Generate 3 prompts ensuring the anthropomorphic cat style is maintained:
        IMAGE: Optimized for DALL-E 3 (Detailed character design)
        VIDEO: Optimized for Luma (Camera movement focusing on character action)
        MUSIC: Optimized for Suno (Mood fitting the scene)
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
        topic = st.text_input("Story Topic", "ကျောပိုးအိတ်လွယ်ပြီး ငိုနေတဲ့ ကြောင်လေး")
        if st.form_submit_button("Write Script"):
            with st.spinner("Writing human-like cat script..."):
                res = generate_visual_script(topic, selected_model)
                if res:
                    st.session_state.burmese_story = res
                    st.rerun()
    
    if st.session_state.burmese_story:
        st.session_state.burmese_story = st.text_area("Edit Script (Burmese):", st.session_state.burmese_story, height=300)
        if st.button("Next >"):
            st.session_state.step = 2
            st.rerun()

# STEP 2
elif st.session_state.step == 2:
    if not st.session_state.scenes_data:
        with st.spinner(f"Splitting into {num_scenes_input} scenes & creating prompts..."):
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
                st.markdown(f"**Action:** _{sc['text']}_")
                if st.button(f"Generate Preview {i+1}", key=f"b{i}"):
                    with st.spinner("Generating preview..."):
                        img = generate_preview_image(sc['prompt'])
                        if img: 
                            st.session_state.scenes_data[i]['img'] = img
                            st.rerun()
                if sc['img']: st.image(sc['img'])
            with c2:
                st.session_state.scenes_data[i]['prompt'] = st.text_area("Visual Prompt (English)", sc['prompt'], key=f"p{i}", height=150)

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
        with st.spinner("Finalizing prompts..."):
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
        c1.markdown(f"**Action:** _{item['text']}_")
        if item['img']: c1.image(item['img'], width=200)
        c2.text_area("Image Prompt (DALL-E/MJ)", item['p_img'], key=f"fi{i}")
        c2.text_area("Video Prompt (Luma/Runway)", item['p_vid'], key=f"fv{i}")
        c2.text_area("Music Prompt (Suno)", item['p_mus'], key=f"fm{i}")

    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()


