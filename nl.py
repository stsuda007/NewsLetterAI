import streamlit as st
import os
import requests
import json
from datetime import datetime

# API configurations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")  # For Gemini

# Set page title and configuration
st.set_page_config(page_title="Multi-LLM Newsletter Generator", layout="wide")

def load_prompt_template():
    """Load the prompt template from prompt_for_newsletter.txt"""
    try:
        with open("prompt_for_newsletter.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.error("prompt_for_newsletter.txt file not found. Please create this file with your prompt template.")
        return ""

# Function to create final prompt by inserting user input into template
def create_final_prompt(user_input, prompt_template):
    """Insert user input into the prompt template"""
    if "{user_input}" in prompt_template:
        return prompt_template.replace("{user_input}", user_input)
    else:
        # Fallback if no placeholder exists
        return f"{prompt_template}\n\nUSER INPUT:\n{user_input}"

# Function to generate newsletter with OpenAI
def generate_with_openai(final_prompt):
    if not OPENAI_API_KEY:
        return "⚠️ OpenAI API key not found. Please add it to your environment variables."
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        payload = {
            "model": "gpt-4-turbo",
            "messages": [{"role": "user", "content": final_prompt}],
            "temperature": 0.5,
            "max_tokens": 2000
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code}, {response.text}"
    
    except Exception as e:
        return f"Error generating with OpenAI: {str(e)}"

# Function to generate newsletter with Anthropic (Claude)
def generate_with_anthropic(final_prompt):
    if not ANTHROPIC_API_KEY:
        return "⚠️ Anthropic API key not found. Please add it to your environment variables."
    
    try:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 2000,
            "temperature": 0.5,
            "messages": [{"role": "user", "content": final_prompt}]
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            return f"Error: {response.status_code}, {response.text}"
    
    except Exception as e:
        return f"Error generating with Anthropic: {str(e)}"

# Function to generate newsletter with Google Gemini
def generate_with_gemini(final_prompt):
    if not GOOGLE_API_KEY:
        return "⚠️ Google API key not found. Please add it to your environment variables."
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GOOGLE_API_KEY}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": final_prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.5,
                "maxOutputTokens": 2000
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error: {response.status_code}, {response.text}"
    
    except Exception as e:
        return f"Error generating with Gemini: {str(e)}"

# App title and description
st.title("🗞️ Multi-LLM Newsletter Generator")
st.markdown("Generate newsletters using multiple AI providers side by side")

# Load prompt template
prompt_template = load_prompt_template()

# API key input in sidebar (optional - can use env vars instead)
with st.sidebar:
    st.subheader("API Configuration")
    use_env_vars = st.checkbox("Use environment variables for API keys", value=True)
    
    if not use_env_vars:
        input_openai_key = st.text_input("OpenAI API Key", value=OPENAI_API_KEY, type="password")
        input_anthropic_key = st.text_input("Anthropic API Key", value=ANTHROPIC_API_KEY, type="password")
        input_google_key = st.text_input("Google API Key", value=GOOGLE_API_KEY, type="password")
        
        # Update API keys if manually entered
        OPENAI_API_KEY = input_openai_key
        ANTHROPIC_API_KEY = input_anthropic_key
        GOOGLE_API_KEY = input_google_key
    
    # Display prompt template
    st.subheader("Prompt Template")
    if prompt_template:
        st.text_area("Template from prompt_for_newsletter.txt:", prompt_template, height=300, disabled=True)
    else:
        st.warning("No prompt template found. Please create a prompt_for_newsletter.txt file.")

# Main input area
user_input = st.text_area("Enter your newsletter content ideas:", height=200, 
                         placeholder="Enter the key points you want to include in your newsletter...")

# Toggle switches for LLM providers
st.subheader("Choose LLM Providers")
col1, col2, col3 = st.columns(3)

with col1:
    use_openai = st.toggle("OpenAI (GPT-4)", value=True)
with col2:
    use_anthropic = st.toggle("Anthropic (Claude)", value=True)
with col3:
    use_gemini = st.toggle("Google (Gemini)", value=True)

# Generate button
if st.button("Generate Newsletter"):
    if user_input:
        if not prompt_template:
            st.error("Prompt template not found. Please create a prompt_for_newsletter.txt file.")
        elif not (use_openai or use_anthropic or use_gemini):
            st.error("Please enable at least one LLM provider.")
        else:
            # Create the final prompt by inserting user input into the template
            final_prompt = create_final_prompt(user_input, prompt_template)
            
            # Display the final prompt in a collapsible section
            with st.expander("View Final Prompt"):
                st.text_area("Final prompt sent to AI models:", final_prompt, height=300, disabled=True)
            
            # Create columns for results
            num_enabled = sum([use_openai, use_anthropic, use_gemini])
            result_cols = st.columns(num_enabled)
            
            col_index = 0
            
            # OpenAI generation
            if use_openai:
                with result_cols[col_index]:
                    st.subheader("OpenAI (GPT-4)")
                    with st.spinner("Generating with OpenAI..."):
                        openai_content = generate_with_openai(final_prompt)
                        st.markdown(openai_content)
                        
                        # Add download button
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="Download OpenAI Newsletter",
                            data=openai_content,
                            file_name=f"openai_newsletter_{timestamp}.md",
                            mime="text/markdown"
                        )
                col_index += 1
            
            # Anthropic generation
            if use_anthropic:
                with result_cols[col_index]:
                    st.subheader("Anthropic (Claude)")
                    with st.spinner("Generating with Anthropic..."):
                        anthropic_content = generate_with_anthropic(final_prompt)
                        st.markdown(anthropic_content)
                        
                        # Add download button
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="Download Claude Newsletter",
                            data=anthropic_content,
                            file_name=f"claude_newsletter_{timestamp}.md",
                            mime="text/markdown"
                        )
                col_index += 1
            
            # Gemini generation
            if use_gemini:
                with result_cols[col_index]:
                    st.subheader("Google (Gemini)")
                    with st.spinner("Generating with Gemini..."):
                        gemini_content = generate_with_gemini(final_prompt)
                        st.markdown(gemini_content)
                        
                        # Add download button
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="Download Gemini Newsletter",
                            data=gemini_content,
                            file_name=f"gemini_newsletter_{timestamp}.md",
                            mime="text/markdown"
                        )
    else:
        st.error("Please enter some content to generate a newsletter.")

# Instructions section
#st.markdown("---")
#st.subheader("How to use this app")
#st.markdown("""
#1. Create a file named `prompt_for_newsletter.txt` with your complete prompt template
#2. Include a placeholder `{user_input}` in your prompt template where the user's content should be inserted
#3. Set up your API keys as environment variables or input them in the sidebar
#4. Enter your content ideas in the text area above
#5. Toggle which AI providers you want to use
#6. Click 'Generate Newsletter' to create your newsletters side by side
#7. Download any newsletters you like using the download buttons
#""")

# Example prompt template
#st.markdown("---")
#st.subheader("Example Prompt Template")
#st.code("""
#Generate a professional newsletter based on the following input:

#USER INPUT:
#{user_input}

#Please follow these guidelines:
#1. Use a friendly but professional tone
#2. Include a catchy headline
#3. Organize content into clear sections
#4. Keep paragraphs short and scannable
#5. Include a call to action at the end

#Here are some examples of our previous newsletters for style reference:

# Example Newsletter - January 2025
#Dear subscribers,
#...

# Example Newsletter - February 2025
#Hello everyone,
#...
#""")

# Setup instructions 
#st.markdown("---")
#st.subheader("Environment Setup")
#st.code("""
# Install required packages:
#pip install streamlit requests python-dotenv

# Set environment variables in a .env file:
#OPENAI_API_KEY=your_openai_key_here
#ANTHROPIC_API_KEY=your_anthropic_key_here
#GOOGLE_API_KEY=your_google_key_here

# Run the app:
streamlit run newsletter_app.py

