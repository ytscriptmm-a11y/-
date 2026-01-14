import streamlit as st
import google.generativeai as genai
import time

# 1. Page Configuration
st.set_page_config(page_title="Silent Cat Movie Maker", layout="wide")
st.title("🐱 Silent Cat Movie Maker (Visual Script Only)")

# 2. API Key Setup
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

# --- SIDEBAR SETTINGS (ဒီအပိုင်း အရေးကြီးပါတယ်) ---
st.sidebar.header("⚙️ Settings")

# User's Custom Model List
text_model_options = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "models/gemini-2.5-pro",
    "models/gemini-3-flash-preview",
    "models/gemini-3-pro-preview"
]
selected_model = st.sidebar.selectbox("Select Model:", model_options, index=0)

# Scene Count Slider (ဒီကောင်ပျောက်နေလို့ Error တက်တာပါ - အခုပြန်ထည့်ထားပါတယ်)
num_scenes_input = st.sidebar.slider("Scene အရေအတွက် (ပုံအရေအတွက်)", 4, 15, 8)

st.sidebar.info("Note: No Audio (TTS) - Visual Script Only")

# 3. Session State Initialization
if 'step' not in st.session_state: st.session_state.step = 1
if 'burmese_story' not in st.session_state: st.session_state.burmese_story = ""
if 'scenes_data' not in st.session_state: st.session_state.scenes_data = [] 
if 'final_data' not in st.session_state: st.session_state.final_data = []

# --- Functions ---

def generate_visual_script(topic, model_name):
    """Step 1: Silent Movie Script (No Dialogue)"""
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        You are a Video Scriptwriter for a viral 'Silent Cat Movie'.
        Topic: '{topic}'

        Rules:
        1. NO Dialogue. NO Narration.
        2. Focus ONLY on Visual Actions (Body language, expressions, environment).
        3. Language: Write the visual description in Burmese.
        4. Length: Create enough content for a 3-minute video.
        5. Style: Show, Don't Tell.

        Output: Just write the visual story flow in Burmese paragraphs.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error with {model_name}: {e}")
        return None

def generate_scene_breakdown(script_text, model_name, scene_count):
    """Step 2: Breakdown into Scenes with Image Prompts"""
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Visual Script (Burmese): 
        "{script_text}"
        
        Task:
        1. Split this script into exactly {scene_count} distinct scenes.
        2. For each scene, provide the Burmese Visual Action text.
        3. For each scene, write an English Image Prompt (3D Pixar style cat).
        
        Output format strictly like this:
        Burmese: [Visual Action Text]
        English_Prompt: [Image Prompt]
        ###
        Burmese: [Next Action Text]
        English_Prompt: [Next Image Prompt]
        ###
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def generate_preview_image(prompt):
    """Image Preview (Requires google-generativeai>=0.8.3)"""
    try:
        # Using Imagen 3 via Gemini API
        model = genai.GenerativeModel("imagen-3.0-generate-001")
        result = model.generate_images(
            prompt=prompt + ", 3D render, cute cat, high quality, masterpiece",
            number_of_images=1,
        )
        return result.images[0]
    except Exception as e:
        # Fallback if specific model name fails
        try:
             model = genai.GenerativeModel("models/gemini-3-pro-image-preview")
             result = model.generate_images(prompt=prompt, number_of_images=1)
             return result.images[0]
        except Exception as e2:
            st.warning(f"Image Error: {e2}")
            return None

def generate_final_3_prompts(image_prompt, model_name):
    """Step 3: Platform Specific Prompts"""
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Based on: "{image_prompt}"
        Generate 3 prompts:
        IMAGE: Optimized for DALL-E 3
        VIDEO: Optimized for Luma Dream Machine (Camera movement, action)
        MUSIC: Optimized for Suno AI (Mood, instruments)
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

# Progress Bar
steps = ["၁. Visual Script ရေး", "၂. Scene ခွဲ & Preview", "၃. Final Output"]
current_progress = (st.session_state.step / 3)
st.progress(current_progress)
st.subheader(f"အဆင့် {st.session_state.step}: {steps[st.session_state.step-1]}")

# ----------------------------------------------------------------
# STEP 1: Script Generation
# ----------------------------------------------------------------
if st.session_state.step == 1:
    with st.form("step1_form"):
        topic = st.text_input("ဇာတ်လမ်းခေါင်းစဉ်", "မိုးရွာထဲ ကျန်ခဲ့တဲ့ ကြောင်လေး")
        submitted = st.form_submit_button("Visual Script ရေးသားရန်")
        
        if submitted:
            with st.spinner(f"Writing silent movie script..."):
                story = generate_visual_script(topic, selected_model)
                if story:
                    st.session_state.burmese_story = story
                    st.rerun()

    if st.session_state.burmese_story:
        st.info("အောက်ပါ Visual Script ကို ဖတ်ရှုပြင်ဆင်ပါ။")
        edited_story = st.text_area("Visual Script (Burmese)", st.session_state.burmese_story, height=300)
        st.session_state.burmese_story = edited_story
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Next Step >"):
                st.session_state.step = 2
                st.rerun()

# ----------------------------------------------------------------
# STEP 2: Breakdown & Image Preview
# ----------------------------------------------------------------
elif st.session_state.step == 2:
    if not st.session_state.scenes_data:
        # Fixed: Using variable from sidebar
        with st.spinner(f"Breaking down into {num_scenes_input} scenes..."):
            raw_data = generate_scene_breakdown(st.session_state.burmese_story, selected_model, num_scenes_input)
            if raw_data:
                scenes = raw_data.split('###')
                parsed_scenes = []
                for scene in scenes:
                    if "Burmese:" in scene:
                        lines = scene.strip().split('\n')
                        burmese_text = ""
                        eng_prompt = ""
                        for line in lines:
                            if "Burmese:" in line: burmese_text = line.replace("Burmese:", "").strip()
                            if "English_Prompt:" in line: eng_prompt = line.replace("English_Prompt:", "").strip()
                        
                        if burmese_text:
                            # No Audio
                            parsed_scenes.append({"text": burmese_text, "prompt": eng_prompt, "preview_img": None})
                st.session_state.scenes_data = parsed_scenes
                st.rerun()

    st.info("Scene တစ်ခုချင်းစီကို စစ်ဆေးပါ။ 'Generate Preview' နှိပ်၍ ပုံစမ်းထုတ်ကြည့်ပါ။")

    for i, scene in enumerate(st.session_state.scenes_data):
        with st.expander(f"Scene {i+1}", expanded=True):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown("**Visual Action:**")
                st.write(f"_{scene['text']}_")
                
                # Image Preview Button
                if st.button(f"Generate Preview 🖼️", key=f"btn_img_{i}"):
                    with st.spinner("Generating Image..."):
                        img = generate_preview_image(scene['prompt'])
                        if img:
                            st.session_state.scenes_data[i]['preview_img'] = img
                            st.rerun()
                
                if scene['preview_img']:
                    st.image(scene['preview_img'], use_container_width=True)

            with c2:
                new_p = st.text_area(f"Visual Prompt (English)", scene['prompt'], key=f"p_{i}", height=120)
                st.session_state.scenes_data[i]['prompt'] = new_p

    c1, c2 = st.columns(2)
    with c1:
        if st.button("< Back to Script"):
            st.session_state.step = 1
            st.session_state.scenes_data = [] 
            st.rerun()
    with c2:
        if st.button("Final Output ထုတ်မယ် >"):
            st.session_state.step = 3
            st.rerun()

# ----------------------------------------------------------------
# STEP 3: Final Output
# ----------------------------------------------------------------
elif st.session_state.step == 3:
    if not st.session_state.final_data:
        with st.spinner("Creating Prompts for Image, Video & Music..."):
            final_results = []
            for scene in st.session_state.scenes_data:
                res = generate_final_3_prompts(scene['prompt'], selected_model)
                p_img, p_vid, p_mus = "", "", ""
                if res:
                    for line in res.split('\n'):
                        if "IMAGE:" in line: p_img = line.replace("IMAGE:", "").strip()
                        if "VIDEO:" in line: p_vid = line.replace("VIDEO:", "").strip()
                        if "MUSIC:" in line: p_mus = line.replace("MUSIC:", "").strip()
                final_results.append({**scene, "p_img": p_img, "p_vid": p_vid, "p_mus": p_mus})
            st.session_state.final_data = final_results
            st.rerun()

    st.success("🎉 Final Prompts for your Video Creation")

    for i, item in enumerate(st.session_state.final_data):
        st.divider()
        st.subheader(f"Scene {i+1}")
        
        c_left, c_right = st.columns([1,2])
        with c_left:
             st.markdown("**Visual Action:**")
             st.info(item['text'])
             if item.get('preview_img'):
                 st.image(item['preview_img'], width=200)

        with c_right:
            st.text_area("🖼️ Image Prompt", item['p_img'], key=f"img_{i}")
            st.text_area("🎥 Video Prompt", item['p_vid'], key=f"vid_{i}")
            st.text_area("🎵 Music Prompt", item['p_mus'], key=f"mus_{i}")

    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()
