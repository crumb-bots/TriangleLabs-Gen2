import subprocess, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

token = ""
status_type = "" # playing/listening/watching/streaming
status_text = "" # my DMs
bot_personality = """backstory goes here""" # backstory 
stream_link = "" # stream link

k = subprocess.Popen(["python3","Bot/bot.py",
    token,
    status_type.lower(),
    status_text,
    bot_personality, 
    "database", "1", stream_link])
input("press enter to stop bot...")
k.kill()