from telegram import Bot
import logging
import json
from configparser import ConfigParser
from time import sleep

# ---------- Message ----------
# category_key = "Kat2"
# text = "Eine Nachricht aus " + category_key
# -----------------------------

config = ConfigParser()
config.read("config.ini")

API_KEY = config["General"]["api_key"]
category_keys = config["Categories"]["category_keys"].split(",")

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
bot = Bot(token=API_KEY)

while True:
	with open("database", "r") as json_file:
		users = json.load(json_file)

	for category_key in category_keys:
		for user in list(users.keys()):
			if users[user][category_key]:
				bot.send_message(
					chat_id=user,
					text="Eine Nachricht aus " + category_key
				)

	sleep(60)
