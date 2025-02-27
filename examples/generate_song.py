import requests
import time

def generate_song():
    # API endpoint
    url = 'http://localhost:3000/api/generate'
    
    # Request payload
    payload = {
        "prompt": "A boy crying lonely in a rainy day night in hindi",
        "make_instrumental": False,
        "wait_audio": False
    }
    
    # Send POST request
    response = requests.post(url, json=payload)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    
    # Get the generation data
    data = response.json()
    print("Generation started...")
    
    # Get the IDs for checking status
    ids = f"{data[0]['id']},{data[1]['id']}"
    print(f"Generation IDs: {ids}")
    
    # Poll for status every 5 seconds
    for _ in range(60):  # Maximum 5 minutes waiting time
        status_url = f'http://localhost:3000/api/get?ids={ids}'
        status_response = requests.get(status_url)
        status_data = status_response.json()
        
        if status_data[0]['status'] == 'streaming':
            print("\nGeneration completed! Audio URLs:")
            print(f"Version 1: {status_data[0]['audio_url']}")
            print(f"Version 2: {status_data[1]['audio_url']}")
            return
        
        print("Waiting for generation to complete...")
        time.sleep(5)
    
    print("Timeout: Generation took too long")

if __name__ == '__main__':
    print("Starting Suno AI song generation...")
    generate_song()