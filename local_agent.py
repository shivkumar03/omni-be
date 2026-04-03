"""
OMNI Local Agent - runs on user's Windows PC (localhost:5001)
Handles all system commands that require local machine access.
Start this before using OMNI on the web.
"""
import os, subprocess, difflib, datetime, time, webbrowser, re
from flask import Flask, request, jsonify
from flask_cors import CORS

try:
    import pyautogui
    import pywhatkit as kit
    import screen_brightness_control as sbc
except Exception as e:
    print(f"[WARN] Some libraries missing: {e}")

app = Flask(__name__)
CORS(app, origins=["https://omnidashboard.co.in", "http://localhost:5173", "http://127.0.0.1:5173"])

APPS = {
    "spotify": "start spotify:", "chrome": "start chrome", "edge": "start msedge",
    "vscode": "code", "vs code": "code", "visual studio code": "code", "code": "code",
    "notepad": "notepad", "calculator": "calc", "calc": "calc",
    "camera": "start microsoft.windows.camera:", "settings": "start ms-settings:",
    "file explorer": "explorer", "explorer": "explorer", "task manager": "taskmgr",
    "word": "start winword", "excel": "start excel", "powerpoint": "start powerpnt",
    "outlook": "start outlook", "onenote": "start onenote", "teams": "start msteams",
    "onedrive": "start onedrive", "microsoft store": "start ms-windows-store:",
    "paint": "mspaint", "snipping tool": "snippingtool", "vlc": "vlc",
    "whatsapp": "start whatsapp:", "telegram": "start telegram", "zoom": "start zoom:",
    "skype": "start skype:", "firefox": "start firefox",
    "control panel": "control", "command prompt": "start cmd", "powershell": "start powershell",
}

PROCESSES = {
    "chrome": "chrome.exe", "edge": "msedge.exe", "firefox": "firefox.exe",
    "spotify": "Spotify.exe", "vscode": "Code.exe", "notepad": "notepad.exe",
    "calculator": "Calculator.exe", "task manager": "Taskmgr.exe",
    "word": "WINWORD.EXE", "excel": "EXCEL.EXE", "powerpoint": "POWERPNT.EXE",
    "outlook": "OUTLOOK.EXE", "teams": "Teams.exe", "onedrive": "OneDrive.exe",
    "paint": "mspaint.exe", "vlc": "vlc.exe", "whatsapp": "WhatsApp.exe",
    "telegram": "Telegram.exe", "zoom": "Zoom.exe", "skype": "Skype.exe",
    "powershell": "powershell.exe", "command prompt": "cmd.exe", "explorer": "explorer.exe",
}

SETTINGS_MAP = {
    "display": "ms-settings:display", "screen": "ms-settings:display",
    "brightness": "ms-settings:display", "sound": "ms-settings:sound",
    "bluetooth": "ms-settings:bluetooth", "wifi": "ms-settings:network-wifi",
    "network": "ms-settings:network", "power": "ms-settings:powersleep",
    "mouse": "ms-settings:mouse", "keyboard": "ms-settings:keyboard",
    "update": "ms-settings:windowsupdate", "apps": "ms-settings:appsfeatures",
    "themes": "ms-settings:themes", "background": "ms-settings:personalization-background",
    "settings": "ms-settings:",
}

@app.route("/system_command", methods=["POST"])
def system_command():
    try:
        text = request.json.get("command", "").lower().strip()

        # SHUTDOWN
        if "shutdown" in text:
            subprocess.Popen("shutdown /s /t 5", shell=True)
            return jsonify({"status": "Shutting down system in 5 seconds"})

        # RESTART
        if "restart" in text:
            subprocess.Popen("shutdown /r /t 5", shell=True)
            return jsonify({"status": "Restarting system in 5 seconds"})

        # LOCK
        if "lock" in text:
            subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True)
            return jsonify({"status": "System locked"})

        # VOLUME
        if "volume up" in text:
            for _ in range(5): pyautogui.press("volumeup")
            return jsonify({"status": "Volume increased"})
        if "volume down" in text:
            for _ in range(5): pyautogui.press("volumedown")
            return jsonify({"status": "Volume decreased"})
        if "mute" in text:
            pyautogui.press("volumemute")
            return jsonify({"status": "Muted"})

        # BRIGHTNESS
        if "brightness" in text:
            current = sbc.get_brightness(display=0)
            current = current[0] if isinstance(current, list) else current
            if "increase" in text:
                val = min(current + 20, 100)
            elif "decrease" in text:
                val = max(current - 20, 10)
            else:
                m = re.search(r'\d+', text)
                val = int(m.group()) if m else 70
                val = max(10, min(val, 100))
            sbc.set_brightness(val)
            return jsonify({"status": f"Brightness set to {val}%"})

        # MINIMIZE / MAXIMIZE
        if "minimize" in text:
            pyautogui.hotkey("win", "d")
            return jsonify({"status": "Minimized all windows"})
        if "maximize" in text:
            pyautogui.hotkey("win", "shift", "m")
            return jsonify({"status": "Restored all windows"})

        # WIFI
        if "wifi on" in text:
            subprocess.run('netsh interface set interface "Wi-Fi" enable', shell=True)
            return jsonify({"status": "WiFi enabled"})
        if "wifi off" in text:
            subprocess.run('netsh interface set interface "Wi-Fi" disable', shell=True)
            return jsonify({"status": "WiFi disabled"})

        # SETTINGS
        if "settings" in text:
            for key, uri in SETTINGS_MAP.items():
                if key in text:
                    os.startfile(uri)
                    return jsonify({"status": f"Opening {key} settings"})
            os.startfile("ms-settings:")
            return jsonify({"status": "Opening settings"})

        # CLOSE APP
        if "close" in text:
            app_name = text.replace("close", "").strip()
            match = difflib.get_close_matches(app_name, PROCESSES.keys(), n=1, cutoff=0.6)
            if match:
                subprocess.run(f'taskkill /f /im {PROCESSES[match[0]]}', shell=True)
                return jsonify({"status": f"Closed {match[0]}"})
            return jsonify({"status": f"No running app found for '{app_name}'"})

        # PLAY YOUTUBE
        if "play" in text:
            song = text.replace("play", "").replace("on youtube", "").replace("in youtube", "").strip()
            if song:
                try:
                    kit.playonyt(song)
                    time.sleep(5)
                    pyautogui.press("space")
                    return jsonify({"status": f"Playing {song} on YouTube"})
                except:
                    webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
                    return jsonify({"status": f"Showing results for {song}"})

        # OPEN APP or WEBSITE
        if "open" in text:
            app_name = text.replace("open", "").strip()
            # Try app first
            for key in APPS:
                if key in app_name:
                    subprocess.Popen(APPS[key], shell=True)
                    return jsonify({"status": f"Opening {key}"})
            match = difflib.get_close_matches(app_name, APPS.keys(), n=1, cutoff=0.6)
            if match:
                subprocess.Popen(APPS[match[0]], shell=True)
                return jsonify({"status": f"Opening {match[0]}"})
            # Fallback: open as website
            sites = {
                "youtube": "https://www.youtube.com",
                "google": "https://www.google.com",
                "github": "https://github.com",
                "instagram": "https://www.instagram.com",
                "facebook": "https://www.facebook.com",
                "twitter": "https://twitter.com",
                "linkedin": "https://www.linkedin.com",
                "netflix": "https://www.netflix.com",
                "amazon": "https://www.amazon.in",
                "flipkart": "https://www.flipkart.com",
                "whatsapp web": "https://web.whatsapp.com",
                "gmail": "https://mail.google.com",
                "google drive": "https://drive.google.com",
                "google maps": "https://maps.google.com",
                "chatgpt": "https://chat.openai.com",
                "spotify": "https://open.spotify.com",
                "reddit": "https://www.reddit.com",
                "wikipedia": "https://www.wikipedia.org",
                "stack overflow": "https://stackoverflow.com",
                "leetcode": "https://leetcode.com",
                "geeksforgeeks": "https://www.geeksforgeeks.org",
                "canva": "https://www.canva.com",
                "figma": "https://www.figma.com",
                "notion": "https://www.notion.so",
                "swiggy": "https://www.swiggy.com",
                "zomato": "https://www.zomato.com",
                "hotstar": "https://www.hotstar.com",
                "prime video": "https://www.primevideo.com",
                "seeding minds": "https://seedingminds.co.in",
                "orcode": "https://orcode.co.in",
            }
            if app_name in sites:
                webbrowser.open(sites[app_name])
                return jsonify({"status": f"Opening {app_name}"})
            # domain like flipkart.com
            if re.match(r"^[\w\-]+\.[a-z]{2,}(\.[a-z]{2,})?$", app_name):
                webbrowser.open(f"https://{app_name}")
                return jsonify({"status": f"Opening {app_name}"})
            # generic fallback
            webbrowser.open(f"https://www.{app_name}.com")
            return jsonify({"status": f"Opening {app_name}"})

        return jsonify({"status": "Command not recognized locally"})

    except Exception as e:
        return jsonify({"status": f"Local agent error: {str(e)}"}), 500

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "mode": "windows"})

if __name__ == "__main__":
    print("=" * 50)
    print("  OMNI Local Agent running on port 5001")
    print("  Keep this running while using OMNI on web")
    print("=" * 50)
    app.run(port=5001, debug=False)
