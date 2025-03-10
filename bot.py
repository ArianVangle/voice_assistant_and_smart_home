import json
import pyaudio
from vosk import Model, KaldiRecognizer
import torch
import sounddevice as sd
import time
from random import randint
from text_to_num import text2num as t2n
from num2t4ru import num2text as n2t
from fuzzywuzzy import fuzz, process
import webbrowser
import wikipedia as wiki
from scipy.io.wavfile import write
from shazamio import Shazam
import os
from comtypes import CLSCTX_ALL
import asyncio
import pyowm
import screen_brightness_control as sbc
from googletrans import Translator
import re
import time
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import playsound
import serial
import serial.tools.list_ports
from datetime import datetime
from smart_lamp import *
from transliterate import translit
from answer import * #файл с ответами
from config import * #файл со словарём команд и их тригерами
import g4f
import telebot
import pymorphy3
from g4f.client import Client
import g4f
bot = telebot.TeleBot('7981203170:AAHwFEY5xo7i8TWF-pF6_SZqwTDOp9sCUdc')
command_keys = ''
answer_text = ''
text = ''
morph = pymorphy3.MorphAnalyzer()



client = Client()
def gpt4o_ans(text: str):

    response = client.chat.completions.create(
        model=g4f.models.gpt_4o,
        messages=[{"role": "user", "content": text}],
        max_tokens=20,
        web_search=True,
    )
    return response.choices[0].message.content


def choose_command(textin, abs=True):
	global command_value, command_keys, answer_text, text
	command_value_list = []
	command_keys = ''
	text = textin
	if abs:
		command_keys = 'ABSENCE'
	command_list = []
	for keys in commands:
		for i in range(0, len(commands[keys])):
			if fuzz.token_set_ratio(commands[keys][i], textin) > 80 or fuzz.partial_token_set_ratio(commands[keys][i], textin) > 80:
				print(commands[keys][i], fuzz.token_set_ratio(commands[keys][i], textin),fuzz.partial_token_set_ratio(commands[keys][i], textin))
				command_value_list.append(commands[keys][i])
				command_value = commands[keys][i]
				command_list.append(keys)
	command_list = list(set(command_list)) #удаление повторов из command_list
	print(command_list)
	if 'WIKIPEDIA' in command_list:
		command_keys = 'WIKIPEDIA'
		command_value = command_value_list[0]
	else: 
		if len(command_list) > 1:
			command_keys = 'TOGETHER'
		elif len(command_list)==1:
			command_keys = command_list[0]
		else:
			if fuzz.token_set_ratio('ева', textin) != 100:
				try:
					command_list += ['GPT-4o']
					command_keys = 'GPT-4o'
					answer_text = gpt4o_ans(textin)
				except: pass
	try:
		answer_text = answers[f'{command_keys}'][randint(0, len(answers[f'{command_keys}']) - 1)]
		eval(f'{command_keys}'.lower())()

	except Exception as e:
		print(e)
		try:
			eval(f'{command_keys}'.lower())()
		except Exception as e:
			print(e)
	finally:
		pass
	return [command_keys, answer_text]

def open_browser():
	global answer_text
	webbrowser.open('https://ya.ru')
	answer_text = 'открыла'

def weather():
	global text, answer_text

	try:
		owm = pyowm.OWM('e215e480e8e3b35ca5fba1afd5c83f9b')
		city = 'Туапсе'
		mgr = owm.weather_manager()
		obs = mgr.weather_at_place(city)
		w = obs.weather
		t = w.temperature('celsius')
		temp = round(t['temp'])
		feels = round(t['feels_like'])
		units = ((u'градус', u'градуса', u'градусов'), 'm')
		print (n2t(temp, units))
		fl = ''
		f = ''
		if temp != feels:
			fl = 'ощущается как'
			t = temp
			f = str(feels) + '°C'
		if temp == feels:
			t = temp
		translator = Translator()
		osad = w.detailed_status
		o = translator.translate(text=osad, scr='en', dest='ru').text
		answer_text = f'Сейчас в городе {city} {temp}°C, {o}. {fl} {f}'
	except:
		answer_text = 'не могу получить информацию о погоде, возможно что-то случилось с API'

def wikipedia():
	global answer_text, text
	# answer_text = ''
	# command_value_list = command_value.split() #преобразование сказанной фразы и значения ключа команды в список
	# text_list = text.split()
	# index_start_command = 0
	# for i in text_list:     #удаление слов до запроса пользователя
	# 	if fuzz.token_set_ratio(i, command_value_list[0]) > 80:
	# 		index_start_command = text_list.index(i)
	# del text_list[0:index_start_command + 1]
	# query_word = ' '.join(text_list)
	# # print(query_word)
	# try:
	# 	wiki.set_lang('ru')
	# 	query = wiki.summary(query_word, sentences = 10)
	# 	delete_brackets_text = re.sub("\[.*?\]", "", query)
	# 	delete_brackets_text = re.sub("\(.*?\)", "", delete_brackets_text)
	# 	sentences = delete_brackets_text.split('.')
	# 	while len(sentences) > 1: #укорачивание найденного текста-ответа до одного предложения
	# 		sentences.pop(-1)
	# 	sentences = '.'.join(sentences)
	# 	answer_text += sentences
	# except Exception as e:
	# 	answer_text = e
	answer_text = gpt4o_ans(text)

def screen_brightness():
	print(123)
	global text, answer_text
	brightness = sbc.get_brightness()
	print(text)
	#--------------------------------------
	brightness_list = []
	text = text.split()
	for i in text:
		try:
			a = t2n(i, 'ru')
			brightness_list.append(a)
		except:
			pass
	if len(brightness_list) != 0:
		try:
			sbc.set_brightness(sum(brightness_list))
			return
		except:
			answer_text = (f'минимум яркости - ноль, а максимум сто, не могу поставить {n2t(sum(brightness_list))}')

#------------------------------------------
	if fuzz.token_set_ratio(text, 'повысь') > 90 or fuzz.token_set_ratio(text, 'увеличь') > 90:
		print('я в повысь')
		sbc.set_brightness(brightness[0] + 20)
	elif fuzz.token_set_ratio(text, 'понизь') >  90 or fuzz.token_set_ratio(text, 'уменьши') >  70:
		sbc.set_brightness(brightness[0] - 20)
		print('я в понизь')
	elif fuzz.token_set_ratio(text, 'максимум') >  90:
		sbc.set_brightness(100)
		print('я в максимум')

try:
	ports = serial.tools.list_ports.comports()
	com_port = ''
	for port in ports:
		str_port = str(port)
		if 'USB-SERIAL CH340' in str_port:
			com_port = str(port[0])
	serial_port = serial.Serial(com_port, baudrate=9600, timeout=2)
	print(com_port)
except:
	pass

def com_receiving():
	print('вызов ком ресевинг')
	try:
		serial_port.flushInput()
		data = serial_port.readline().decode().strip()
		now = datetime.now()
		current_time =  now.strftime("%d/%m/%Y %H:%M:%S")
		with open('sensor.txt', 'a', encoding='utf8') as file:
			file.write(current_time + ' ' + 'температура ' + data.split()[1][:-2] + "  " + 'влажность ' + data.split()[3][:-1] + '\n')
		return data
	except:
		return 0 

def light_control():
	global text, answer_text
	words = text.split()
	verbs = []
	for w in words:
		m = morph.parse(w)[0]
		if m.tag.POS == 'VERB': verbs.append(m.tag.mood)
	print(verbs)
	if 'impr' in verbs or 'включить' in text or 'выключить' in text:
		b = process.extractOne(text, [['включить', 1], ['выключить', 0],['зеленый', 2],['желтый', 6], ['синий', 5], ['красный', 3], ['обычный', 4]])
		print(b)
		asyncio.run(turn(b[0][1]))
		answer_text = 'оформила'
	else:
		answer_text = gpt4o_ans(text)

def temp_hum_sensor():
	global answer_text, text
	rec = com_receiving()
	if rec != 0:
		print(rec)
		answer_text = (f'сейчас температура в комнате {rec.split()[1]}, а влажность {rec.split()[3]}')
	else:
		answer_text = ('не могу получить информацию с датчика')

def gas_sensor():
	global answer_text, text
	rec = com_receiving()
	# print(rec.split())
	if rec != 0:
		print(rec)
		gas = rec.split()[5]
		if int(rec.split()[5]) > 600:
			answer_text = f'сейчас в воздухе порядка {gas} PPM, стоит проветрить'
		else: answer_text = f'сейчас в воздухе порядка {gas} PPM, показатели в норме'
	else:
		answer_text = 'не могу получить информацию с датчика'

@bot.message_handler()
def info(message):
	now = datetime.now()
	current_time =  now.strftime("%d/%m/%Y %H:%M:%S")
	with open('bot.txt', 'a', encoding='utf8') as file:
		file.write(current_time + ' ' + str(message.from_user.username)+ ' ' +  message.text +  '\n')
	# bot.send_message(message.chat.id, message.text + f'\n {choose_command(message.text)}')
	bot.send_message(message.chat.id, f'\n {choose_command(message.text)[1]}')

	

bot.polling(none_stop=True)