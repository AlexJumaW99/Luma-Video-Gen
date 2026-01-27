import os
from pathlib import Path
from dotenv import load_dotenv
from lumaai import LumaAI
import requests 
import time


# 1. Locate the .env file in the sibling directory
# Get the directory where this script is located
current_script_dir = Path(__file__).resolve().parent


# Navigate up to the parent directory, then down into the sibling folder
# REPLACE 'your_sibling_folder' with the actual name of the folder containing your .env file
sibling_env_path = current_script_dir.parent / "env" / ".env"


# 2. Load the environment variables
if sibling_env_path.exists():
    load_dotenv(dotenv_path=sibling_env_path)
    print(f"Loaded environment variables from: {sibling_env_path}")
else:
    print(f"Warning: .env file not found at {sibling_env_path}")


# 3. Initialize the Client
# The SDK will now find the loaded LUMAAI_API_KEY in os.environ
client = LumaAI(
    auth_token=os.environ.get("LUMAAI_API_KEY")
)

# 4. Define key details such as the prompt_text, 
# and url links posting to the reference .png images,
# that are used to add a custom: character face, and still pose. 

# Replace this with the direct URL to your 'pose.png'
# If you can merge face.png onto pose.png beforehand, use that image here for 100% face accuracy.
pose_image_url = "https://your-public-url.com/pose.png"

prompt_text = (
    "Camera motion: Smooth 360-degree orbit around the subject. "
    "Subject: A hyper-realistic Pharaoh standing in a frozen, statue-like pose. "
    "The subject is completely motionless and still, exhibiting no movement. "
    "Wearing a Nemes crown and full royal golden regalia. "
    "Environment: Vast Sahara desert, sand dunes, three pyramids visible in the distance. "
    "Style: Photorealistic, Unreal Engine 5, 8k resolution, cinematic lighting."
)


# 4. Generate the Video
try:
    generation = client.generations.create(
        # 'ray-2' is the current standard for high-quality video
        model="ray-2",
        
        aspect_ratio="16:9",
        
        # 'loop' forces the start and end to match, creating a perfect orbit
        loop=True, 
        prompt=prompt_text,
        resolution="1080p",
        duration="9s",
        
        #the keyframes parameter allows users to enter images to use as reference in video generation, add or omit as needed. 
        keyframes={
            "frame0": {
                "type": "image",
                "url": "pose_image_url"
            }
        }
    )
    
    print(f"Generation started successfully! ID: {generation.id}")

except Exception as e:
    print(f"An error occurred during generation: {e}")
    

# 5. Check the status of the video generation
try:
    completed = False
    while not completed:
        generation = client.generations.get(id=generation.id)
        if generation.state == "completed":
            completed = True
        elif generation.state == "failed":
            raise RuntimeError(f"Generation failed: {generation.failure_reason}")
        print("Dreaming")
        time.sleep(3)
        
except Exception as e:
    print(f"An error occurred during periodic status checks: {e}")
    
    
# 6. Download completed video generation
video_url = generation.assets.video

try:
    # download the video
    response = requests.get(video_url, stream=True)
    with open(f'{generation.id}.mp4', 'wb') as file:
        file.write(response.content)
    print(f"File downloaded as {generation.id}.mp4")
    
except Exception as e:
    print(f"An error occurred during the download process: {e}")
    

    

    