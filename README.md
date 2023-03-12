# Aiogram Telegram Bot - бот для упрощения учебного процесса у школьников.

<img src="https://img.shields.io/github/last-commit/ftdt800/School_Bot?style=for-the-badge">

## Описание проекта

Данный проект является эксперементом, и тестированием моих знаний. Создавался для решения 
конкретной задачи и был внедрен в учебные-процессы реальной школы. 
Возможно содержит ошибки в логике программы и исполняемом коде.

## Технологический стек
- [Python](https://www.python.org/)
- [Aiogram 3](https://docs.aiogram.dev/en/dev-3.x/)
- [Aioschedule](https://github.com/ibrb/python-aioschedule)
- [SQLite 3](https://docs.python.org/3/library/sqlite3.html)
- [emoji](https://emoji-python.readthedocs.io/en/stable/)
- [secrets](https://docs.python.org/3/library/secrets.html)
- [datetime](https://docs.python.org/3/library/datetime.html)

## Установка
<b>Этот бот находится в предварительной версии и еще не выпущен. Некоторые функции могут работать неправильно.</b>
* Создать файл ```config.py```
* Вставить в файл переменные с <b>Api_token</b> (берётся здесь @botfather) и свой <b>user_id</b> (для доступа администратора)
```
API_TOKEN = TOKEN_HERE
admin_id = ID_HERE
```
* Создать базу данных SQLite3 ```DataBase.db```
* Установить все библеотеки, и запустить ```main.py```
## Демо

![image](https://user-images.githubusercontent.com/79777228/224525175-0035865e-33ee-4594-9854-e639a0265e2c.png)


![image](https://user-images.githubusercontent.com/79777228/224524982-dec38def-b624-4bd6-a88b-b084ca1ebaa8.png)

## Реализованные функции
- Регистрация пользователя через telegram с добавлением в БД
- База для хранения данных SQLite3, для хранения состояний 
  aiogram
- Администрирование через админ-панель telegram

### Администрирование
- Добавление уроков (Название, время, кабинет)
- Составление расписания на определенный день
- Удаление/исправление расписания и уроков
- Рассылка расписания на конкретную дату пользователям

### Клиентская часть
- Регистрация (Айди пользователя, класс)
- Ежедневное напоминание о окончании уроков, с указанием следующего
- Возможность согласиться, отказаться от уведомлений о окончании урока

## Автор
RomaVol
Telegram: https://t.me/ftdt800

