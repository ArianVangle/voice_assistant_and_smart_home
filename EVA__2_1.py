import json
import pyaudio
from vosk import Model, KaldiRecognizer
import torch
import sounddevice as sd
import time
from random import randint
from text_to_num import text2num as t2n
from num2t4ru import num2text as n2t
from fuzzywuzzy import fuzz
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
from transliterate import translit
from answer import * #файл с ответами
from config import * #файл со словарём команд и их тригерами

model = Model(r'C:\Users\1\Desktop\python\EVA\small_model')
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1,
				rate=16000, input=True, frames_per_buffer=8000)
language = 'ru'
model_id = 'v3_1_ru'
sample_rate = 48000
speaker = 'xenia'  # aidar, baya, kseniya, xenia, eugene, random
device = torch.device('cpu')
model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
						  model='silero_tts',
						  language=language,
						  speaker=model_id)
model.to('cpu') 

answer_text = ''

def listen():
	while True:
		data = stream.read(4000, exception_on_overflow=False)
		if rec.AcceptWaveform(data) and len(data) > 0:
			answer = json.loads(rec.Result())
			yield answer['text']

audio = model.apply_tts(text='абвгдеежзийклмнопрстуфхцчшщъыьэюя', speaker=speaker, sample_rate=sample_rate)


def timer():
	global command_keys, answer_text, text
	print('таймер запущен')
	timing = time.time()
	while True:
		listen()
		for text in listen():
			if text != '':
				choose_command(text)
				return
			else:
				if time.time() - timing > 6.0:
					print('ева перешла в режим ожидания')
					bye()
					return

def voice_out(answer_text):
	stream.stop_stream()
	audio = model.apply_tts(text=answer_text, speaker=speaker, sample_rate=sample_rate)
	print(audio)
	sd.play(audio, sample_rate)
	time.sleep((len(audio) / sample_rate) * 1.1)
	time.sleep(0.10)
	stream.start_stream()


def play_recorder_voice(command_keys):
	global answer_index, text
	stream.stop_stream()
	answer_index = randint(0, len(answers[command_keys]) - 1)
	try:
		print(f'РАСПОЗНАНО: {text} \nКОМАНДА: {command_keys} \nОТВЕТ: {answers[command_keys][answer_index]}')
	except: 
		print(answers[command_keys][answer_index])
	p = rf"C:\Users\1\Desktop\python\EVA\EVA_ANS\{command_keys}\{answer_index + 1}.wav"
	playsound.playsound(p)
	time.sleep(0.2)
	stream.start_stream()


#транслитерация английских слов
def transliteration(text):
	cyrillic = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	latin = 'а|б|с|д|е|ф|г|х|и|дж|к|л|м|н|о|п|к|р|с|т|у|в|в|кс|й|з|А|Б|Ц|Д|И|Ф|Г|АШ|И|ДЖЕЙ|К|Л|М|Н|О|П|К|Р|С|Т|Ю|В|В|КС|Й|З'.split('|')
	return text.translate({ord(k):v for k,v in zip(cyrillic,latin)})

#универсальный выбор команды
def choose_command(text, abs=True):
	global command_value, command_keys, answer_text
	command_value_list = []
	command_keys = ''
	if abs:
		command_keys = 'ABSENCE'
	command_list = []
	for keys in commands:
		for i in range(0, len(commands[keys])):
			if fuzz.token_set_ratio(commands[keys][i], text) > 80 or fuzz.partial_token_set_ratio(commands[keys][i], text) > 80:
				print(commands[keys][i], fuzz.partial_token_set_ratio(commands[keys][i], text))
				command_value_list.append(commands[keys][i])
				command_value = commands[keys][i]
				command_list.append(keys)
	command_list = list(set(command_list)) 
	print(command_list)
	if 'WIKIPEDIA' in command_list:
		command_keys = 'WIKIPEDIA'
		command_value = command_value_list[0]
	else:
		if len(command_list) > 1:
			command_keys = 'TOGETHER'
		else:
			for elem in command_list:
				command_keys = elem
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
	return command_keys


def open_browser():
	webbrowser.open('https://ya.ru')
	play_recorder_voice('OPEN_BROWSER')

def bye():
	global command_keys, answer_text, text
	if command_keys == 'BYE':
		play_recorder_voice('BYE')
	while True:
		for text in listen():
			if fuzz.token_set_ratio(text, 'ева') > 90:
				choose_command(text, abs=False)
				return

def music_recognize():
	global answer_text, text, out
	play_recorder_voice('MUSIC_RECOGNIZE')
	file_name = 'music.mp3'
	start_shazam = False
	try:
		recording = sd.rec((7 * 44100), samplerate=44100, channels=1)
		sd.wait()
		write(f'{file_name}', 44100, recording)
		start_shazam = not start_shazam
		while start_shazam:
			async def main():
				global out
				shazam = Shazam()
				out = await shazam.recognize_song(f"{file_name}")
				out = out['track']['title'] + ' ' + out['track']['subtitle']
				out = transliteration(out)
			loop = asyncio.get_event_loop()
			loop.run_until_complete(main())
			start_shazam = not start_shazam
		answer_text = f'это {out}'
		status_bar(text)
		voice_out(answer_text)
		os.remove(f'{file_name}')
	except:
		answer_text = 'у меня не получилось'
		status_bar(text)
		voice_out(answer_text)
		os.remove(f'{file_name}')

def wikipedia():
	global answer_text
	command_value_list = command_value.split() 
	text_list = text.split()
	index_start_command = 0
	for i in text_list:  
		if fuzz.token_set_ratio(i, command_value_list[0]) > 80:
			index_start_command = text_list.index(i)
	del text_list[0:index_start_command + 1]
	query_word = ' '.join(text_list)
	try:
		wiki.set_lang('ru')
		query = wiki.summary(query_word, sentences = 10)
		delete_brackets_text = re.sub("\[.*?\]", "", query)
		delete_brackets_text = re.sub("\(.*?\)", "", delete_brackets_text)
		sentences = delete_brackets_text.split('.')
		while len(sentences) > 1:
			sentences.pop(-1)
		sentences = '.'.join(sentences)
		answer_text += sentences
		status_bar(text)
		voice_out(transliteration(answer_text))
	except:
		answer_text = 'Попробуйте уточнить ваш запрос'
		status_bar(text)
		voice_out(answer_text)

def screen_brightness():
	print(123)
	global text
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
			voice_out(answer_text)
			return
		except:
			voice_out(f'минимум яркости - ноль, а максимум сто, не могу поставить {n2t(sum(brightness_list))}')

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

	status_bar(' '.join(text))
	voice_out(answer_text)



devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volume.GetMute()
volume.GetVolumeRange()
def change_volume():
	global text, answer_text
	current_volume = volume.GetMasterVolumeLevelScalar()
	status_bar(text)
#--------------------------------------
	volume_list = []
	text = text.split()
	for i in text:
		try:
			a = t2n(i, 'ru')
			volume_list.append(a)
		except:
			pass
	if len(volume_list) != 0:
		try:
			volume.SetMasterVolumeLevelScalar(sum(volume_list)/ 100, None)
			voice_out(answer_text)
			return
		except:
			voice_out(f'минимум громкости - ноль, а максимум сто, не могу поставить {n2t(sum(volume_list))}')

#------------------------------------------

	if fuzz.token_set_ratio(text, 'повысь') > 90 or fuzz.token_set_ratio(text, 'увеличь') > 90 or fuzz.token_set_ratio(text, 'повысить') > 90:
		volume.SetMasterVolumeLevelScalar(current_volume + 0.2, None)
		voice_out(answer_text)
	if fuzz.token_set_ratio(text, 'понизить') >  90 or fuzz.token_set_ratio(text, 'уменьши') >  90:
		volume.SetMasterVolumeLevelScalar(current_volume - 0.2, None)

		voice_out(answer_text)


def open_youtube():
	webbrowser.open('https://youtube.com')
	play_recorder_voice('OPEN_YOUTUBE')


def school_diary():
	webbrowser.open('https://sgo.rso23.ru')
	play_recorder_voice('SCHOOL_DIARY')

def absence():
	play_recorder_voice('ABSENCE')

def together():
	play_recorder_voice('TOGETHER')


def informal():
	global command_keys, answer_text, text
	answer_text += ', а у вас?'
	status_bar(text)
	voice_out(answer_text)
	listen()
	for text in listen():
		global query
		query = text
		if 	choose_command(text, False) == '':
			answer_text = 'Понятно. Чем вам помочь?'
			status_bar(text)
			voice_out(answer_text)
		break
	return

def weather():
	global text

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
			t = n2t(temp)
			f = n2t(feels)
		if temp == feels:
			t = n2t(temp)
		translator = Translator()
		osad = w.detailed_status
		o = translator.translate(text=osad, scr='en', dest='ru').text
		answer_text = f'Сейчас в городе {city} {n2t(temp, units)}, {o}. {fl} {f}'
		voice_out(answer_text)
	except:
		voice_out('не удалось подключиться к серверу')
	

def calculator():
	global text, answer_text, command_value, command_keys
	text_list = text.split()
	index_command_value = 0
	first_number_list = []
	second_number_list = []
	for i in text_list: 
		if fuzz.token_set_ratio(i, command_value) > 70: #!
			index_command_value = text_list.index(i)
	for i in range(len(text_list)):
		if text_list[i] == 'одну':
			text_list.insert(text_list.index(text_list[i]), 'одна')
			text_list.pop(text_list.index(text_list[i]) + 1)
		if text_list[i] == 'тысячу':
			text_list.insert(text_list.index(text_list[i]), 'тысяча')
			text_list.pop(text_list.index(text_list[i]) + 1)
	for i in range(index_command_value, -1, -1): 
		try:
			if type(t2n(text_list[i], 'ru')) == int:
				first_number_list.append(text_list[i])
		except:
			pass
	for i in range(index_command_value, len(text_list)):
		try:
			if type(t2n(text_list[i], 'ru')) == int:
				second_number_list.append(text_list[i])
		except:
			pass

	if len(first_number_list) == 0 and len(second_number_list) == 0:
		voice_out('не могу складывать слова, на+учите?')
		
	else:
		first_number = t2n(' '.join(first_number_list[::-1]), 'ru')
		second_number = t2n(' '.join(second_number_list), 'ru')
		if command_value == 'плюс':
			result = n2t(first_number + second_number)
			answer_text = result + answer_text
		if command_value == 'минус':
			result = n2t(first_number - second_number)
			answer_text = result + answer_text
		if command_value == 'умножить':
			result = n2t(first_number * second_number)
			answer_text = result + answer_text
		if command_value == 'разделить':
			try:
				result = first_number / second_number
				result_list = str(result).split()
				result_list_numbers = []
				for i in result_list:
					for z in i:
						result_list_numbers.append(z)
				for i in range(len(result_list_numbers)):
					if result_list_numbers[i] == '.':
						if int(result_list_numbers[i + 1]) == 0:
							answer_text = n2t(result) + answer_text
						else:
							answer_text = f'примерно {n2t(round(result))} {answer_text}'
			except ZeroDivisionError:
				answer_text = 'на ноль делить нельзя!'
		status_bar(text)
		voice_out(answer_text)

def help():
	status_bar(text)
	voice_out(answer_text)


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


def temp_hum_sensor():
	rec = com_receiving()
	if rec != 0:
		print(rec)
		units_temp = ((u'градус', u'градуса', u'градусов'), 'm')
		units_perc = ((u'процент', u'процента', u'процентов'), 'm')
		temp = n2t(int(rec.split()[1][:-2]), units_temp)
		hum = n2t(int(rec.split()[3][:-1]), units_perc)
		voice_out(f'сейчас температура в комнате {temp}, а влажность {hum} ')
	else:
		voice_out('не могу получить информацию с датчика')





def status_bar(text):
	print(f'РАСПОЗНАНО: {text} \nКОМАНДА: {command_keys} \nОТВЕТ: {answer_text}')

now = datetime.now()
current_time =  now.strftime("%H")
if int(current_time) >= 17:
	answer_text = answers['START'][1]
else:
	answer_text = answers['START'][-1]

print(answer_text)
voice_out(answer_text)

for text in listen():
	global query
	query = text
	if text:
		print('распознание в основном цикле')
		choose_command(text)
	else:
		timer()
