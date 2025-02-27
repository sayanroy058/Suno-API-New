import streamlit as st
import requests
import time

def generate_song(prompt, make_instrumental, wait_audio, model, suno_cookie=None):
    # API endpoint
    url = 'http://localhost:3000/api/generate'
    
    # Request headers
    headers = {}
    if suno_cookie:
        headers['Cookie'] = suno_cookie
    
    # Request payload
    payload = {
        "prompt": prompt,
        "make_instrumental": make_instrumental,
        "wait_audio": wait_audio,
        "model": model
    }
    
    # Send POST request
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200:
        st.error(f"Error: {response.status_code}")
        return None
    
    # Get the generation data
    data = response.json()
    st.info("Generation started...")
    
    # Get the IDs for checking status
    ids = f"{data[0]['id']},{data[1]['id']}"
    st.text(f"Generation IDs: {ids}")
    
    # Create a progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Poll for status
    for i in range(60):  # Maximum 5 minutes waiting time
        status_url = f'http://localhost:3000/api/get?ids={ids}'
        status_response = requests.get(status_url)
        status_data = status_response.json()
        
        # Add error handling for status data
        if not status_data or not isinstance(status_data, list) or len(status_data) == 0:
            st.error("Invalid response format from the API")
            return None
            
        # Check if the first item has a status field
        if 'status' not in status_data[0]:
            st.error("Status field not found in the API response")
            return None
            
        if status_data[0]['status'] == 'streaming':
            progress_bar.progress(100)
            status_text.text("Generation completed!")
            return status_data
        
        progress = min((i + 1) * 2, 99)  # Cap progress at 99% until complete
        progress_bar.progress(progress)
        status_text.text("Waiting for generation to complete...")
        time.sleep(5)
    
    st.error("Timeout: Generation took too long")
    return None

def main():
    st.title("Suno AI Song Generator")
    st.write("Generate unique songs using Suno AI")
    
    # Create input form
    with st.form("song_generator"):
        # Add cookie input field
        suno_cookie = st.text_input(
            "Suno Cookie (Optional)",
            "",
            help="Enter your Suno cookie to override the default one from .env file",
            type="password"
        )
        
        prompt = st.text_area(
            "Enter your song prompt",
            "A boy crying lonely in a rainy day night in hindi",
            help="Describe the song you want to generate"
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            make_instrumental = st.checkbox(
                "Make Instrumental",
                False,
                help="Generate an instrumental version"
            )
        with col2:
            wait_audio = st.checkbox(
                "Wait for Audio",
                False,
                help="Wait for audio generation to complete"
            )
        with col3:
            model = st.selectbox(
                "Select Model",
                ["chirp-v4", "chirp-v3-5", "chirp-v3-0"],
                help="Choose the model for generation"
            )
        
        submit_button = st.form_submit_button("Generate Song")
    
    if submit_button:
        with st.spinner("Generating your song..."):
            result = generate_song(prompt, make_instrumental, wait_audio, model, suno_cookie if suno_cookie else None)
            
            if result:
                st.success("🎵 Songs generated successfully!")
                
                # Display both versions with audio players and download links
                for i, version in enumerate(result, 1):
                    st.subheader(f"Version {i}")
                    audio_url = version['audio_url']
                    
                    # Display audio player
                    st.audio(audio_url)
                    
                    # Add download button
                    st.markdown(f"[Download Version {i}]({audio_url})")

if __name__ == "__main__":
    main()