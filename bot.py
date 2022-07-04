from telegram.ext import Updater, CommandHandler, PollAnswerHandler, MessageHandler, Filters
import logging
import json
from configparser import ConfigParser
import os
from itertools import count

config = ConfigParser()
config.read("config.ini")

API_KEY = config["General"]["api_key"]
ADMIN_IDS = [int(admin_id) for admin_id in config["General"]["admin_ids"].split(",")]

category_names = config["Categories"]["category_names"].split(",")
category_keys = config["Categories"]["category_keys"].split(",")
category_descriptions = []

# Load the categorie descriptions from the config file
for i in count(1):
	try:
		category_descriptions.append(config["Categories"][f"description{i}"])
	except KeyError:
		break

# Create an empty database if it doesn't exist
if not os.path.exists("database"):
	with open("database", 'w') as json_file:
		json_file.write("{}")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

updater = Updater(token=API_KEY)
dispatcher = updater.dispatcher


# Load users and their category subscriptions from the database
def load_database():
	with open("database", "r") as json_file:
		return json.load(json_file)


# Save users and their category subscriptions to the database
def write_database(users):
	with open("database", "w") as json_file:
		json.dump(users, json_file)


# Send a welcome message to the user and redirect to managing categories
def start(update, context):
	chat_id = update.effective_chat.id
	users = load_database()

	# Welcome message
	context.bot.send_message(
		chat_id=chat_id,
		text="♥️ Herzlich Willkommen, deine Anmeldung war erfolgreich.\n\n"
		"🌍 Wir senden regelmäßig einen Überblick mit kommenden Veranstaltungsterminen, Tagesordnungspunkten der "
		"Fachschaft und interessanten Treffen, die von großem Interesse für Studierende sein könnten. "
		"Außerdem melden wir uns zwischendurch bei wichtigen Meldungen (z.B. Anmeldefristen bei Flexnow).\n\n"
		"🛑 Um den Empfang zu stoppen, schreibe einfach /stop.\n\n"
		"📰 Mit dem Befehl /abo kannst du die verschiedenen Infokanäle abonnieren."
	)

	# Redirect to managing categories if the user is not in the database
	if str(chat_id) in list(users.keys()):
		context.bot.send_message(
			chat_id=chat_id,
			text="Du schon bei diesem Bot angemeldet. Wenn du deine Präferenzen bearbeiten willt, kannst du das mit "
			"/abo tun."
		)
	else:
		# Add the user to the database with no category subscriptions
		users[str(chat_id)] = {key: False for key in category_keys}
		write_database(users)

		abo(update, context)


# Manage the user's category subscriptions
def abo(update, context):
	chat_id = update.effective_chat.id
	users = load_database()

	# Send a poll to choose the category subscriptions if the user is in the database
	if str(chat_id) in list(users.keys()):
		context.bot.send_poll(
			chat_id=chat_id,
			question="Aus welchen Kategorien möchtest du Nachrichten bekommen?",
			options=category_names,
			is_anonymous=False,
			allows_multiple_answers=True
		)

		# Send an overview of the categories with their descriptions
		message = ""
		for i in range(len(category_descriptions)):
			message += f"#{category_names[i]}\n"
			message += category_descriptions[i] + "\n\n"

		context.bot.send_message(
			chat_id=chat_id,
			text=message
		)
	else:
		# Send a welcome message if the user is not in the database
		start(update, context)


# Remove the user from the database
def stop(update, context):
	chat_id = update.effective_chat.id
	users = load_database()

	# Goodbye message
	context.bot.send_message(
		chat_id=chat_id,
		text="Du hast alle Kategorien abgewählt und wirst keine Nachrichten mehr von diesem Bot bekommen. Um dich "
		"wieder anzumelden, nutze /start."
	)

	# Remove the user from the database if they are in the database
	try:
		users.pop(str(chat_id))
		write_database(users)
	except KeyError:
		# If the user is not in the database, do nothing
		pass


# Manage the user's category subscriptions from their answer to the poll
def poll_answer(update, context):
	chat_id = update.poll_answer.user.id
	selected_answers = update.poll_answer.option_ids
	users = load_database()

	# Update the user's category subscriptions
	for i in range(len(category_keys)):
		if i in selected_answers:
			users[str(chat_id)][category_keys[i]] = True
		else:
			users[str(chat_id)][category_keys[i]] = False

	write_database(users)


# Redirect other messages to the admins
def feedback(update, context):
	for admin_id in ADMIN_IDS:
		update.message.forward(chat_id=admin_id)


# Link the functions to the commands and events
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("abo", abo))
dispatcher.add_handler(CommandHandler("stop", stop))
dispatcher.add_handler(PollAnswerHandler(poll_answer))
dispatcher.add_handler(MessageHandler(Filters.text, feedback))

# Start the bot
updater.start_polling()
