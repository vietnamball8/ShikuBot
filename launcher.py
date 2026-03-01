import subprocess
import os
import sys

# 1. Start your main bot
subprocess.Popen([sys.executable, 'main.py'])

# 2. Start everything in the 'scripts' folder
folder_path = './cogs' # Change this to your folder name
for filename in os.listdir(folder_path):
    if filename.endswith('.py'):
        file_path = os.path.join(folder_path, filename)
        subprocess.Popen([sys.executable, file_path])
        print(f"🚀 Launched {filename} from {folder_path}")

# Keep this script alive so Render stays "Live"
import time
while True:
    time.sleep(3600)
