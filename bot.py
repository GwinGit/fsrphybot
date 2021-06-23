from telegram.ext import Updater, CommandHandler, PollAnswerHandler, MessageHandler, Filters
import logging
import json
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

API_KEY = config["General"]["api_key"]
ADMIN_IDS = [int(admin_id) for admin_id in config["General"]["admin_ids"].split(",")]

categorie_names = ["Kategorie 1", "Kategorie 2", "Kategorie 3", "Kategorie 4"]
categorie_keys = ["Kat1", "Kat2", "Kat3", "Kat4"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

updater = Updater(token=API_KEY)
dispatcher = updater.dispatcher


def start(update, context):
	chat_id = update.effective_chat.id
	with open("database", "r") as json_file:
		users = json.load(json_file)

	context.bot.send_message(chat_id=chat_id, text="Hier ist ein Willkommenstext!")

	if str(chat_id) in list(users.keys()):
		context.bot.send_message(chat_id=chat_id,
								text="Du schon bei diesem Bot angemeldet. Wenn du deine Präferenzen bearbeiten willt, "
									"kannst du das mit /abo tun.")
	else:
		users[str(chat_id)] = {key: False for key in categorie_keys}
		with open("database", "w") as json_file:
			json.dump(users, json_file)

		abo(update, context)


def abo(update, context):
	chat_id = update.effective_chat.id
	with open("database", "r") as json_file:
		users = json.load(json_file)

	if str(chat_id) in list(users.keys()):
		context.bot.send_poll(chat_id=chat_id,
							question="Aus welchen Kategorien möchtest du Nachrichten bekommen?",
							options=categorie_names, is_anonymous=False, allows_multiple_answers=True)
	else:
		start(update, context)


def deabo(update, context):
	chat_id = update.effective_chat.id
	with open("database", "r") as json_file:
		users = json.load(json_file)

	context.bot.send_message(chat_id=chat_id,
							text="Du hast alle Kategorien abgewählt und wirst keine Nachrichten mehr von diesem Bot "
								"bekommen. Um dich wieder anzumelden, nutze /start. (To-Do: Bist du sicher? einfügen)")

	try:
		users.pop(str(chat_id))
		with open("database", "w") as json_file:
			json.dump(users, json_file)
	except KeyError:
		pass


def poll_answer(update, context):
	chat_id = update.poll_answer.user.id
	selected_answers = update.poll_answer.option_ids

	with open("database", "r") as json_file:
		users = json.load(json_file)

	for i in range(len(categorie_keys)):
		if i in selected_answers:
			users[str(chat_id)][categorie_keys[i]] = True
		else:
			users[str(chat_id)][categorie_keys[i]] = False

	with open("database", "w") as json_file:
		json.dump(users, json_file)


def feedback(update, context):
	for admin_id in ADMIN_IDS:
		update.message.forward(chat_id=admin_id)


dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("abo", abo))
dispatcher.add_handler(CommandHandler("deabo", deabo))
dispatcher.add_handler(PollAnswerHandler(poll_answer))
dispatcher.add_handler(MessageHandler(Filters.text, feedback))

updater.start_polling()
