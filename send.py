from telegram import Bot
import logging
import json
from configparser import ConfigParser

# ---------- Message ----------
category = "Kat2"
text = "Eine Nachricht aus " + category
# -----------------------------

config = ConfigParser()
config.read("config.ini")

API_KEY = config["General"]["api_key"]

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
bot = Bot(token=API_KEY)

with open("database", "r") as json_file:
	users = json.load(json_file)

for user in list(users.keys()):
	if users[user][category]:
		bot.send_message(
			chat_id=user,
			text=text
		)
