"""
Голосовой помощник будет служить для выполнения задач разного спектра,
например, банальные благодаря которым пользователь сможет
узнать погоду, время, узнать что-либо в интернете. Помимо того предпола-
гается, что помощник сможет взаимодействовать и с компьютером: сможет
его выключить, презагрузить, открыть приложение или файл из папки.

Голосовой помощник будет откликатся по имени, которое ему сможет дать
пользователь. Все необходимые данные для работы программы будут хранится
в отдельных файлах (txt, db, csv).

Помимо того ГП будет сохранять все те запросы на которые не может дать
ответ для того чтобы разработчик мог постоянно дополнять приложение
функционалом.
"""
import requests
import vk_api
import pyttsx3
import webbrowser
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
import time
import os
import locale
import speech_recognition as sr
import sys
import sqlite3
from translate import Translator
from langdetect import detect


class VoiceHelp(QMainWindow):
    """
    Основное приложение

    Класс который отписавет основное приложение
    Подлючает интрефейс, подключет функции к кнопкам,
    описывает функции которые реагируют на команды
    пользовотателя и работают с файлами которые
    необходимы для рабты проложения
    """

    def __init__(self):
        """
        Подключение интефейса приложения и задача ввех размеров
        Инициализация всех преременных необходимызх для работы

        А также назначение функций на кнопки
        """
        super(VoiceHelp, self).__init__()
        uic.loadUi('files_for_work/interface.ui', self)
        self.setFixedSize(402, 525)

        self.task = ''

        self.place = 'Кириши'

        self.day = time.strftime('Сейчас %d %B, %A')
        self.times = time.strftime('%H:%M')

        self.enter_btn.clicked.connect(self.program_execution)
        self.record_btn.clicked.connect(self.speech_2_text)

    def task_reform(self, task):
        """
        :param task: (string) Задача которая будет отправлена в файл
        :return: None

        Итог работы в files/revision.txt

        Функция отвечающая за добавлние неизвестных комад
        в файл куда будут заглядывать разработчики и брать
        команды для попления функционала приложения
        """
        print('Добалнение в реестр новой неизвестной команды: ' + task)
        f = open('files_for_work/revision.txt', mode="a", encoding='utf-8')
        f.write(task + '\n')
        f.close()

    def system(self, task):
        """
        :param task: (string) Задача которая будет даваться программе
        :return: (string) Фраза которая будет отвечать пользователю
                и делать илюзию небольшого общения

        Функция которая будет выполнять программы связанные с работой
        в системе. Это такоя такая катероя из всех таких функций
        """
        task = task.lower()
        if ('перезагрузи' and 'копмьютер') in task:
            os.system(['shutdown', '-r' '-t', '0'])
            return 'минуточку'
        elif ('выключи' and 'компьютер') in task:
            os.system('shutdown -s')
            return 'Выключаю!'
        return False

    def browser(self, task, flag=False):
        """
        :param task: (string) Задача которая будет даваться программе
        :param flag: (boolean) Метка отвечающая за грамотное отображение
                    вывода результата программы
        :return: (string) Фраза которая будет отвечать пользователю
                и делать илюзию небольшого общения

        Фуекция которая отвечает за выполнение тех задач
        которые связаны с работой с браузере

        P.S Открывается браузер который поставлен по умолчанию
        """
        task = task.lower()

        if flag is True:
            if 'открой' and ('youtube' or 'ютуб') in task:
                url = 'https://www.youtube.com'
                webbrowser.open(url)
            elif 'открой' and ('gmail' or 'гмаил' or 'почту') in task:
                url = 'https://mail.google.com'
                webbrowser.open(url)
            elif 'открой' and ('mail' or 'маил') in task:
                url = 'https://mail.ru'
                webbrowser.open(url)
            elif 'открой' and ('twitch' or 'твич') in task:
                url = 'https://twitch.tv'
                webbrowser.open(url)
            elif 'открой' and ('твитер' or 'твиттер' or 'twitter') in task:
                url = 'https://twitter.com'
                webbrowser.open(url)
            elif 'открой' and ('вк' or 'вконтакте' or 'vk' or 'vkontakte') in task:
                url = 'https://vk.com'
                webbrowser.open(url)
            elif 'как' or 'какой' or 'что' or 'чего' in task:
                url = f'https://yandex.ru/search/?lr=10871&text={task}'
                webbrowser.open(url)
                return 'Попытаюсь найти в интернете!'
            return 'открываю'
        else:
            return True

    def msg_2_developer(self, task):
        """
        :param task: (string) Задача которая будет отправлена в файл
        :return: (string) Простой текст

        Функция благодаря которой можно напрямую обратится
        к разработчику с пожеланиями
        """
        if ('пожелания' or 'сообщнение') and 'разработчику':
            self.task_reform(task)
            return 'Ваше сообщение отправлено!'

    def command(self, task):
        """
        :param task: (string) Задача которая будет даваться программе
        :return: (string) Фраза которая будет отвечать пользователю
                и делать илюзию небольшого общения

        Функция которая служит для выполнения команд
        которые нельза отнести, по каким либо,
        причинам к какойто категории, поэтому
        они будут обрабатыватся здесь и ответы
        будут исходить их этой функции
        """
        locale.setlocale(locale.LC_ALL, 'Russian_Russia.1251')

        if ('день' or ('какое' and 'число')) in task:
            return self.day

        elif 'погода' in task:
            api_owm = '635ff672c2bc9116392a97f19abc50c9'
            url = f'http://api.openweathermap.org/data/2.5/weather?APPID={api_owm}&lang=ru&q={self.place}'

            data_weather = requests.get(url).json()

            temp = round(data_weather['main']['temp'] - 273.15)
            cloud = data_weather['weather'][0]['description']

            return f'Температура в {self.place} сейчас в районе {int(temp)} градусов, {cloud}'

        elif ('время' or 'час') in task:
            return f'В данный момент{self.times}'
        elif 'переведи' and 'текст' in task:
            task = task.lower().split('переведи текст ')
            task = ''.join(task[1])
            lang = detect(task)
            if lang == 'ru' or lang == 'mk':
                trans = Translator(from_lang=lang, to_lang='en')
                return trans.translate(str(task))
            else:
                trans = Translator(from_lang=lang, to_lang='ru')
                return trans.translate(str(task))
        return False

    def program_execution(self):
        """
        Эта функция ничего в себя не принимает
        так как является назначенной на объект

        :return: None

        Данная функия собрает все иписанные функции
        которые выполняют, те или иные, задачи
        связанные с отвем на задание пользователя

        Это функция назначана на объект(кнопку)
        self.enter_btn
        """
        task = self.command_receiver.text().lower()

        con = sqlite3.connect('files_for_work/data.sqlite')
        cur = con.cursor()

        user_info = cur.execute(f"""SELECT * FROM user_info""").fetchall()

        user_name = user_info[0][1]
        vh_name = user_info[0][0]

        if task == '':
            QMessageBox.critical(self, "Ошибка ",
                                 "При отправке команды не оствляйте это поле пустым",
                                 QMessageBox.Ok)
        elif 'смена' in task and 'имени' in task:
            self.change_name()
        elif 'смена' in task and 'апи' in task:
            self.change_vk_api()
        elif 'обучение' in task:
            tutor.show()
        elif 'напиши' and 'сообщение' in task:
            """
            Этот фрагмент кода не вынесен отдельно просто так :-)
            """
            self.message_print(user_name, self.command_receiver.text())
            task = self.command_receiver.text().split()

            con = sqlite3.connect('files_for_work/data.sqlite')
            cur = con.cursor()

            api = cur.execute(f"""SELECT user_vk FROM user_profile """).fetchone()
            if api != '':
                session = vk_api.VkApi(token=api)
                vk = session.get_api()

                for i in vk.friends.get()['items']:
                    user = session.method("users.get", {"user_ids": i})
                    if user[0]['first_name'] in task:
                        msg = task[task.index(user[0]['first_name']) + 1:]
                        vk.messages.send(user_id=int(user[0]['id']), message=' '.join(msg), random_id=0)
            else:
                self.change_vk_api()
            self.message_print(vh_name, self.speak('Уже исполняю'))
        elif 'and' and 'ты' and 'умеешь' in task:
            self.message_print(user_name, task)

            self.message_print(vh_name, self.speak(
                'Я могу многое например: Отправить сообщение другу\n'
                'Показать Вам погоду или время\n'
                'Превести Ваш текст\n'
                'А если вам не хватает чего-то\n'
                'Просто напиши прямо в строку команд'
            ))
        elif self.command(task) is not False:
            self.message_print(user_name, self.command_receiver.text())

            self.message_print(vh_name, self.speak(self.command(task)))
        elif self.browser(task) is not False:
            self.message_print(user_name, self.command_receiver.text())

            self.message_print(vh_name, self.browser(task, flag=True))
            self.speak('Открываю')
        elif self.system(task) is not False:
            self.message_print(user_name, self.command_receiver.text())

            self.message_print(vh_name, self.system(task))
            self.speak(self.system(task))
        else:
            print(self.task_reform(task))

        self.command_receiver.setText('')

    def message_print(self, name, text):
        """
        :param name: (string) Имя того кто будет выводится
        :param text: (string) Задача которая будет даваться программе
        :return: None

        Данная фунция отображает в поле
        QTextBrowser сообщение которое будет отсылать
        пользователь или программа в Формате

        (Имя) (Время)
        --------------------------------
        (Текст сообщения)
        --------------------------------
        """
        self.message_box.append(f'<b>{name}</b> {self.times}')
        self.message_box.append(f'--------------------------------')
        self.message_box.append(text.capitalize())
        self.message_box.append(f'--------------------------------')
        self.message_box.append('\n')

    def speak(self, what):
        """
        :param what: (string) Сообщение которое будет
                    говорить программа 'голосом компьютера'
        :return: (string) Текст того что сказала программа

        Функция которая принимает сообщение  и
        с помощью компьэтера произносит это сообщение
        """
        engine = pyttsx3.init()
        engine.say(what)
        engine.runAndWait()

        return what.capitalize()

    def speech_2_text(self):
        """
        Эта функция ничего в себя не принимает
        так как является назначенной на объект

        :return: None

        Эта функция по нажатию на назначенную кнопку
        преобразует голос пользователя в текст
        И вставляет его в поле для ввода для
        того чтобы корректировать введенный текст

        В случае если то что сказал пользователь
        очень расходится с понятием программы
        то повторным нажатием на назначенную
        кнопку ползователь может перезаписать
        команду

        Назначена на кнопку - record_btn
        Взаиможействует с полем для ввода - command_receiver
        """
        self.command_receiver.setText('')
        r = sr.Recognizer()
        r.pause_threshold = 0.5

        with sr.Microphone() as sourse:
            r.adjust_for_ambient_noise(sourse, duration=0.5)
            audio = r.listen(sourse)
            query = r.recognize_google(audio, language='ru-RU')
        self.command_receiver.setText(query)

    def change_name(self):
        """
        :return: None

        Функция которая открывает окно
        в которой можно будет сменить
        введеное имя пользователя и
        имя голосового помощника
        """
        name_app.show()

    def change_vk_api(self):
        """
        :return: None

        Функция которая открывает окно
        в которой можно будет сменить
        API ключь которыый необходим для
        отправки сообщений в ВК
        """
        vk_app.show()


class NameUI(QMainWindow):
    """
    Приложение в котором можно будет сменить
    имя пользователя и имя голосового
    помощника
    """

    def __init__(self):
        """
        Функция иницииализации в которой
        подключается интерфейс, задаются
        фиксированные размеры программы
        и подключаются функции к кнопкам
        """
        super(QMainWindow, self).__init__()
        uic.loadUi('files_for_work/interface_reg.ui', self)
        self.setFixedSize(438, 241)

        self.pushButton.clicked.connect(self.on_click)

    def on_click(self):
        """
        :return: None

        Функция которая открывает интерфейс,
        где можно булет сменить имя пользователя
        и имя голосовго помощника
        """

        con = sqlite3.connect('files_for_work/data.sqlite')
        cur = con.cursor()

        vh_name = self.vh_name.text()
        user_name = self.user_name.text()

        cur.execute(f"""UPDATE user_info SET vh_name = '{vh_name}', user_name = '{user_name}'""")
        con.commit()

        con.close()
        name_app.close()


class VkUI(QMainWindow):
    """
    Приложение в котором можно будет сменить
    имя пользователя и имя голосового
    помощника
    """

    def __init__(self):
        """
        Функция иницииализации в которой
        подключается интерфейс, задаются
        фиксированные размеры программы
        и подключаются функции к кнопкам
        """
        super(QMainWindow, self).__init__()
        uic.loadUi('files_for_work/vk_interface.ui', self)
        self.setFixedSize(362, 304)

        self.send_in_bd.clicked.connect(self.on_click)

    def on_click(self):
        """
        :return: None

        Функция которая открывает интерфейс,
        где можно булет сменить API ключь
        которыый необходим для отправки
        сообщений в ВК
        """
        con = sqlite3.connect('files_for_work/data.sqlite')
        cur = con.cursor()

        api = self.api_key.text()
        print(api)

        cur.execute(f"""UPDATE user_profile SET user_vk = '{api}'""")
        con.commit()

        con.close()
        vk_app.close()


class Tutorial(QMainWindow):
    """
    Интерфейс обучения по пользованию программы
    """

    def __init__(self):
        """
        Функция иницииализации в которой
        подключается интерфейс, задаются
        фиксированные размеры программы
        и подключаются функции к кнопкам
        """
        super(QMainWindow, self).__init__()
        uic.loadUi('files_for_work/tutorial.ui', self)
        self.setFixedSize(542, 505)


if __name__ == '__main__':
    """
    Точка входа в программе в которой:
    
    Запускаются интерфейсы всех нужных окон
    
    Запускается этап проверки БД на 
    нахождение в ней имени пользователя и
    голосового помощника
    """
    app = QApplication(sys.argv)

    main_app = VoiceHelp()
    name_app = NameUI()
    vk_app = VkUI()
    tutor = Tutorial()

    con = sqlite3.connect('files_for_work/data.sqlite')
    cur = con.cursor()

    user_info = cur.execute(f"""SELECT * FROM user_info""").fetchall()

    tutor_flag = cur.execute(f"""SELECT tutor FROM user_profile""").fetchall()

    if user_info[0][0] == '' or user_info[0][1] == '':
        name_app.show()

    if tutor_flag[0][0] == 0:
        print(tutor_flag[0][0])
        tutor.show()
        cur.execute(f"""UPDATE user_profile SET tutor = '1'""")
        con.commit()

    con.close()
    main_app.show()

    sys.exit(app.exec())
