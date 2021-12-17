from telegram import Bot
import logging
import json
from configparser import ConfigParser
from time import sleep

# ---------- Message ----------
# categorie = "Kat2"
# text = "Eine Nachricht aus " + categorie
# -----------------------------

config = ConfigParser()
config.read("config.ini")

API_KEY = config["General"]["api_key"]

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
bot = Bot(token=API_KEY)

while True:
	with open("database", "r") as json_file:
	        users = json.load(json_file)


	for categorie in ["Kat1", "Kat2", "Kat3", "Kat4"]:
		for user in list(users.keys()):
			if users[user][categorie]:
				bot.send_message(chat_id=user, text="Eine Nachricht aus " + categorie)

	sleep(60)
