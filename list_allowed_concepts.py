import requests
import os
from dotenv import load_dotenv

# 1. Load API Key from env/.env
# We look for the 'env' folder relative to where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, 'env', '.env')
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv('LUMA_API_KEY')

# 2. Define the endpoint URL
url = "https://api.lumalabs.ai/dream-machine/v1/generations/concepts/list"

# 3. Set the required headers
headers = {
    "accept": "application/json",
    "authorization": f"Bearer {API_KEY}"
}

try:
    # 4. Make the GET request
    response = requests.get(url, headers=headers)
    
    # 5. Check if the request was successful
    response.raise_for_status()
    
    # 6. Parse and print the data
    concepts = response.json()
    
    print(f"Successfully retrieved {len(concepts)} concepts:")
    print("-" * 30)
    for concept in concepts:
        # The API typically returns a list of strings (e.g., 'zoom_in', 'orbit_left')
        print(f"- {concept}")

except requests.exceptions.RequestException as e:
    print(f"Error fetching concepts: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Status Code: {e.response.status_code}")
        print(f"Response Body: {e.response.text}")