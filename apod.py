import os
import urllib.request
import json

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


API_KEY = os.environ.get("NASA_API")
# Fallback values in case the API call drops entirely
title = "Cosmic Windows Lockscreen"
date_str = "Awaiting Sync"
explanation = "Connecting to NASA's deep space network. Your daily space update will populate momentarily."
hd_url = "https://unsplash.com" # High-res space backup image
media_type = "image"

if not API_KEY:
    print("Error: NASA_API environment variable not set.")
    exit(1)

URL = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"
print("Fetching today's cosmic data from NASA...")

try:
    with urllib.request.urlopen(URL) as response:
        if response.status == 200:
            raw_data = response.read().decode("utf-8")
            data = json.loads(raw_data)

            title = data.get('title', 'Cosmic View')
            date_str = data.get('date', '')
            explanation = data.get('explanation', '')
            media_url = data.get('url', '')
            hd_url = data.get('hdurl', media_url)
            media_type = data.get('media_type', 'image')

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
            width: 100vw;
            height: 100vh;
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
                html_content += f"""<script>document.getElementById('bg-container').style.backgroundImage = "url('{hd_url}')";</script>"""
            elif media_type == 'video':
                embed_url = media_url.replace("watch?v=", "embed/")
                html_content += f"""<iframe src="{embed_url}?autoplay=1&mute=1&loop=1&controls=0" frameborder="0" allow='"autoplay"></iframe>"""

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
            print(f"Failed to fetch data. NASA Status code: {response.status_code}")

except Exception as e:
    print(f"An error occurred: {e}")
