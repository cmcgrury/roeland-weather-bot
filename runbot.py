from datetime import datetime
from zoneinfo import ZoneInfo
import subprocess
import sys

shutdown_start = 22
shutdown_end = 6

now_ct = datetime.now(ZoneInfo("America/Chicago"))
current_hour = now_ct.hour

print(f"Current Central Time: {now_ct.strftime('%Y-%m-%d %H:%M:%S')}")

if current_hour >= shutdown_start or current_hour < shutdown_end:
    print("Bot is in sleep mode — shutting down.")
    sys.exit()

subprocess.run(["python", "main.py"])
