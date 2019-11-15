from flask import Flask, request
import vk
import random
import settings
import os
import json
import math

app = Flask(__name__)
session = vk.Session()
api = vk.API(session, access_token = settings.access_token, v = 5.8)

themes = ['parity', 'assessment', 'graphs', 'pst']
opp_theme = [['четность'], ['оценка'], ['графы'], ['параллельность и сумма углов','параллельность и сумма углов треугольника']]

command_list = [['привет', 'ку', 'хай', 'здравствуйте'], ['помощь'], ['хочу задачу'], ['номер'], ['сложность'], ['ответ'], ['следующая'], ['предыдущая'], ['хочу новую задачу'], ['топ'], ['закончить'], ['люблю гордея']]
list_of_swearing = ['бля', 'блять', 'блядина', 'блядство',
					'ебать', 'ебля', 'ебу', 'заебал', 'ебал', 'ебучка', 'долбоеб',
					'пизда', 'пиздец','хуй', 'хуйня', 'нахуй', 'хуево', 'хуета',
					'сука', 'сучка', 'соси']

help_list = """Команды:\n
			   Хочу задачу - начать решать.
			   Топ - топ игроков.
			   Ответ [текст] - дать ответ на выданную ботом задачу.
			   \n\nЕсли у Вас старая версия вк то:
			   \n[тема] номер [№] - получить задачу с указанным номером из указанной темы.
			   [тема] сложность [№] - получить задачу с указанной сложностью из указанной темы.
			   Ответ [текст] - дать ответ на выданную ботом задачу.
			   Следующая задача - получить следующую задачу в данной теме.
			   Предыдущая задача - получить предыдущую задачу в данной теме.
			   Хочу новую задачу - получить новую задачу, когда решаешь другую.
			   Закончить - перестать решать текущую задачу."""

info = {'task' : {'parity' : [0, 1, 2, 3, 4],
				  'assessment' : [0, 1, 2, 3, 4, 5, 6, 7, 8],
				  'graphs' : [0, 1, 2, 3, 4, 5],
				  'pst' : [0, 1, 2, 3, 4, 5, 6, 7, 8]},
		'answer' : False,
		'points' : 0,
		'active_task' : ['', None]}

about_answer = "\n\nТеперь ты можешь писать боту свой ответ. Вот так 'ответ [свой ответ]'."
wrong_task = "Вы еще не сдали прошлую задачу, но Вы можете взять новую, написав 'предыдущая задача' / 'следующая задача' / 'хочу новую задачу' или закончить решать : 'закончить'."

main_keyboard = {"one_time" : True, 
				 "buttons" : [[{"action" : {
									"type" : "text",
									"payload" : "{\"button\":\"task\"}",
									"label" : "хочу задачу"},
								"color" : "positive"}]]}
main_keyboard = json.dumps(main_keyboard, ensure_ascii = False).encode('utf-8')
main_keyboard = str(main_keyboard.decode('utf-8'))

answer_keyboard = {"one_time" : True, 
				   "buttons" : [[{"action" : {
									"type" : "text",
									"payload" : "{\"button\":\"previous\"}",
									"label" : "<--предыдущая задача"},
								"color" : "primary"}],
								[{"action" : {
									"type" : "text",
									"payload" : "{\"button\":\"next\"}",
									"label" : "следующая задача-->"},
								"color" : "primary"}],
								[{"action" : {
									"type" : "text",
									"payload" : "{\"button\":\"task\"}",
									"label" : "хочу другую задачу"},
								"color" : "positive"}],
								[{"action" : {
									"type" : "text",
									"payload" : "{\"button\":\"end\"}",
									"label" : "закончить"},
								"color" : "negative"}]]}
answer_keyboard = json.dumps(answer_keyboard, ensure_ascii = False).encode('utf-8')
answer_keyboard = str(answer_keyboard.decode('utf-8'))

without_previous_keyboard = {"one_time" : True, 
							 "buttons" : [[{"action" : {
												"type" : "text",
												"payload" : "{\"button\":\"next\"}",
												"label" : "следующая задача-->"},
											"color" : "primary"}],
											[{"action" : {
												"type" : "text",
												"payload" : "{\"button\":\"task\"}",
												"label" : "хочу другую задачу"},
											"color" : "positive"}],
											[{"action" : {
												"type" : "text",
												"payload" : "{\"button\":\"end\"}",
												"label" : "закончить"},
											"color" : "negative"}]]}
without_previous_keyboard = json.dumps(without_previous_keyboard, ensure_ascii = False).encode('utf-8')
without_previous_keyboard = str(without_previous_keyboard.decode('utf-8'))

without_next_keyboard = {"one_time" : True, 
						 "buttons" : [[{"action" : {
											"type" : "text",
											"payload" : "{\"button\":\"previous\"}",
											"label" : "<--предыдущая задача"},
										"color" : "primary"}],
										[{"action" : {
											"type" : "text",
											"payload" : "{\"button\":\"task\"}",
											"label" : "хочу другую задачу"},
										"color" : "positive"}],
										[{"action" : {
											"type" : "text",
											"payload" : "{\"button\":\"end\"}",
											"label" : "закончить"},
										"color" : "negative"}]]}
without_next_keyboard = json.dumps(without_next_keyboard, ensure_ascii = False).encode('utf-8')
without_next_keyboard = str(without_next_keyboard.decode('utf-8'))

without_keyboard = {"one_time" : True, 
					"buttons" : [[{"action" : {
										"type" : "text",
										"payload" : "{\"button\":\"task\"}",
										"label" : "хочу другую задачу"},
									"color" : "positive"}],
									[{"action" : {
										"type" : "text",
										"payload" : "{\"button\":\"end\"}",
										"label" : "закончить"},
									"color" : "negative"}]]}
without_keyboard = json.dumps(without_keyboard, ensure_ascii = False).encode('utf-8')
without_keyboard = str(without_keyboard.decode('utf-8'))

hello_keyboard = {"one_time" : True, 
					"buttons" : [[{"action" : {
										"type" : "text",
										"payload" : "{\"button\":\"task\"}",
										"label" : "хочу задачу"},
									"color" : "positive"}],
									[{"action" : {
										"type" : "text",
										"payload" : "{\"button\":\"help\"}",
										"label" : "помощь"},
									"color" : "primary"}]]}
hello_keyboard = json.dumps(hello_keyboard, ensure_ascii = False).encode('utf-8')
hello_keyboard = str(hello_keyboard.decode('utf-8'))

help_keyboard = {"one_time" : True, 
					"buttons" : [[{"action" : {
										"type" : "text",
										"payload" : "{\"button\":\"task\"}",
										"label" : "хочу задачу"},
									"color" : "positive"}],
									[{"action" : {
										"type" : "text",
										"payload" : "{\"button\":\"top\"}",
										"label" : "топ"},
									"color" : "primary"}]]}
help_keyboard = json.dumps(help_keyboard, ensure_ascii = False).encode('utf-8')
help_keyboard = str(help_keyboard.decode('utf-8'))


@app.route('/', methods = ['POST'])
def processing():
	my_dir = os.path.dirname(__file__)
	json_file_path = os.path.join(my_dir, 'id.json')
	with open(json_file_path, 'r') as rf:
		for_test = json.load(rf)
	data = json.loads(request.data)
	if 'type' not in data.keys():
		return 'not vk'
	if(data['type'] == 'confirmation'):
		return settings.confirmation_token
	elif(data['type'] == 'message_new' and data['object']['id'] > for_test['id']):
		for_test['id'] = data['object']['id']
		with open(json_file_path, 'w') as wf:
			json.dump(for_test, wf)
		create_answer(data['object'])
		return 'ok'

def damerau_levenshtein_distance(s1, s2):
	d = {}
	lenstr1 = len(s1)
	lenstr2 = len(s2)
	for i in range(-1, lenstr1 + 1):
		d[(i, -1)] = i + 1
	for j in range(-1, lenstr2 + 1):
		d[(-1, j)] = j + 1
	for i in range(lenstr1):
		for j in range(lenstr2):
			if(s1[i] == s2[j]):
				cost = 0
			else:
				cost = 1
			d[(i, j)] = min(
				d[(i - 1, j)] + 1,
				d[(i, j - 1)] + 1,
				d[(i - 1, j - 1)] + cost,
			)
			if(i and j and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]):
				d[(i, j)] = min(d[(i, j)], d[i - 2, j - 2] + cost)
	return d[lenstr1 - 1, lenstr2 - 1]


def from_str_to_dict(a):
	l1 = 0
	l2 = 0
	num = 0
	for i in a:
		if(i == "\""):
			num += 1
		if(num == 1):
			l1 += 1
		if(num == 3):
			l2 +=1
	try:
		b = {str(a[2 : l1 + 1]) : int(a[l1 + 4 : l1 + l2 + 3])}
	except:
		b = {str(a[2 : l1 + 1]) : str(a[l1 + 4 : l1 + l2 + 3])}
	return b

def create_answer(data):
	print(data)
	user_id = data['from_id']
	message, attachment = get_answer(data)
	send_message(data, message, attachment)

def get_answer(data):
	body = data['text'].lower()
	user_id = str(data['from_id'])
	check_list = list(body.split())
	cs = check_situation(data)
	data_task, info_about_id = load_json()
	command = check_answer(body)

	try:
		payload = from_str_to_dict(data['payload'])
		if(payload['button'] == 'task'):
			return 'Выберите тему.', ''

		if(payload['button'] == 'parity' or 
		   payload['button'] == 'assessment' or
		   payload['button'] == 'graphs' or
		   payload['button'] == 'pst'):
			return 'Выберите номер.', ''

		try: 
			num = int(payload['button'])
			theme = info_about_id[user_id]['active_task'][0]
			message = 'Задача номер ' + str(num + 1) + ' из темы ' +  data_task[theme]['name'] + ' со сложностью ' + str(data_task[theme]['point'][num]) + ':\n\n'
			task = data_task[theme]['task'][num]
			return message + task + about_answer, ''
		except:
			pass

		if(payload['button'] == 'next'):
			command = 6

		if(payload['button'] == 'previous'):
			command = 7

	except:
		pass

	if(check_swearing_words(check_list)):
		return 'У нас не матерятся.', ''
	

	if(command == None):
		return "Я еще слишком тупой, чтобы понимать, что ты говоришь. Напиши 'помощь', чтобы ознакомиться с возможностями бота.", ''

	elif(command == 0):
		return "Привет, напиши 'помощь', чтобы ознакомиться с возможностями бота.", ''

	elif(command == 1):
		return help_list, ''

	elif(command == 2 and cs == True):
		return wrong_task, ''

	elif(command == 2 and cs == False):
		return 'хочу задачу', ''

	elif(command == 3 and cs == True):
		return wrong_task, ''

	elif(command == 3 and cs == False):
		try:
			theme = get_theme(check_list, 'номер')	
			num = int(find_after(check_list, 'номер'))
			count1 = 0
			distance = 99999999
			for i in opp_theme:
				count2 = 0
				for j in i:
					d = damerau_levenshtein_distance(theme, j)
					if(d < distance):
						distance = d
						right_key_1 = count1
						right_key_2 = count2
					count2 += 1
				count1 += 1
			if(distance < len(opp_theme[right_key_1][right_key_2])*0.3):
				task = data_task[themes[right_key_1]]['task'][num-1]
				update_json_task(user_id, themes[right_key_1], num)
				message = 'Задача номер ' + str(num) + ' из темы ' + data_task[themes[right_key_1]]['name'] + ' со сложностью ' + str(data_task[themes[right_key_1]]['point'][num -1]) + ':\n\n'
			return message + task + about_answer, ''
		except:
			return 'Неправильный ввод', ''

	elif(command == 4 and cs == True):
		return wrong_task, ''

	elif(command == 4 and cs == False):
		try:
			theme = get_theme(check_list, 'сложность')	
			num = int(find_after(check_list, 'сложность'))
			count1 = 0
			distance = 99999999
			for i in opp_theme:
				count2 = 0
				for j in i:
					d = damerau_levenshtein_distance(theme, j)
					if(d < distance):
						distance = d
						right_key_1 = count1
						right_key_2 = count2
					count2 += 1
				count1 += 1
			if(distance < len(opp_theme[right_key_1][right_key_2])*0.3):
				try:
					temp_data = []
					for i in info_about_id[user_id]['task'][themes[right_key_1]]:
						if(data_task[themes[right_key_1]]['point'][i] == num):
							temp_data.append(i)
					number_of_task = random.choice(temp_data)
					task = data_task[themes[right_key_1]]['task'][number_of_task]
					update_json_task(user_id, themes[right_key_1], number_of_task)
					message = 'Задача номер ' + str(number_of_task + 1) + ' из темы ' + data_task[themes[right_key_1]]['name'] + ' со сложностью ' + str(num) + ':\n\n'
					return message + task + about_answer, ''
				except:
					return 'Задачи такой сложности нет. Выберите другую задачу.', ''
		except:
			return 'Неправильный ввод', ''

	elif(command == 5):
		if(info_about_id[user_id]['answer'] == True):
			message = 'хуй'
			answer = int(check_list[-1])
			if(data_task[info_about_id[user_id]['active_task'][0]]['answer'][info_about_id[user_id]['active_task'][1]] == answer):
				points = info_about_id[user_id]['points'] + data_task[info_about_id[user_id]['active_task'][0]]['point'][info_about_id[user_id]['active_task'][1]]
				message = "Молодец. Ты крутой.\nТеперь у тебя " + str(points) + ' ' + get_point(points) + "\nПопробуй решить следующюю задачу. Чтобы это сделать напиши 'следующая задача'."
				delete_json_task(user_id, info_about_id[user_id]['active_task'][0], info_about_id[user_id]['active_task'][1], data_task[info_about_id[user_id]['active_task'][0]]['point'][info_about_id[user_id]['active_task'][1]])
			else: 
				message = 'Неправильно.'
		elif(info_about_id[user_id]['answer'] == False):
			message = 'Вы ничего не решаете.'
		return message, ''
	
	elif(command == 6 and cs == False):
		return "Вы ничего не решаете.\nОзнакомтесь со списком команд, написав 'помощь'.", ''

	elif(command == 6 and cs == True):
		try:
			theme = info_about_id[user_id]['active_task'][0]
			number_of_task = info_about_id[user_id]['active_task'][1]
			for key, value in enumerate(info_about_id[user_id]['task'][theme]):
				if(value == number_of_task):
					new_key = key + 1
			if(new_key > len(data_task[theme]['task'])):
				return "Это последняя задача, другую тему можно выбрать, написав 'хочу задачу [тема] номер [№]'.", ''
			new_number_of_task = info_about_id[user_id]['task'][theme][new_key]
			task = data_task[theme]['task'][new_number_of_task]
			update_json_task(user_id, theme, new_number_of_task)
			message = 'Задача номер ' + str(new_number_of_task + 1) + ' из темы ' + data_task[theme]['name'] + ' со сложностью ' + str(data_task[theme]['point'][new_number_of_task]) + ':\n\n'
			return message + task + about_answer, ''
		except:
			return 'Что то пошло не так.', ''

	elif(command == 7 and cs == False):
		return "Вы ничего не решаете.\nОзнакомтесь со списком команд, написав 'помощь'.", ''

	elif(command == 7 and cs == True):
		try:
			theme = info_about_id[user_id]['active_task'][0]
			number_of_task = info_about_id[user_id]['active_task'][1]
			for key, value in enumerate(info_about_id[user_id]['task'][theme]):
				if(value == number_of_task):
					new_key = key - 1
			if(new_key < 0):
				return "Это первая задача, другую тему можно выбрать, написав 'хочу задачу [тема] номер [№]'.", ''
			new_number_of_task = info_about_id[user_id]['task'][theme][new_key]
			task = data_task[theme]['task'][new_number_of_task]
			update_json_task(user_id, theme, new_number_of_task)
			message = 'Задача номер ' + str(new_number_of_task + 1) + ' из темы ' + data_task[theme]['name'] + ' со сложностью ' + str(data_task[theme]['point'][new_number_of_task]) + ':\n\n'
			return message + task + about_answer, ''
		except:
			return 'Что то пошло не так.', ''

	elif(command == 8):
		try:
			random_theme = random.choice(list(info_about_id[user_id]['task']))
			if(random_theme == info_about_id[user_id]['active_task'][0]):
				random_theme = random.choice(list(info_about_id[user_id]['task']))
			random_task = int(random.choice(list(info_about_id[user_id]['task'][random_theme])))
			if(random_task == info_about_id[user_id]['active_task'][1]):
				random_task = int(random.choice(list(info_about_id[user_id]['task'][random_theme])))
			task = data_task[random_theme]['task'][random_task]
			update_json_task(user_id, random_theme, random_task)
			message = 'Задача номер ' + str(random_task + 1) + ' из темы ' +  data_task[random_theme]['name'] + ' со сложностью ' + str(data_task[random_theme]['point'][random_task]) + ':\n\n'
			return message + task + about_answer, ''
		except: 
			return 'что то пошло не так', ''

	elif(command == 9):
		my_dir = os.path.dirname(__file__)
		json_file_path = os.path.join(my_dir, 'top.json')
		with open(json_file_path, 'r') as rf1:
			top = json.load(rf1)
		top_list = ''
		count = 1
		for key, value in top.items():
			top_list += str(count) + '. ' + key + ' - ' + str(value) + '\n'
			count+=1
			if(count > 10):
				break
		return 'Топ:\n' + top_list, ''

	elif(command == 10):
		info_about_id[user_id]['answer'] = False
		my_dir = os.path.dirname(__file__)
		json_file_path = os.path.join(my_dir, 'info_id.json')
		with open(json_file_path, 'w') as wf:
			json.dump(info_about_id, wf)
		return 'Попробуй другую задачу. Даже у самых умных людей не получалось все сразу¯\_(ツ)_/¯.', ''

	elif(command == 11):
		return 'Он мой пупсик, а не твой.', "photo-188352493_457239051" # mathplace : "photo-182333326_457239070"

	else:
		return command_list[command], ''


def get_point(num):
	if(num%10 == 0
	or num%10 == 5 or num%100 == 11
	or num%10 == 6 or num%100 == 12
	or num%10 == 7 or num%100 == 13
	or num%10 == 8 or num%100 == 14
	or num%10 == 9):
		return 'очков'
	elif(num%10 == 1):
		return 'очко'
	else:
		return 'очка'

def load_json():
	my_dir = os.path.dirname(__file__)
	json_file_path_1 = os.path.join(my_dir, 'data.json')
	json_file_path_2 = os.path.join(my_dir, 'info_id.json')
	with open(json_file_path_1, 'r') as rf1:
		data_task = json.load(rf1)
	with open(json_file_path_2, 'r') as rf2:
		info_about_id = json.load(rf2)
	return data_task, info_about_id

def delete_json_task(user_id, key_1, key_2, point):
	my_dir = os.path.dirname(__file__)
	json_file_path = os.path.join(my_dir, 'info_id.json')
	with open(json_file_path, 'r') as rf:
		info_about_id = json.load(rf)
	info_about_id[user_id]['task'][key_1].remove(key_2)
	info_about_id[user_id]['points'] += point
	info_about_id[user_id]['answer'] = False
	with open(json_file_path, 'w') as wf:
		json.dump(info_about_id, wf)
	info = api.users.get(user_ids = user_id)
	name = info[0]['first_name'] + ' ' + info[0]['last_name']
	update_top(name, info_about_id[user_id]['points'])

def update_top(name, point):
	my_dir = os.path.dirname(__file__)
	json_file_path = os.path.join(my_dir, 'top.json')
	with open(json_file_path, 'r') as rf:
		top_list = json.load(rf)
	top_list[name] = point
	sort_list = list(top_list.items())
	sort_list.sort(key=lambda i: i[1], reverse = True)
	new_top_list = {}
	for key, value in sort_list:
		new_top_list[key] = value
	with open(json_file_path, 'w') as wf:
		json.dump(new_top_list, wf)

def update_json_task(user_id, key_1, key_2):
	my_dir = os.path.dirname(__file__)
	json_file_path = os.path.join(my_dir, 'info_id.json')
	with open(json_file_path, 'r') as rf:
		info_about_id = json.load(rf)
	info_about_id[user_id]['answer'] = True
	info_about_id[user_id]['active_task'] = [key_1, key_2]
	with open(json_file_path, 'w') as wf:
		json.dump(info_about_id, wf)


def get_theme(words, end_word):
	try:
		count = 0
		distance2 = 99999999
		for i in words:
			d2 = damerau_levenshtein_distance(i, end_word)
			if(d2 < distance2):
				distance2 = d2
				end = count
			count += 1
		message = ''
		for i in range(end):
			if(i != end - 1):
				message += words[i]	+ ' '
			else:
				message += words[i]
		return message
	except:
		return 'что то пошло не так'

def find_after(words, after_what):
	count = 0
	distance = 99999999
	for i in words:
		d = damerau_levenshtein_distance(i, after_what)
		if(d < distance):
			distance = d
			right_key = count
		count +=1
	try:
		return words[right_key + 1]
	except:
		return None

def check_situation(data):
	try:
		my_dir = os.path.dirname(__file__)
		json_file_path_1 = os.path.join(my_dir, 'info_id.json')
		with open(json_file_path_1, 'r') as rf:
			info_about_id = json.load(rf)
	except:
		info_about_id = {}

	try:
		if(info_about_id[str(data['from_id'])]['answer'] == True):
			return True
		else:
			return False
	except:
		info_about_id[str(data['from_id'])] = info
		with open(json_file_path_1, 'w') as wf:
			json.dump(info_about_id, wf)
		return False

		

def check_swearing_words(check_list):
	for i in check_list:
		distance = len(i)
		for j in list_of_swearing:
			d = damerau_levenshtein_distance(i, j)
			if(d < distance):
				distance = d
				if(distance < len(i)*0.4):
					return True
	return False

def check_answer(body):
	count = 0
	words = body.split()
	distance = len(body)
	for key in command_list:
		for k in key:
			d = damerau_levenshtein_distance(body, k)
			if(d < distance):
				distance = d
				right_key = count
			for i in words:
				d2 = damerau_levenshtein_distance(i, k)
				if(d2 < distance):
					distance = d2
					right_key = count
		count += 1
	if(distance < len(body)*0.3):
		return right_key
	else: 
		return None

def send_message(data, message, attachment):
	user_id = data['from_id']
	info = api.users.get(user_ids = user_id)
	message_for_me = info[0]['first_name'] + ' ' + info[0]['last_name'] + '\n' + data['text']
	data_task, info_about_id = load_json()

	try:
		payload = from_str_to_dict(data['payload'])
	except:
		payload = {'button' : ''}


	if(message[0:6] == 'Привет'):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = hello_keyboard)


	elif(message[0:7] == 'Команды' or payload['button'] == 'help'):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = help_keyboard)


	elif(message[0:3] == 'Топ' or payload['button'] == 'top'):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = main_keyboard)


	elif(message == 'хочу задачу' or payload['button'] == 'task'):
		number_of_theme = len(info_about_id[str(user_id)]['task'])
		n = math.ceil(number_of_theme/4)
		theme_keyboard = {"one_time" : True, "buttons" : [[0 for i in range(4)] for i in range(n)]}
		i = 0
		for key in info_about_id[str(user_id)]['task']:
			if(info_about_id[str(user_id)]['task'][key] != []):
				temp_dict = {"action" : {
									"type" : "text",
									"payload" : "{\"button\":\"" + key + "\"}",
									"label" : data_task[key]['name']},
							 "color" : "primary"}
				theme_keyboard['buttons'][i//4][i%4] = temp_dict
				i += 1
		theme_keyboard['buttons'][-1] = list(filter(None, theme_keyboard['buttons'][-1]))
		theme_keyboard = json.dumps(theme_keyboard, ensure_ascii = False).encode('utf-8')
		theme_keyboard = str(theme_keyboard.decode('utf-8'))
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = theme_keyboard)

	
	elif(message == 'Выберите номер.'):
		info_about_id[str(user_id)]['active_task'][0] = payload['button']
		my_dir = os.path.dirname(__file__)
		json_file_path = os.path.join(my_dir, 'info_id.json')
		with open(json_file_path, 'w') as wf:
			json.dump(info_about_id, wf)

		number_of_task = len(info_about_id[str(user_id)]['task'][payload['button']])
		n = math.ceil(number_of_task/4)
		task_keyboard = {"one_time" : True, "buttons" : [[0 for i in range(4)] for i in range(n)]}
		i = 0
		for key in info_about_id[str(user_id)]['task'][payload['button']]:
			temp_dict = {"action" : {
								"type" : "text",
								"payload" : "{\"button\":\"" + str(key) + "\"}",
								"label" : str(key + 1)},
						 "color" : "primary"}
			task_keyboard['buttons'][i//4][i%4] = temp_dict
			i += 1
		task_keyboard['buttons'][-1] = list(filter(None, task_keyboard['buttons'][-1]))
		task_keyboard = json.dumps(task_keyboard, ensure_ascii = False).encode('utf-8')
		task_keyboard = str(task_keyboard.decode('utf-8'))
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = task_keyboard)


	elif(type(payload['button']) == int and payload['button'] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][0] and payload['button'] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][-1]):
		info_about_id[str(user_id)]['active_task'][1] = payload['button']
		info_about_id[str(user_id)]['answer'] = True
		my_dir = os.path.dirname(__file__)
		json_file_path = os.path.join(my_dir, 'info_id.json')
		with open(json_file_path, 'w') as wf:
			json.dump(info_about_id, wf)

		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = without_keyboard)
	
	elif(type(payload['button']) == int and payload['button'] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][0]):
		info_about_id[str(user_id)]['active_task'][1] = payload['button']
		info_about_id[str(user_id)]['answer'] = True
		my_dir = os.path.dirname(__file__)
		json_file_path = os.path.join(my_dir, 'info_id.json')
		with open(json_file_path, 'w') as wf:
			json.dump(info_about_id, wf)

		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = without_previous_keyboard)

	elif(type(payload['button']) == int and payload['button'] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][-1]):
		info_about_id[str(user_id)]['active_task'][1] = payload['button']
		info_about_id[str(user_id)]['answer'] = True
		my_dir = os.path.dirname(__file__)
		json_file_path = os.path.join(my_dir, 'info_id.json')
		with open(json_file_path, 'w') as wf:
			json.dump(info_about_id, wf)

		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = without_next_keyboard)

	elif(type(payload['button']) == int):
		info_about_id[str(user_id)]['active_task'][1] = payload['button']
		info_about_id[str(user_id)]['answer'] = True
		my_dir = os.path.dirname(__file__)
		json_file_path = os.path.join(my_dir, 'info_id.json')
		with open(json_file_path, 'w') as wf:
			json.dump(info_about_id, wf)

		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = answer_keyboard)


	elif(payload['button'] == 'previous' and info_about_id[str(user_id)]['active_task'][1] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][0]):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = without_previous_keyboard)

	elif(payload['button'] == 'next' and info_about_id[str(user_id)]['active_task'][1] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][-1]):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = without_next_keyboard)


	elif(payload['button'] == 'previous'):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = answer_keyboard)

	elif(payload['button'] == 'next'):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = answer_keyboard)


	elif(message[0:8] == 'Молодец.'):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = main_keyboard)


	elif(message[0:6] == 'Вы еще' and
		info_about_id[str(user_id)]['active_task'][1] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][0] and
		info_about_id[str(user_id)]['active_task'][1] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][-1]):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = without_keyboard)

	elif(message[0:6] == 'Вы еще' and info_about_id[str(user_id)]['active_task'][1] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][0]):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = without_previous_keyboard)

	elif(message[0:6] == 'Вы еще' and info_about_id[str(user_id)]['active_task'][1] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][-1]):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = without_next_keyboard)

	elif(message[0:6] == 'Вы еще'):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = answer_keyboard)

	
	elif(message[0:12] == 'Неправильно.' and
		info_about_id[str(user_id)]['active_task'][1] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][0] and
		info_about_id[str(user_id)]['active_task'][1] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][-1]):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = without_keyboard)

	elif(message[0:12] == 'Неправильно.' and info_about_id[str(user_id)]['active_task'][1] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][0]):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = without_previous_keyboard)

	elif(message[0:12] == 'Неправильно.' and info_about_id[str(user_id)]['active_task'][1] == info_about_id[str(user_id)]['task'][info_about_id[str(user_id)]['active_task'][0]][-1]):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = without_next_keyboard)

	elif(message[0:12] == 'Неправильно.'):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = answer_keyboard)


	elif(message[0:8] == 'Попробуй' or payload['button'] == 'end'):
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment, keyboard = main_keyboard)


	else:
		api.messages.send(access_token = settings.access_token, user_id = str(user_id), message = message, attachment = attachment)
	
	api.messages.send(access_token = settings.access_token, user_id = str(settings.top_id), message = message_for_me, attachment = '')