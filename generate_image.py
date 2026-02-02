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
my_image = "https://i.postimg.cc/ZK81NjrM/alexander16-9.png"
my_image_flipped = "https://i.postimg.cc/Kz5Vszsf/alexander-pharaoh-flipped.png"


# video_prompt = (
#     """
#     A bronze Pharaoh statue, Photorealistic Unreal Engine 5 animation style.
#     Orbit left quickly and smoothly along the circumference of a circle until one revolution is complete.
#     The facial and bodily features of the bronze statue should look consistent throughout the video as the camera orbits. 
#     """
# )

image_prompt = (
    "Massive ocean leviathan obliterates a warship in the frozen North Sea."
)


# 4. Generate the Video
try:
    generation = client.generations.create(
        # 'photon-flash-1' is the current standard for high-quality images
        model="photon-flash-1",
        
        aspect_ratio="16:9",
        
        # 'loop' forces the start and end to match, creating a perfect orbit
        # since loop does not support start and end (multiple) keyframes however, we will change it to False for now
        # it does not support multiple keyframes because loop=True implies start and end frame are the same
        # remember, we can always loop using CapCut
        image_ref=[
            {
                "url": "https://storage.cdn-luma.com/dream_machine/7e4fe07f-1dfd-4921-bc97-4bcf5adea39a/video_0_thumb.jpg",
                "weight": 0.85
            }
        ],
        
        style_ref=[
            {
                "url": "https://staging.storage.cdn-luma.com/dream_machine/400460d3-cc24-47ae-a015-d4d1c6296aba/38cc78d7-95aa-4e6e-b1ac-4123ce24725e_image0c73fa8a463114bf89e30892a301c532e.jpg",
                "weight": 0.8
            }
        ],
        
        character_ref={
            "identity0": {
                "images": [
                    "https://staging.storage.cdn-luma.com/dream_machine/400460d3-cc24-47ae-a015-d4d1c6296aba/38cc78d7-95aa-4e6e-b1ac-4123ce24725e_image0c73fa8a463114bf89e30892a301c532e.jpg"
                ]
            }
        },
        
        prompt=image_prompt,
        resolution="4k",
        duration="9s",
           
        
        #the keyframes parameter allows users to enter images to use as reference in video generation, add or omit as needed. 
         
    )
    
    print(f"Generation started successfully! ID: {generation.id}")

except Exception as e:
    print(f"An error occurred during generation: {e}")
    sys.exit(1) # Stop the script here so you don't get errors later for trying to check the status of a non-existent generated video
    

# 5. Check the status of the image generation
try:
    completed = False
    while not completed:
        generation = client.generations.get(id=generation.id)
        if generation.state == "completed":
            completed = True
        elif generation.state == "failed":
            raise RuntimeError(f"Generation failed: {generation.failure_reason}")
        print("Generating image...")
        time.sleep(3)
        
except Exception as e:
    print(f"An error occurred during periodic status checks: {e}")
    sys.exit(1) 
    
    
# 6. Download completed image generation
# CHANGE: Access the 'image' property instead of 'video'
image_url = generation.assets.image

try:
    # download the image
    response = requests.get(image_url, stream=True)
    
    # CHANGE: Save with a .jpg extension instead of .mp4
    # You can also use os.path.join(output_dir, ...) if you want to use the folder created in Step 1
    filename = f'{generation.id}.jpg'
    
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"File downloaded as {filename}")
    
except Exception as e:
    print(f"An error occurred during the download process: {e}")