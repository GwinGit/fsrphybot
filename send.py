from telegram import Bot, error
import logging
import json
from configparser import ConfigParser

# ---------- Message ----------
category_key = "Kat2"
text = "Eine Nachricht aus " + category_key
with_picture = True
picture_file = "pic.jpg"		# should be located in pictures/picture_file
# -----------------------------

config = ConfigParser()
config.read("config.ini")

API_KEY = config["General"]["api_key"]

category_names = config["Categories"]["category_names"].split(",")
category_keys = config["Categories"]["category_keys"].split(",")
category_name = category_names[category_keys.index(category_key)]

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
bot = Bot(token=API_KEY)

text = f"#{category_name}: " + text

with open("database", "r") as json_file:
	users = json.load(json_file)

for user in list(users.keys()):
	if users[user][category_key]:
		if with_picture:
			try:
				bot.send_photo(
					chat_id=user,
					photo=open(f"pictures/{picture_file}", "rb"),
					caption=text
				)
			except error.BadRequest:
				bot.send_photo(
					chat_id=user,
					photo=open(f"pictures/{picture_file}", "rb")
				)
				bot.send_message(
					chat_id=user,
					text=text
				)
		else:
			bot.send_message(
				chat_id=user,
				text=text
			)
