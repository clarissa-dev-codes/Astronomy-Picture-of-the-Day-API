import os
import urllib.request
import json
from datetime import datetime
import time

# --- SECURE LOCAL TESTING FALLBACK ---
try:
    if os.path.exists(".env"):
        print("Local .env file detected. Extracting keys...")
        with open(".env", "r") as f:
            for line in f:
                cleaned_line = line.strip()
                if cleaned_line and not cleaned_line.startswith("#") and "=" in cleaned_line:
                    key, value = cleaned_line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
except Exception as fallback_err:
    print(f"Skipping .env parse (Running in cloud environment): {fallback_err}")
# -------------------------------------

# Fallback values in case the API call drops entirely
title = "Cosmic Windows Lockscreen"
date_str = "Awaiting Sync"
explanation = "Connecting to NASA's deep space network. Your daily space update will populate momentarily."
hd_url = "https://unsplash.com" # High-res space backup image
media_type = "image"

# NOTE: The new endpoint does not require an API key! It has completely open REST routes.
URL = "https://nasa.gov"
print("Fetching today's cosmic data from the new NASA platform...")

try:
    # Set a User-Agent so NASA's server firewall doesn't drop the Python stream connection
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            raw_data = response.read().decode("utf-8")
            posts = json.loads(raw_data)

            if not posts or not isinstance(posts, list):
                print("Error: Invalid or empty response array received.")
                exit(1)
            
            # --- CRITICAL FIX: Extract the first post dictionary from the list ---
            data = posts[0]

            print("--- RAW API RESPONSE FROM NASA ---")
            print(json.dumps(data, indent=2)) 
            print("----------------------------------")

            # Extract Title from the WordPress text rendering dictionary
            title_data = data.get('title', 'Cosmic View')
            if isinstance(title_data, dict):
                title = title_data.get('rendered', 'Cosmic View')
            else:
                title = str(title_data)

            # Sanitize Date
            raw_date = data.get('date', '')
            date_str = raw_date.split('T')[0] if 'T' in raw_date else raw_date
            
            # Pull Explanation out of the updated schema framework
            explanation = data.get('explanation', '')
            if not explanation and isinstance(data.get('content'), dict):
                explanation = data.get('content', {}).get('rendered', '')

            # --- TARGET MEDIA CHANNELS ACCURATELY ---
            # Extract asset source parameters from the flat WordPress payload
            img_src = data.get('featured_media_src_url', '')
            
            # Fallback checking: verify nested sub-dictionary keys if present
            if isinstance(data.get('apod'), dict):
                apod = data.get('apod')
                explanation = explanation or apod.get('explanation', '')
                img_src = img_src or apod.get('hdurl') or apod.get('url', '')

            # Classify media types securely 
            if 'youtube.com' in img_src or 'vimeo.com' in img_src or 'player.' in img_src or '.mp4' in img_src:
                media_type = 'video'
                media_url = img_src
            else:
                media_type = 'image'
                hd_url = img_src

            # Build HTML Layout (Windows Lock Screen Style with Full Containment)
            # [Your remaining html_content template string code stays exactly the same here]


            # Build HTML Layout (Windows Lock Screen Style with Full Containment)
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NASA Picture of the Day - {title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body, html {{ width: 100%; height: 100%; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #050505; }}
        
        /* Blurred mirrored layer behind the main image to prevent ugly empty black bars */
        #bg-blur-layer {{
            position: fixed; top: -10%; left: -10%; width: 120vw; height: 120vh;
            background-size: cover; background-position: center;
            filter: blur(40px) brightness(0.4); z-index: 1; opacity: 0.75;
        }}

        /* The Main Image container: Keeps the photo 100% visible and uncropped */
        #bg-container {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background-size: contain; background-position: center; background-repeat: no-repeat; z-index: 2;
        }}
        #bg-container iframe {{ width: 100vw; height: 100vh; pointer-events: none; }}

        #lockscreen-card {{
            position: absolute; bottom: 40px; left: 40px; z-index: 3; max-width: 420px; padding: 24px; color: #ffffff;
            background: rgba(0, 0, 0, 0.6); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.15); border-radius: 12px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
        }}
        #title {{ font-size: 1.4rem; font-weight: 600; margin-bottom: 4px; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }}
        #date {{ font-size: 0.85rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; }}
        #explanation-wrapper {{ max-height: 180px; overflow-y: auto; padding-right: 8px; }}
        #explanation {{ font-size: 0.95rem; line-height: 1.5; color: rgba(255, 255, 255, 0.9); }}
        #explanation-wrapper::-webkit-scrollbar {{ width: 4px; }}
        #explanation-wrapper::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.3); border-radius: 4px; }}
    </style>
</head>
<body>
    <div id="bg-blur-layer"></div>
    <div id="bg-container">"""

            if media_type == 'image':
                cache_buster = int(time.time())
                html_content += f"""<script>
                    document.getElementById('bg-blur-layer').style.backgroundImage = "url('{hd_url}?v={cache_buster}')";
                    document.getElementById('bg-container').style.backgroundImage = "url('{hd_url}?v={cache_buster}')";
                </script>"""

            elif media_type == 'video':
                embed_url = media_url.replace("watch?v=", "embed/")
                html_content += f"""<iframe src="{embed_url}?autoplay=1&mute=1&loop=1&controls=0" frameborder="0" allow="autoplay"></iframe>"""

            html_content += f""" </div>
            <main id="lockscreen-card">
                <div id="title">{title}</div>
                <div id="date">{date_str}</div>
                <div id="explanation-wrapper">
                    <div id="explanation">{explanation}</div>
                </div>
            </main>
</body>
</html>"""

            with open("index.html", "w", encoding="utf-8") as file:
                file.write(html_content)

            print("Successfully compiled dynamic lock screen page into index.html.")
        else:
            print(f"Failed to fetch data. NASA Status code: {response.status}")

except Exception as e:
    print(f"An error occurred: {e}")
