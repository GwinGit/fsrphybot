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
category_names = config["Categories"]["category_names"].split(",")
category_keys = config["Categories"]["category_keys"].split(",")

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
bot = Bot(token=API_KEY)


# Load users and their category subscriptions from the database
def load_database():
	with open("database", "r") as json_file:
		return json.load(json_file)


while True:
	users = load_database()
	for i in range(len(category_keys)):
		for user in list(users.keys()):
			if users[user][category_keys[i]]:
				bot.send_message(
					chat_id=user,
					text=f"#{category_names[i]}: Eine Nachricht aus {category_keys[i]}"
				)

	sleep(60)
