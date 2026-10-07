import os
import urllib.request
import json
from datetime import datetime

# The upcoming open REST endpoint does not require API keys or secrets
URL = "https://nasa.gov"
print("Pulling the absolute latest live data directly from NASA's backend...")

try:
    # Set a User-Agent so NASA's server firewall doesn't drop the connection
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            raw_data = response.read().decode("utf-8")
            posts = json.loads(raw_data)

            if not posts or not isinstance(posts, list):
                print("Error: Invalid or empty response array received.")
                exit(1)
            
            # Extract the single newest object from the data stream
            post = posts[0]
            
            # Map values out of the updated schema framework
            title = post.get('title', 'Cosmic View')
            explanation = post.get('explanation', '')
            
            # Format and sanitize the standard date format string
            raw_date = post.get('date', '')
            date_str = raw_date.split('T')[0] if 'T' in raw_date else raw_date
            
            # Grab the raw image source asset URL
            img_src = post.get('featured_media_src_url', '')
            
            # Check fallback configurations inside nested dictionary parameters
            if isinstance(post.get('apod'), dict):
                apod = post.get('apod')
                explanation = explanation or apod.get('explanation', '')
                img_src = img_src or apod.get('url')

            # Determine whether the asset is a video frame or standard image
            if 'youtube.com' in img_src or 'vimeo.com' in img_src or 'player.' in img_src:
                media_type = 'video'
            else:
                media_type = 'image'

            # Create a localized timestamp identifier string to force clear the browser's cache
            cache_buster = int(datetime.now().timestamp())

            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NASA Picture of the Day - {title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body, html {{ width: 100%; height: 100%; overflow: hidden; font-family: apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #000; }}

        #bg-container{{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            z-index: 1;
        }}

        #bg-container iframe {{
            width: 100vw;
            height: 100vh;
            pointer-events: none;}}

        #lockscreen-card {{
            position: absolute;
            bottom: 40px;
            left: 40px;
            z-index: 2;
            max-width: 420px;
            padding: 24px;
            color: #ffffff;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        }}

        #title{{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 4px;
        }}

        #date{{
           font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        #explanation-wrapper{{
            max-height: 200px;
            overflow-y: auto;
            padding-right: 8px;
        }}

        #explanation{{
            font-size: 0.95rem;
            line-height: 1.4;
            color: rgba(255, 255, 255, 0.9);
        }}

        #explanation-wrapper::-webkit-scrollbar {{
            width: 6px;
        }}

        #explanation-wrapper::-webkit-scrollbar-thumb {{
            background-color: rgba(255, 255, 255, 0.3);
            border-radius: 3px;
        }}
    </style>
    </head>
<body>
    <div id="bg-container">"""

            if media_type == 'image':
                html_content += f"""<script>document.getElementById('bg-container').style.backgroundImage = "url('{img_src}?v={cache_buster}')";</script>"""
            elif media_type == 'video':
                embed_url = img_src.replace("watch?v=", "embed/")
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

            print(f"Successfully generated future-proof index.html for date: {date_str}")
            print(f"Targeted Image Asset: {img_src}")
        else:
            print(f"Failed to fetch data. Status code: {response.status}")

except Exception as e:
    print(f"An error occurred: {e}")
