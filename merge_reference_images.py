import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from lumaai import LumaAI

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

# --- INPUTS ---
# Replace these with your actual hosted URLs
face_image_url = "https://i.postimg.cc/Y2WQSFtw/face.png"
pose_image_url = "https://i.postimg.cc/449p3cX4/pose.png"

# --- THE PROMPT ---
# Derived from your prompt.txt, but optimized for a STILL image (removed camera motion)
# Changes made:
# 1. Added "Three-quarter angle" and "facing Southeast" to rotate the subject.
# 2. Added "Full body wide shot" and "centered" to ensure visibility.
# 3. Added "Depth of field" and "bokeh" for background blur.
image_prompt = (
    "Subject: A full-body wide shot of a hyper-realistic Pharaoh standing in a statue-like pose. "
    "He is turned at a three-quarter angle, facing Southeast (looking diagonally towards the camera's right). "
    "The subject is perfectly centered with his entire figure visible from head to toe. "
    "He is wearing a Nemes crown and full royal golden regalia. "
    "Environment: The vast Sahara desert with endless sand dunes. "
    "Style: Shallow depth of field with a soft background blur (bokeh) to isolate the subject. "
    "Cinematic photorealistic lighting, rendered in the style of Unreal Engine 5, 8k resolution."
)

def bake_character_image():
    print(f"Starting Image Generation with Model: photon-1")
    print(f"   - Identity Source: {face_image_url}")
    print(f"   - Pose Source: {pose_image_url}")

    try:
        # 1. Call the Image API
        # We use 'photon-1' for high-fidelity image synthesis
        generation = client.generations.image.create(
            prompt=image_prompt,
            model="photon-1",
            
            # CHANGED: Switched to 9:16 (Portrait) to fit the "Full Body" better
            aspect_ratio="9:16",            
            
            # Character Reference: Locks the facial identity
            character_ref={
                "identity0": {
                    "images": [face_image_url]
                }
            },
            
            # Image Reference: Locks the composition/structure (the pose)
            # BEFORE: We use a high weight (0.85) to force the pose to match closely
            
            # AFTER: Lowered weight from 0.85 to 0.45.
            # High weight locks the angle to the input image. 
            # Lower weight allows the text prompt ("facing Southeast") to take effect.            
            image_ref=[
                {
                    "url": pose_image_url,
                    "weight": 0.45
                }
            ]
        )
        print(f"Generation started! ID: {generation.id}")

        # 2. Poll for Completion
        completed = False
        while not completed:
            gen_status = client.generations.get(id=generation.id)
            
            if gen_status.state == "completed":
                completed = True
                print("Image generation completed successfully.")
                
                # 3. Download and Save the Merged Image
                final_image_url = gen_status.assets.image
                save_path = output_dir / "merged_pharaoh.png"
                
                response = requests.get(final_image_url, stream=True)
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"SUCCESS: Merged image saved to: {save_path}")
                    print(f"URL: {final_image_url}")
                else:
                    print(f"Error downloading image: {response.status_code}")

            elif gen_status.state == "failed":
                raise RuntimeError(f"Generation failed: {gen_status.failure_reason}")
            
            else:
                print("Processing... (Dreaming)")
                time.sleep(3)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    bake_character_image()