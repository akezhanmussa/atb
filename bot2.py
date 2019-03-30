import sys
import telegram
import logging
import random
import telegram.bot
import datetime
import os
from telegram import KeyboardButton
from telegram.ext import CommandHandler
from telegram.ext import Updater, RegexHandler, ConversationHandler
from telegram.ext import MessageHandler, Filters
import numpy as np
from flask import Flask
#Сколько лет?

#Сознание какое?

#Дыхание какое?

# Способность ходить
#

# Лежит?
# {}

# Посинения
# {"Есть":0.112, "Нет":0}

# Потеет?
# {"Да":0, "Нет":0, "Не знаю":0.724}

app = Flask(__name__)

token_ayala = "725000187:AAG74_5qbFRXhOSpDynS9KX429_r09XneoU"
bot_ayala = telegram.Bot(token=token_ayala)

#The specific weights for the model
ages = {"0-1":0, "1-14":0, "15-39":0, "40-69":2.231, "70+":2.564, "Не знаю":2.564}
mood = {"Ясное":0, "Неясное":0.19, "Без сознания":1.749, "Не знаю":1.749}
breath = {"Нормальное":0, "Одышка":0.989, "Задыхается":4.861, "Не знаю":1.116}
walk_ability = {"Нормальное":0, "С поддержкой":0.999, "Не может":1.727, "Не знаю":1.805}
on_bed = {"Да":0.536, "Нет":0}
is_blue = {"Есть":0.112, "Нет":0}
is_sweat = {"Да":0, "Нет":0, "Не знаю":0.724}
counter = 0
speechafter = """
Если цифра выше 3.6% - рекомендуется вызвать скорую помощь.
Если цифра меньше 3.6% - вы сможете решить ситуацию сами. Инструкции даны по ссылке ниже.

В инструкции указаны следующее: гипертония, простуда, отравление/боли в животе, голвная/суставная боль.

В случае отсутствия нужной информации в нашей инструкции - позвонить врачу. Номера даны ниже.

Нет нужных лекарств? Закажи их здесь с доставкой на дом: @europharmabot

**Номера врачей для консультации:**
Астана: 1430
Алматы: 8 (7273) 00 01 03

Если тебе нравится такой способ вызова скорой помощи- поделись с нами в __Instagram__, отметив нас @ayala_space. Так мы видим, что это нужно 

https://teletype.in/@ayalaspace/SkMebjRlN
"""

u = Updater(token_ayala)
dispatcher = u.dispatcher
results = []
wasQuestion = False


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def validate(date_text):
	try:
		datetime.datetime.strptime(date_text, '%d/%m/%Y')
		return True
	except ValueError:
		return False

def sigmoid(x):
  return np.exp(x)/(1+np.exp(x))

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
	menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
	if header_buttons:
		menu.insert(0, header_buttons)
	if footer_buttons:
		menu.append(footer_buttons)
	return menu


def start(bot, update):
	con_keyboard = KeyboardButton(text='Начать', request_contact=False)
	custom_keyboard = [[con_keyboard]]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="Дай доступ к своему номеру для регистрации, нажав на <Отправить номер>", reply_markup=reply_markup)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

#CONVERSATIONS

START, PHONE, BIRTH, CONV, HELP, ANSWER, MENU = range(7)
q1, q2, q3, q4, q5, q6, q7, q8, q9, menu, CONV2 = range(11)
# HELP, ANSWER, MENU = range(3)

def conversationStarter(bot, update):
	print("HERE")
	custom_keyboard = [['Узнать критичность'], ['Как пользоваться?']]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	# [['Узнать критичность', '⚙️Настройка'], ['Как пользоваться?']]
	text = ['⚙️Настройка', 'Узнать критичность', 'Как пользоваться?']
	if update.message.text == text[0]:
		bot.send_message(chat_id=update.message.chat_id, text="Ваши данные сохранены в базу, пройдите тест", reply_markup=reply_markup)
		return CONV
	elif update.message.text == text[1]:
		return START
	elif update.message.text == text[2]:
		bot.send_message(chat_id=update.message.chat_id, text="Чтобы узнать уровень критичности ситуации, нажмите на Узнать критичность два раза", reply_markup=reply_markup)
		return CONV
	else:
		return ConversationHandler.END

def conversationStarter2(bot, update):
	print("HERE")
	custom_keyboard = [['Узнать критичность', '⚙️Настройка'], ['Как пользоваться?']]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	# [['Узнать критичность', '⚙️Настройка'], ['Как пользоваться?']]
	text = ['⚙️Настройка', 'Узнать критичность', 'Как пользоваться?']
	if update.message.text == text[0]:
		bot.send_message(chat_id=update.message.chat_id, text="Ваши данные сохранены в базу, пройдите тест", reply_markup=reply_markup)
		return CONV2
	elif update.message.text == text[1]:
		return q2
	elif update.message.text == text[2]:
		bot.send_message(chat_id=update.message.chat_id, text="Чтобы узнать уровень критичности ситуации, нажмите на Узнать критичность два раза", reply_markup=reply_markup)
		return CONV2
	else:
		return ConversationHandler.END

#CONVERSATION FOR SETTINGS

def number(bot, update):
	text = 'Начать'
	text2 = '⚙️Настройка'
	text3 = 'Узнать критичность'
	print('Was clicked')
	if update.message.text == text or update.message.text == text2 or update.message.text == text3:
		con_keyboard = KeyboardButton(text='Отправить номер', request_contact=True)
		custom_keyboard = [[con_keyboard]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
		bot.send_message(chat_id=update.message.chat_id, text="Отправьте свой номер", reply_markup=reply_markup)
		return PHONE
	else:
		return q2

# def location(bot, update):
# 	loc_keyboard = KeyboardButton(text='Отправить локацию', request_location=True)
# 	custom_keyboard = [[loc_keyboard]]
# 	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
# 	bot.send_message(chat_id=update.message.chat_id, text="Отправьте свое местоположение", reply_markup=reply_markup)
# 	return BIRTH

def birth(bot, update):
	reply_markup = telegram.ReplyKeyboardRemove()
	bot.send_message(chat_id=update.message.chat_id, text="Отправьте свою дату рождения (dd/MM/yyyy)", reply_markup=reply_markup)
	# update.message.location.latitude
	# update.message.location.longitude
	return BIRTH

def cancel(bot, update):
    update.message.reply_text('Отмена', reply_markup=telegram.ReplyKeyboardRemove())
    return ConversationHandler.END

def manageBirth(bot, update):
	print("dfdfd")
	if validate(update.message.text):
		print("fdfd")
		custom_keyboard = [['Узнать критичность', '⚙️Настройка'], ['Как пользоваться?']]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
		bot.send_message(chat_id=update.message.chat_id, text="МЕНЮ", reply_markup=reply_markup)
		return CONV
	else:
		birth(bot, update)

#CONVERSATION FOR CALL
# ages = {"0-1":0, "1-14":0, "15-39":0, "40-69":2.231, "70+":2.564, "Не знаю":2.564}
# mood = {"Ясное":0, "Неясное":0.19, "Без сознания":1.749, "Не знаю":1.749}
# breath = {"Нормальное":0, "Одышка":0.989, "Задыхается":4.861, "Не знаю":1.116}
# walk_ability = {"Нормальное":0, "С поддержкой":0.999, "Не может":1.727, "Не знаю":1.805}
# on_bed = {"Да":0.536, "Нет":0}
# is_blue = {"Есть":0.112, "Нет":0}
# is_sweat = {"Да":0, "Нет":0, "Не знаю":0.724}
# counter = 0
# speechafter = """
q1a = ["Родственник"]
q2a = ["0-1", "1-14", "15-39", "40-69", "70+", "не знаю"]
q3a = ["Ясное", "Неясное", "Без сознания", "Не знаю"]
q4a = ["Нормальное", "Одышка", "Задыхается", "Не знаю"]
q5a = ["Нормальное", "С поддержкой", "Не может", "Не знаю"]
q6a = ["Да", "Нет"]
q7a = ["Есть", "Нет"]
q8a = ["Да", "Нет", "Не знаю"]
q9a = ["Да", "Нет"]

# TODO: finish if statements to validate answers
# def question1(bot, update):
# 	text = 'Вызывать скорую'
# 	if update.message.text == text:
# 		custom_keyboard = [["Родственник"]]
# 		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
# 		bot.send_message(chat_id=update.message.chat_id, text="Кому вызываем?", reply_markup=reply_markup)
# 		return q2
# 	else:
# 		return ConversationHandler.END


def question2(bot, update):
	custom_keyboard = [["0-1", "1-14"], ["15-39", "40-69"], ["70+", "не знаю"]]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="Возраст пациента?", reply_markup=reply_markup)
	return q3


def question3(bot, update):
	global results
	results.append(update.message.text)
	custom_keyboard = [["Ясное", "Неясное"], ["Без сознания", "Не знаю"]]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="Сознание?", reply_markup=reply_markup)
	return q4


def question4(bot, update):
	global results
	results.append(update.message.text)
	custom_keyboard = [["Нормальное", "Одышка"], ["Задыхается", "Не знаю"]]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="Дыхание?", reply_markup=reply_markup)
	return q5


def question5(bot, update):
	global results
	results.append(update.message.text)
	custom_keyboard = [["Нормальное", "С поддержкой"], ["Не может", "Не знаю"]]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="Способность ходить?", reply_markup=reply_markup)
	return q6


def question6(bot, update):
	global results
	results.append(update.message.text)
	custom_keyboard = [["Да", "Нет"]]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="Лежит?", reply_markup=reply_markup)
	return q7


def question7(bot, update):
	global results
	results.append(update.message.text)
	custom_keyboard = [["Есть", "Нет"]]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="Посинения?", reply_markup=reply_markup)
	return q8


def question8(bot, update):
	global results, counter
	global wasQuestion
	results.append(update.message.text)
	print(update.message.text)
	custom_keyboard = [["Да", "Нет"], ["Не знаю"]]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="Потеет?", reply_markup=reply_markup)
	wasQuestion = True
	counter += 1
	return menu


# def question9(bot, update):
# 	global results
# 	global wasQuestion
# 	results.append(update.message.text)
# 	custom_keyboard = [["Да", "Нет"]]
# 	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
# 	bot.send_message(chat_id=update.message.chat_id, text="Паника?", reply_markup=reply_markup)
# 	return menu

def risk_estimation():
	y = -8.78
	global ages, mood, breath, walk_ability, on_bed, is_blue, is_sweat, results
	if ages[results[0]]:
		y += ages[results[0]]
		print(1)
	if mood[results[1]]:
		y += mood[results[1]]
		print(1)
	if breath[results[2]]:
		y += breath[results[2]]
		print(1)
	if walk_ability[results[3]]:
		y += walk_ability[results[3]]
		print(1)
	if on_bed[results[4]]:
		y += on_bed[results[4]]
		print(1)
	if is_blue[results[5]]:
		y += is_blue[results[5]]
		print(1)
	if is_sweat[results[6]]:
		y += is_sweat[results[6]]
	y = sigmoid(y)
	return y

def manageAnswers(bot, update):
	global results
	global wasQuestion
	if wasQuestion:
		results.append(update.message.text)
		wasQuestion = False
	result = risk_estimation() * 100
	print("The number of clicks {}".format(counter))
	custom_keyboard = [['Узнать критичность', '⚙️Настройка'], ['Как пользоваться?']]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="""Критичность вызова {} \n {}""".format(result, speechafter), reply_markup=reply_markup)
	return CONV2

#CONVERSATION FOR SETTINGS

def helpp(bot, update):
	text = 'Как пользоваться?'
	if update.message.text == text:
		custom_keyboard = [["Вызов скорой", "Настройка профиля"]]
		reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
		bot.send_message(chat_id=update.message.chat_id, text="Как пользоваться?", reply_markup=reply_markup)
		return ANSWER
	else:
		return ConversationHandler.END

def helpAnswer(bot, update):
	text = 'Вызов скорой'
	if update.message.text == text:
		bot.send_message(chat_id=update.message.chat_id, text="Вызов скорой инструкция")
		return MENU
	elif update.message.text == "Настройка профиля":
		bot.send_message(chat_id=update.message.chat_id, text="Настройка профиля инструкция")
		return MENU
	else:
		return HELP

def menuu(bot, update):
	print("HERE")
	results.append(update.message.text)
	custom_keyboard = [['Узнать критичность', '⚙️Настройка'], ['Как пользоваться?']]
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.message.chat_id, text="МЕНЮ", reply_markup=reply_markup)
	return ConversationHandler.END


def unknown(bot, update):
	bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)


def main():
	settingsConversation = ConversationHandler(
		entry_points = [MessageHandler(Filters.text, number)],
		states = {
			START: [MessageHandler(Filters.contact, number)],
			PHONE: [MessageHandler(Filters.contact, birth)],
			BIRTH: [MessageHandler(Filters.text, manageBirth)],
			CONV: [MessageHandler(Filters.text, conversationStarter)],
			HELP: [MessageHandler(Filters.text, helpp)],
			ANSWER: [MessageHandler(Filters.text, helpAnswer)],
			MENU: [MessageHandler(Filters.text, menuu)]
		},
		fallbacks = [CommandHandler('cancel', cancel)]
	)
	dispatcher.add_handler(settingsConversation)

	callConversation = ConversationHandler(
		entry_points = [MessageHandler(Filters.text, question2)],
		states = {
			# q1: [MessageHandler(Filters.text, question1)],
			q2: [MessageHandler(Filters.text, question2)],
			q3: [MessageHandler(Filters.text, question3)],
			q4: [MessageHandler(Filters.text, question4)],
			q5: [MessageHandler(Filters.text, question5)],
			q6: [MessageHandler(Filters.text, question6)],
			q7: [MessageHandler(Filters.text, question7)],
			q8: [MessageHandler(Filters.text, question8)],
			# q9: [MessageHandler(Filters.text, question9)],
			menu: [MessageHandler(Filters.text, manageAnswers)],
			CONV2: [MessageHandler(Filters.text, conversationStarter2)],
		},
		fallbacks = [CommandHandler('cancel', cancel)]
	)
	dispatcher.add_handler(callConversation)


	helpConversation = ConversationHandler(
		entry_points = [MessageHandler(Filters.text, helpp)],
		states = {
			HELP: [MessageHandler(Filters.text, helpp)],
			ANSWER: [MessageHandler(Filters.text, helpAnswer)],
			MENU: [MessageHandler(Filters.text, menuu)],
		},
		fallbacks = [CommandHandler('cancel', cancel)]
	)
	dispatcher.add_handler(helpConversation)


	u.start_polling()

@app.route('/')
def root():
	return 'hii'

if __name__ == '__main__':
	main()
	port = int(os.environ.get('PORT', 5020))
	app.run(host='0.0.0.0', port = port, debug=True, use_reloader=False)
