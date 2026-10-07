import os
import urllib.request
import json

# Connecting directly to the modern active production database core stream
URL = "https://nasa.gov"
print("Connecting directly to NASA production stream...")

try:
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            raw_data = response.read().decode("utf-8")
            posts = json.loads(raw_data)

            if not posts or not isinstance(posts, list):
                print("Error: Invalid data format received.")
                exit(1)
            
            # Extract the raw current post object
            post_data = posts[0]

            # Save the clean raw data snapshot locally as a predictable data file
            with open("data.json", "w", encoding="utf-8") as json_file:
                json.dump(post_data, json_file, indent=4, ensure_ascii=False)

            print("Successfully refreshed data.json archive.")
        else:
            print(f"Failed to connect. Status code: {response.status}")
except Exception as e:
    print(f"Data collection pipeline error: {e}")
