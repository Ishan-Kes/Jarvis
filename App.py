# This is a basic workflow to help you get started with Actions

name: CI

# Controls when the workflow will run
on:
  # Triggers the workflow on push or pull request events but only for the "main" branch
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

# A workflow run is made up of one or more jobs that can run sequentially or in parallel
jobs:
  # This workflow contains a single job called "build"
  build:
    # The type of runner that the job will run on
    runs-on: ubuntu-latest

    # Steps represent a sequence of tasks that will be executed as part of the job
    steps:
      # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
      - uses: actions/checkout@v4

      # Runs a single command using the runners shell
      - name: Run a one-line script
        run: echo Hello, world!

      # Runs a set of commands using the runners shell
      - name: Run a multi-line script
        run: |
          echo Add other actions to build,
          echo test, and deploy your project.
import os
import io
import csv
from datetime import datetime
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# ---------------------------------------------------------
# Page Configuration & Persona Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="JARVIS AI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 JARVIS AI Assistant")
st.write("Welcome back! I am JARVIS, your intelligent assistant.")

# System instruction defining JARVIS's role and expertise
SYSTEM_INSTRUCTION = (
    "You are JARVIS, an advanced AI assistant. "
    "You excel at answering science questions, explaining historical events/dates accurately, "
    "solving quizzes, and retrieving live, up-to-date web information whenever asked about current events."
)

# ---------------------------------------------------------
# Founder Configuration & Data Logging System
# ---------------------------------------------------------
# Founder security PIN (Change this passcode to whatever you prefer)
FOUNDER_PIN = "7860" 

LOG_FILE = "user_logs.csv"

def log_interaction(user_prompt: str, response_text: str):
    """Saves user query and JARVIS's answer into a local CSV log file for the founder."""
    file_exists = os.path.exists(LOG_FILE)
    try:
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "User Prompt", "JARVIS Response"])
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_prompt, response_text])
    except Exception as e:
        st.error(f"Failed to write log: {e}")

# ---------------------------------------------------------
# Sidebar Configuration & Controls
# ---------------------------------------------------------
st.sidebar.header("⚙️ JARVIS Controls")

api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.info("💡 Please enter your Gemini API Key in the sidebar to activate JARVIS.")
    st.stop()

# Initialize Google GenAI client
client = genai.Client(api_key=api_key)

# Mode Selector
mode = st.sidebar.radio("Select Functionality:", ["💬 Chat & Live Assistant", "🎨 Image Generator", "🔒 Founder Admin Portal"])

# Live Web Search Toggle
enable_web_search = st.sidebar.checkbox("🌐 Enable Live Web Search", value=True)

# ---------------------------------------------------------
# Sidebar Credits & Team Information
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏆 Project Credits")
st.sidebar.markdown("**Founder:**  \n👑 Ishan Kesharwani")
st.sidebar.markdown("**Team Members:**  \n👥 Devbramh Singh  \n👥 Ayush Vishwakarma  \n👥 Vinayak Pandey  \n👥 Aditya Pratap Singh")

# ---------------------------------------------------------
# Mode 1: Chat, Science, History & Live Search (Public Users)
# ---------------------------------------------------------
if mode == "💬 Chat & Live Assistant":
    st.subheader("Interactive Assistant (Science, History, Quizzes & Live Info)")

    # Initialize persistent chat history in session state for current browser session
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous chat messages in current session
    for msg in st.session_state.messages:
        avatar = "🤖" if msg["role"] == "JARVIS" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # User Input Field
    user_prompt = st.chat_input("Ask JARVIS anything...")

    if user_prompt:
        # Render User Message
        st.session_state.messages.append({"role": "User", "content": user_prompt})
        with st.chat_message("User", avatar="👤"):
            st.markdown(user_prompt)

        # Generate Response using Gemini API
        with st.chat_message("JARVIS", avatar="🤖"):
            with st.spinner("JARVIS is analyzing..."):
                try:
                    # Enable Google Search grounding if checkbox is selected
                    tools_list = [{"google_search": {}}] if enable_web_search else []

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            tools=tools_list
                        )
                    )
                    answer = response.text
                    st.markdown(answer)
                    
                    # Store message in session history
                    st.session_state.messages.append({"role": "JARVIS", "content": answer})
                    
                    # Log search to CSV file for the Founder
                    log_interaction(user_prompt, answer)

                except Exception as e:
                    st.error(f"Error communicating with JARVIS: {e}")

# ---------------------------------------------------------
# Mode 2: AI Image Generator (Imagen 3)
# ---------------------------------------------------------
elif mode == "🎨 Image Generator":
    st.subheader("JARVIS Image Generation Suite")

    image_prompt = st.text_area(
        "Describe the image you want JARVIS to generate:",
        placeholder="A futuristic city at sunset with flying cars, highly detailed, 4k resolution..."
    )
    
    if st.button("Generate Image"):
        if not image_prompt:
            st.warning("Please enter a description first.")
        else:
            with st.spinner("JARVIS is generating your image..."):
                try:
                    result = client.models.generate_images(
                        model="imagen-3.0-generate-002",
                        prompt=image_prompt,
                        config=types.GenerateImagesConfig(
                            number_of_images=1,
                            output_mime_type="image/jpeg",
                            aspect_ratio="1:1"
                        )
                    )

                    for generated_image in result.generated_images:
                        image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                        st.image(image, caption=image_prompt, use_column_width=True)
                        
                        # Log image generation event for Founder
                        log_interaction(f"[IMAGE GENERATION PROMPT]: {image_prompt}", "Image successfully generated.")

                except Exception as e:
                    st.error(f"Error generating image: {e}")

# ---------------------------------------------------------
# Mode 3: Locked Founder Admin Portal
# ---------------------------------------------------------
elif mode == "🔒 Founder Admin Portal":
    st.subheader("Founder Access Only")
    
    input_pin = st.text_input("Enter Founder Access Passcode:", type="password")

    if input_pin == FOUNDER_PIN:
        st.success("Access Granted! Welcome, Founder Ishan Kesharwani.")
        st.markdown("### 📊 All Recorded User Activity Logs")

        if os.path.exists(LOG_FILE):
            # Display logs on screen
            with open(LOG_FILE, mode="r", encoding="utf-8") as f:
                log_data = f.read()
                st.text_area("User Logs (`user_logs.csv`)", value=log_data, height=400)
            
            # Download button for Founder
            st.download_button(
                label="📥 Download Log File (CSV)",
                data=log_data,
                file_name="user_logs.csv",
                mime="text/csv"
            )
        else:
            st.info("No user activity recorded yet.")
    elif input_pin != "":
        st.error("Incorrect Passcode! Access Denied.")
