import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from lumaai import LumaAI
import requests 
import time

# --- Configuration ---
# 1. Setup Paths
# We use the current script directory as the base, just like list_allowed_concepts.py
current_script_dir = Path(__file__).resolve().parent
output_dir = current_script_dir / "merged_reference_images"
env_path = current_script_dir / "env" / ".env"

# Ensure output directory exists to save the result
output_dir.mkdir(parents=True, exist_ok=True)

# 2. Load Environment Variables
# Using the same logic that worked in your reference file
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Fallback: Just try loading without a path (searches CWD) or print explicit warning
    print(f"Warning: .env file not found at {env_path}")
    load_dotenv() 

# 3. Initialize Client
api_key = os.getenv("LUMA_API_KEY")
if not api_key:
    raise ValueError(f"API Key not found. Checked path: {env_path}")

client = LumaAI(auth_token=api_key)


# 4. Define key details such as the video_prompt, 
# and url links posting to the reference .png images,
# that are used to add a custom: character face, and still pose. 

# Replace this with the direct URL to your 'pose.png'
# If you can merge face.png onto pose.png beforehand, use that image here for 100% face accuracy.

# have start and end keyframes so not needed for now
# pose_image_url = "https://i.postimg.cc/FHrY4dP5/awesome-pharaoh.png"

start_image_url = "https://i.postimg.cc/FHrY4dP5/awesome-pharaoh.png"
end_image_url = "https://i.postimg.cc/yxxLtYwp/awesome-pharaoh-backside.png"

video_prompt = (
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
        # since loop does not support start and end (multiple) keyframes however, we will change it to False for now
        # it does not support multiple keyframes because loop=True implies start and end frame are the same
        # remember, we can always loop using CapCut
        loop=True, 
        prompt=video_prompt,
        resolution="1080p",
        duration="9s",
        concepts=[
            {
                "key": "orbit_left"
            },
            {
                "key": "eye_level" 
            }
        ],
        
        #the keyframes parameter allows users to enter images to use as reference in video generation, add or omit as needed. 
        keyframes={
            "frame0": {
                "type": "image",
                "url": start_image_url
            },
            # "frame1": {
            #     "type": "image",
            #     "url": end_image_url   
            # }
        }
    )
    
    print(f"Generation started successfully! ID: {generation.id}")

except Exception as e:
    print(f"An error occurred during generation: {e}")
    sys.exit(1) # Stop the script here so you don't get errors later for trying to check the status of a non-existent generated video
    

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
    sys.exit(1) # Stop the script here so you don't get errors later for trying to download a non-existent generated video
    
    
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
    

    

    