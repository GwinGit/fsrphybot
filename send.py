from telegram import Bot, error
import logging
import json
from configparser import ConfigParser

# ---------- Message ----------
category_key = "Kat2"
text = "Eine Nachricht aus " + category_key
with_picture = True
picture_file = "pic.jpg"		# should be located in pictures/picture_file
send_as_test = True				# if true, the message will only be send to the admins defined in the config
# -----------------------------


# Load users and their category subscriptions from the database
def load_database():
	with open("database", "r") as json_file:
		return json.load(json_file)


# Try to send a picture with a caption, if the caption is too long send the caption as a separate message
def send_photo_with_caption(chat_id, photo, caption):
	try:
		bot.send_photo(
			chat_id=chat_id,
			photo=photo,
			caption=caption
		)
	except error.BadRequest:
		bot.send_photo(
			chat_id=chat_id,
			photo=photo
		)
		bot.send_message(
			chat_id=chat_id,
			text=caption
		)


config = ConfigParser()
config.read("config.ini")

API_KEY = config["General"]["api_key"]
ADMIN_IDS = [int(admin_id) for admin_id in config["General"]["admin_ids"].split(",")]

category_names = config["Categories"]["category_names"].split(",")
category_keys = config["Categories"]["category_keys"].split(",")
category_name = category_names[category_keys.index(category_key)]

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
bot = Bot(token=API_KEY)

text = f"#{category_name}: " + text

if send_as_test:
	for admin_id in ADMIN_IDS:
		if with_picture:
			send_photo_with_caption(
				chat_id=admin_id,
				photo=open(f"pictures/{picture_file}", "rb"),
				caption=text
			)
		else:
			bot.send_message(
				chat_id=admin_id,
				text=text
			)
else:
	users = load_database()
	for user in list(users.keys()):
		# Check if the user is subscribed to the category
		if users[user][category_key]:
			if with_picture:
				send_photo_with_caption(
					chat_id=user,
					photo=open(f"pictures/{picture_file}", "rb"),
					caption=text
				)
			else:
				bot.send_message(
					chat_id=user,
					text=text
				)
