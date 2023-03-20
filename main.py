# -*- coding: utf-8 -*-
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3 as sl
import asyncio
import aioschedule
import secrets
from src.config import *
from src.admin_functions import *
bot = aiogram.Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
# __________________________Данные бота__________________________
timelist_start = ["13:15","14:00", "14:55", "15:50", "16:45", "17:35", "18:20"]
timelist_end = ["12:55", "13:55", "14:40", "15:35", "16:30", "17:25", "18:15"]
friendlylist = ["Как следует отдохни на перемене, и бегом на урок" + emoji.emojize(":smiling_face_with_smiling_eyes:")+ "\nНа часах тем временем уже ",
                "Надеюсь у тебя остались силы на ещё один урок"+ emoji.emojize(":winking_face:") + "\nУчись хорошо, я буду следить!" + emoji.emojize(":upside-down_face:")+ "\nСейчас ",
                "Мне тут анекдот вспомнился, как-то раз на экзамене по математике один ученик загнул такое, что даже параллельные линии пересеклись.\nВот умора, я чуть не завис от смеха" + emoji.emojize(":face_with_tears_of_joy:") + "\nА тем временем на часах "
                ]
weekdays = {1: '<b>Понедельник</b>',
            2: '<b>Вторник</b>',
            3: '<b>Среда</b>',
            4: '<b>Четверг</b>',
            5: '<b>Пятница</b>',
            6: '<b>Суббота</b>',
            7: '<b>Воскресенье</b>'}
klass = {"8V": 1,
        "8A": 2,
         "8B": 3}
cb = CallbackData("text","action")
main_inline_full = InlineKeyboardMarkup(row_width=2)
main_inline_full.add(InlineKeyboardButton('Расписание на сегодня...', callback_data='raspisanie'))
main_inline_full.add(InlineKeyboardButton('Уведомление о начале и окончании урока...', callback_data='signal'))
rasp_inline_full = InlineKeyboardMarkup(row_width=2)
rasp_inline_full.add(InlineKeyboardButton(emoji.emojize(":check_mark_button:")+'Включить', callback_data='on_signal'))
rasp_inline_full.add(InlineKeyboardButton(emoji.emojize(":no_entry:")+'Отключить', callback_data='off_signal'))
add_in_klass = InlineKeyboardMarkup(row_width=4)
add_in_8A = (InlineKeyboardButton('8A...', callback_data='add_in_8A'))
add_in_8B = (InlineKeyboardButton('8Б...', callback_data='add_in_8B'))
add_in_8V = (InlineKeyboardButton('8В...', callback_data='add_in_8V'))
add_in_another = (InlineKeyboardButton('Учитель...', callback_data='add_in_Teacher'))
add_in_klass.add(add_in_8A, add_in_8B, add_in_8V, add_in_another)
send_menu = InlineKeyboardMarkup(row_width=2)
send_menu.add(InlineKeyboardButton(text="Отправить💬", callback_data=cb.new(action="send")),
              InlineKeyboardButton(text="Заполнить заново", callback_data=cb.new(action='application')))
#==========================================================FSM Machine (Костыль + Велосипед)
class get_answer(StatesGroup):
    answer1 = State()
async def send_state(call: aiogram.types.CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data["action"]
    if action == "send":
        await bot.send_message(admin_id, f"Поступила новая заявка от @{str(ans0)}\n"#username
                                                    f"Класс: <b>{str(ans1)}</b>\n"#klass
                                                    f"Телеграм айди: <b>{str(ans2)}</b>\n"  #user_id
                               , parse_mode=aiogram.types.ParseMode.HTML, reply_markup=admin_menu(call.from_user.id))
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="Заявка отправлена, в скором времени мы свяжемся с вами.")
        await state.finish()
    if action == "application":
        await state.finish()
        await send_welcome(message = call)
    await call.answer()
async def access(call: aiogram.types.CallbackQuery):  # Обработка заявки
    temp = [call.data[1:2], call.data[2:]]
    if temp[0] == "y":
        await bot.edit_message_text(chat_id=admin_id, message_id=call.message.message_id, text="Вы приняли заявку✅")
        await bot.send_message(temp[1], f'Поздравляю, вы добавлены в базу ✅\n\n'
                                        f'Теперь вам доступны уведомления о началах уроков, расписание и многое другое!\n'
                                        f'Для перехода в меню напишите команду /menu', disable_web_page_preview=True, parse_mode=aiogram.types.ParseMode.HTML)
        try:
            sql = sl.connect('src/DataBase.db')
            cursor = sql.cursor()
            print("Подключен к SQLite")
            if ans1 == "Teacher":
                admin_status = 'True'
            else:
                admin_status = 'False'
            print(ans2,admin_status,ans1,ans0)
            sqlite_insert_query = """INSERT INTO USER
                                  (id, admin, class, notifications, username)
                                  VALUES(?, ?, ?, ?, ?);"""
            changing = (ans2,admin_status,ans1,'False','@'+ans0)
            cursor.execute(sqlite_insert_query,changing)
            sql.commit()
            print("Запись успешно вставлена ​​в таблицу", cursor.rowcount)
            cursor.close()

        except sl.Error as error:
            print("Ошибка при работе с SQLite", error)
        finally:
            if sql:
                sql.close()
                print("Соединение с SQLite закрыто")
    elif temp[0] == "n":
        await bot.edit_message_text(chat_id=admin_id, message_id=call.message.message_id, text="Вы отклонили заявку❌")
        await bot.send_message(temp[1], 'Извините, вы нам не подходите ❌')

    await call.answer()
async def confirm_send(call: aiogram.types.CallbackQuery, answer1):
    print(call.from_user.id, call.from_user.username, answer1)
    await bot.send_message(call.from_user.id, f'Вы выбрали: <b>{answer1}</b>', parse_mode=aiogram.types.ParseMode.HTML, reply_markup=send_menu)
    global ans1
    global ans2
    global ans0
    ans1 = answer1
    ans2 = call.from_user.id
    ans0 = call.from_user.username
#==================================================
@dp.message_handler(commands=['start', 'help', 'menu'])#First message
async def send_welcome(message: aiogram.types.Message):
    sql = sl.connect('src/DataBase.db')
    cursor = sql.cursor()
    cursor.execute("SELECT COUNT(*) FROM USER WHERE id = ?", (message.from_user.id,))
    if cursor.fetchone()[0] > 0:
        await bot.send_message(message.from_user.id,f'Привет житель Седьмого Континента!'+ emoji.emojize(":winking_face:")+'\nЯ помогу тебе со школьной рутиной, можешь положиться на меня...\nЯ могу подсказать расписание звонков,'+ emoji.emojize(":bell:")+'\nНаписать изменение расписания,'+ emoji.emojize(":pushpin:")+'\nИ много чего ещё...)\nНиже ты можешь выбрать интересующую категорию!'+ emoji.emojize(":backhand_index_pointing_down:"),parse_mode="Markdown", reply_markup=main_inline_full)
    else:
        await bot.send_message(message.from_user.id, "Приветствую! Вас ещё нет в списке учащихся 7 школы города Кемерово, выберите свой класс ниже..."+ emoji.emojize(":backhand_index_pointing_down:"),parse_mode="Markdown", reply_markup=add_in_klass)
    sql.close()
    cursor.close()
# @dp.message_handler()  # Принимаем любые сообщения
# async def echo_message(message: aiogram.types.Message):
#     await message.reply("Простите, но я не понимаю этого... Для вызова главного меню нажмите сюда -> /start")
@dp.callback_query_handler(lambda c: c.data == 'add_in_8A')
async def process_callback_button(call: aiogram.types.CallbackQuery):
    await confirm_send(call, answer1="8A",)
@dp.callback_query_handler(lambda c: c.data == 'add_in_8B')
async def process_callback_button(call: aiogram.types.CallbackQuery):
    await confirm_send(call, answer1="8B",)
@dp.callback_query_handler(lambda c: c.data == 'add_in_8V')
async def process_callback_button(call: aiogram.types.CallbackQuery):
    await confirm_send(call, answer1="8V",)
@dp.callback_query_handler(lambda c: c.data == 'add_in_Teacher')
async def process_callback_button(call: aiogram.types.CallbackQuery):
    await confirm_send(call, answer1="Teacher",)
@dp.callback_query_handler(lambda c: c.data == 'raspisanie')
async def process_callback_button(callback_query: aiogram.types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_photo(callback_query.from_user.id, photo = open('src/img/rasp.jpeg', 'rb'), caption="Расписание обновленно 10.02.2023" + emoji.emojize(":winking_face:"))
@dp.callback_query_handler(lambda c: c.data == 'signal')#
async def process_callback_button(callback_query: aiogram.types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,"Функция разработанная специально для тебя!\nВключи, и перед каждым уроком я буду подсказывать следующий урок"+emoji.emojize(":winking_face:"),reply_markup=rasp_inline_full)
@dp.callback_query_handler(lambda c: c.data == 'on_signal')#
async def process_callback_button(callback_query: aiogram.types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,emoji.emojize(":check_mark_button:") + "Уведомления о уроках включены!")
    sql = sl.connect('src/DataBase.db')
    cursor = sql.cursor()
    cursor.execute('SELECT notifications FROM USER WHERE notifications="False" AND id="' + str(callback_query.from_user.id) + '"').fetchall()  # search myself
    cursor.execute('UPDATE USER SET notifications=? WHERE id=?',('True', callback_query.from_user.id))  # refresh info
    print(f'Статус изменен на True для следуещего пользователя {callback_query.from_user.id}')
    sql.commit()
    sql.close()
@dp.callback_query_handler(lambda c: c.data == 'off_signal')#
async def process_callback_button(callback_query: aiogram.types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,emoji.emojize(":no_entry:") + "Уведомления о уроках выключены!")
    sql = sl.connect('src/DataBase.db')
    cursor = sql.cursor()
    cursor.execute('SELECT notifications FROM USER WHERE notifications="True" AND id="'+str(callback_query.from_user.id)+'"').fetchall()# search myself
    cursor.execute('UPDATE USER SET notifications=? WHERE id=?', ('False', callback_query.from_user.id))  # refresh info
    print(f'Статус изменен на False для следуещего пользователя {callback_query.from_user.id}')
    sql.commit()
    sql.close()
async def aioschelder_loop():
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)
async def on_startup(_):
    #await time_print(time_str="15:35")#debug function
    #return
    if datetime.datetime.today().weekday() <= 4:
        print(timelist_end)
        for date in timelist_end:
            aioschedule.every().day.at(time_str=date).do(time_print, time_str=date)
    asyncio.create_task(aioschelder_loop()) #comments for debug function
    print('День недели: '+weekdays.get(datetime.datetime.today().weekday()+1) + "Время: " + datetime.datetime.today().strftime('%H:%M'))

async def time_print(time_str):
    print("Время сейчас, "+time_str)
    sql = sl.connect('src/DataBase.db')
    users = sql.execute("SELECT id FROM USER WHERE notifications='True'").fetchall()
    clas = sql.execute("SELECT class FROM USER WHERE notifications='True'").fetchall()
    for i in range(len(users)):
        print(str(users[i][0])+ " айди")
        print(clas[i][0]+ " класс")
        print(str(datetime.datetime.today().weekday())+ " День недели")
        print(datetime.datetime.now().strftime("%A") + " Прям день недели")
        print(str(klass.get(clas[i][0]))+ " класс но цыфра")#number klass in base
        usertextlist = sql.execute(f"SELECT {datetime.datetime.now().strftime('%A').lower()} FROM RASP WHERE class = ?;",
                                   (clas[i][0],)).fetchall()
        schedulelist_str = (str(usertextlist[i][0]).split(","))
        if not str(schedulelist_str[timelist_end.index(time_str)])[0] == "-":
            await bot.send_message(users[i][0], "<u>" + str(schedulelist_str[timelist_end.index(time_str)])+"</u>\n"+ str(secrets.choice(friendlylist)) +"<u>" + str(timelist_end[timelist_end.index(time_str)])+ "</u>", parse_mode="HTML")
        else:
            print("Урока нет, согласно расписанию")
def register_handlers_client(dp: Dispatcher):
    dp.register_callback_query_handler(send_state, cb.filter(action=["send", "application"]), state="*")
    dp.register_callback_query_handler(access, text_contains="#")
register_handlers_client(dp)  # start dispatcher
if __name__ == '__main__':
    from src import dp
    print(admin_id, API_TOKEN)  # testing import config file
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
