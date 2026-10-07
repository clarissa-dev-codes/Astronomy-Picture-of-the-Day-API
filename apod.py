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
img_src = "https://unsplash.com" 
media_type = "image"

# Fetch directly from the modern active content core stream
URL = "https://nasa.gov"
print("Connecting directly to the live production database feed...")

try:
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            raw_data = response.read().decode("utf-8")
            posts = json.loads(raw_data)

            if not posts or not isinstance(posts, list):
                print("Error: Invalid or empty response array received.")
                exit(1)
            
            # --- FIXED: Target the first post object inside the response list ---
            single_post = posts[0]

            print("--- RAW API RESPONSE FROM NASA ---")
            print(json.dumps(single_post, indent=2)) 
            print("----------------------------------")

            # Extract Title securely across both direct strings and rendered objects
            title_obj = single_post.get('title', 'Cosmic View')
            if isinstance(title_obj, dict):
                title = title_obj.get('rendered', 'Cosmic View')
            else:
                title = str(title_obj)

            # Sanitize Date
            raw_date = single_post.get('date', '')
            date_str = raw_date.split('T')[0] if 'T' in raw_date else raw_date
            
            # Extract description strings safely from custom post parameters
            explanation = single_post.get('explanation', '')
            if not explanation and isinstance(single_post.get('content'), dict):
                explanation = single_post.get('content', {}).get('rendered', '')

            # Gather asset URLs using sequential fallback mapping
            img_src = single_post.get('featured_media_src_url', '')
            
            if isinstance(single_post.get('apod'), dict):
                apod_data = single_post.get('apod')
                explanation = explanation or apod_data.get('explanation', '')
                img_src = apod_data.get('hdurl') or apod_data.get('url') or img_src

            # Emergency asset routing to keep things from going blank
            if not img_src or not isinstance(img_src, str) or img_src.strip() == "":
                img_src = "https://unsplash.com"

            # Determine whether the media asset is a video stream or traditional picture image
            if any(k in img_src for k in ['youtube.com', 'vimeo.com', 'player.', '.html', 'embed']):
                media_type = 'video'
            else:
                media_type = 'image'

            # Build HTML Layout (Fixed full screen structure viewport logic)
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NASA Picture of the Day - {title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body, html {{ width: 100%; height: 100%; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #050505; }}
        
        #bg-blur-layer {{
            position: fixed; top: -10%; left: -10%; width: 120vw; height: 120vh;
            background-size: cover; background-position: center;
            filter: blur(40px) brightness(0.4); z-index: 1; opacity: 0.75;
            display: {"block" if media_type == "image" else "none"};
        }}

        #bg-container {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background-size: contain; background-position: center; background-repeat: no-repeat; z-index: 2;
        }}
        
        /* Fixed iframe properties: forces video frames to consume the full viewport space */
        #bg-container iframe {{ 
            width: 100%; 
            height: 100%; 
            border: none;
            position: absolute;
            top: 0;
            left: 0;
        }}

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
                    document.getElementById('bg-blur-layer').style.backgroundImage = "url('{img_src}?v={cache_buster}')";
                    document.getElementById('bg-container').style.backgroundImage = "url('{img_src}?v={cache_buster}')";
                </script>"""

            elif media_type == 'video':
                # Convert watch layouts to clean embedded tracking configurations automatically
                embed_url = img_src.replace("watch?v=", "embed/") if "watch?v=" in img_src else img_src
                html_content += f"""<iframe src="{embed_url}?autoplay=1&mute=1&loop=1&controls=0" allow="autoplay; encrypted-media" allowfullscreen></iframe>"""

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

            print(f"Successfully compiled dynamic lock screen page into index.html for date: {date_str}")
        else:
            print(f"Failed to fetch data. NASA Status code: {response.status}")

except Exception as e:
    print(f"An error occurred: {e}")
