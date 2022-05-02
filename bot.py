from telegram.ext import Updater, CommandHandler, PollAnswerHandler, MessageHandler, Filters
import logging
import json
from configparser import ConfigParser
import os

config = ConfigParser()
config.read("config.ini")

API_KEY = config["General"]["api_key"]
ADMIN_IDS = [int(admin_id) for admin_id in config["General"]["admin_ids"].split(",")]

category_names = config["Categories"]["category_names"].split(",")
category_keys = config["Categories"]["category_keys"].split(",")

if not os.path.exists("database"):
	with open("database", 'w') as json_file:
		json_file.write("{}")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

updater = Updater(token=API_KEY)
dispatcher = updater.dispatcher


def start(update, context):
	chat_id = update.effective_chat.id
	with open("database", "r") as json_file:
		users = json.load(json_file)

	context.bot.send_message(
		chat_id=chat_id,
		text="♥️ Herzlich Willkommen, deine Anmeldung war erfolgreich.\n\n"
		"🌍 Wir senden regelmäßig einen Überblick mit kommenden Veranstaltungsterminen, Tagesordnungspunkten der "
		"Fachschaft und interessanten Treffen, die von großem Interesse für Studierende sein könnten. "
		"Außerdem melden wir uns zwischendurch bei wichtigen Meldungen (z.B. Anmeldefristen bei Flexnow).\n\n"
		"🛑 Um den Empfang zu stoppen, schreibe einfach /stop.\n\n"
		"📰 Mit dem Befehl /abo kannst du die verschiedenen Infokanäle abonnieren."
	)

	if str(chat_id) in list(users.keys()):
		context.bot.send_message(
			chat_id=chat_id,
			text="Du schon bei diesem Bot angemeldet. Wenn du deine Präferenzen bearbeiten willt, kannst du das mit "
			"/abo tun."
		)
	else:
		users[str(chat_id)] = {key: False for key in category_keys}
		with open("database", "w") as json_file:
			json.dump(users, json_file)

		abo(update, context)


def abo(update, context):
	chat_id = update.effective_chat.id
	with open("database", "r") as json_file:
		users = json.load(json_file)

	if str(chat_id) in list(users.keys()):
		context.bot.send_poll(
			chat_id=chat_id,
			question="Aus welchen Kategorien möchtest du Nachrichten bekommen?",
			options=category_names,
			is_anonymous=False,
			allows_multiple_answers=True
		)
		context.bot.send_message(
			chat_id=chat_id,
			text="Veranstaltungen\n"
			"Hier gibt es kurz und knapp Infos zu Veranstaltungen der Physikfakultat, "
			"der Fachschaft und der Universität.\n\n"
			"Studienticker\n"
			"Hier erinnern wir euch an wichtige Deadlines wie beispielsweise "
			"die Anmeldedeadline bei Flexnow für Übungen.\n\n"
			"FSR\n"
			"Hier laden wir euch regelmäßig zu unseren Sitzungen ein und posten auch die Tagesordnung.\n\n"
			"Interessante TOP's\n"
			"Tagesaktuelle Dinge, die interessant für dich sein könnten!\n\n"
			"Stellenausschreibungen\n"
			"Auf der Suche nach 'nem Hiwijob? Hier leiten wir Ausschreibungen für Stipendien, Preise, Akademien, "
			"Summer schools, Tutor*Innenjobs und Stellenausschreibungen weiter."
		)
	else:
		start(update, context)


def stop(update, context):
	chat_id = update.effective_chat.id
	with open("database", "r") as json_file:
		users = json.load(json_file)

	context.bot.send_message(
		chat_id=chat_id,
		text="Du hast alle Kategorien abgewählt und wirst keine Nachrichten mehr von diesem Bot bekommen. Um dich "
		"wieder anzumelden, nutze /start."
	)

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

	for i in range(len(category_keys)):
		if i in selected_answers:
			users[str(chat_id)][category_keys[i]] = True
		else:
			users[str(chat_id)][category_keys[i]] = False

	with open("database", "w") as json_file:
		json.dump(users, json_file)


def feedback(update, context):
	for admin_id in ADMIN_IDS:
		update.message.forward(chat_id=admin_id)


dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("abo", abo))
dispatcher.add_handler(CommandHandler("stop", stop))
dispatcher.add_handler(PollAnswerHandler(poll_answer))
dispatcher.add_handler(MessageHandler(Filters.text, feedback))

updater.start_polling()
