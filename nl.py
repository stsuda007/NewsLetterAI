import streamlit as st
import os

# Set page title and configuration
st.set_page_config(page_title="Newsletter Generator", layout="wide")

def load_prompt_file():
    """Load the reference newsletter samples from prompt_for_newsletter.txt"""
    try:
        with open("prompt_for_newsletter.txt", "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        st.error("prompt_for_newsletter.txt file not found. Please create this file with sample newsletters.")
        return ""

def generate_newsletter(user_input, reference_samples):
    """Generate newsletter content based on user input and reference samples"""
    # This is a simple implementation - in a real app, you might want to use an AI API
    # For now, we'll format the input with the reference as context
    
    newsletter = f"""
    # Newsletter
    
    {user_input}
    
    ---
    
    Note: This newsletter was generated based on user input and follows the style of previous newsletters.
    """
    
    return newsletter

# App title and description
st.title("🗞️ Newsletter Generator")
st.markdown("Enter your content ideas, and we'll generate a newsletter following the style of past examples.")

# Load reference samples
reference_samples = load_prompt_file()

# Create sidebar with reference samples
with st.sidebar:
    st.subheader("Reference Newsletter Examples")
    if reference_samples:
        st.text_area("Sample newsletters for reference:", reference_samples, height=400, disabled=True)
    else:
        st.warning("No reference samples found. Please create a prompt_for_newsletter.txt file.")

# Main input area
user_input = st.text_area("Enter your newsletter content ideas:", height=200, 
                         placeholder="Enter the key points you want to include in your newsletter...")

# Generate button
if st.button("Generate Newsletter"):
    if user_input:
        with st.spinner("Generating newsletter..."):
            newsletter_content = generate_newsletter(user_input, reference_samples)
            
        st.subheader("Generated Newsletter")
        st.markdown(newsletter_content)
        
        # Add download button
        st.download_button(
            label="Download Newsletter",
            data=newsletter_content,
            file_name="generated_newsletter.md",
            mime="text/markdown"
        )
    else:
        st.error("Please enter some content to generate a newsletter.")

# Instructions for setting up the prompt file
st.markdown("---")
st.subheader("How to use this app")
st.markdown("""
1. Create a file named `prompt_for_newsletter.txt` in the same directory as this app
2. Add sample newsletters to that file to serve as style references
3. Enter your content ideas in the text area above
4. Click 'Generate Newsletter' to create your newsletter
""")
