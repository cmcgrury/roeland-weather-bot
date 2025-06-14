import datetime
import subprocess
import sys

# Set your quiet hours (UTC)
shutdown_start = 2   # 2 AM UTC
shutdown_end = 6     # 6 AM UTC

# Get current UTC hour
current_hour = datetime.datetime.utcnow().hour

# Exit if current time is within shutdown range
if shutdown_start <= current_hour < shutdown_end:
    print("Bot is in sleep mode — exiting to save Railway usage.")
    sys.exit()

# Otherwise, start the main bot
subprocess.run(["python", "main.py"])
