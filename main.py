# -*- coding: utf-8 -*-
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from config import *
import sqlite3 as sl
import asyncio
import datetime
import aioschedule
import emoji
import secrets
from aiogram.utils import executor
import re #не используется
from aiogram.utils.markdown import text
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
print(admin_id, API_TOKEN)# testing import config file
# __________________________Данные бота__________________________
timelist_manday = ["13:55", "14:40", "15:35", "16:30", "17:25", "18:15"]#1-6
timelist_tuesday = ["18:46","13:55", "14:40", "15:35", "16:30", "17:25", "18:15"]#0-6
timelist_wednesday = ["12:55","13:55", "14:40", "15:35", "16:30", "17:25"]#0-5
timelist_thursday = ["12:55","13:55", "14:40", "15:35", "16:30", "17:25", "18:15"]#0-6
timelist_friday = ["12:55","13:55", "14:40", "15:35", "16:30", "17:25", "18:15"]#0-6

timelist_start = ["13:15","14:00", "14:55", "15:50", "16:45", "17:35", "18:20"]
timelist_end = ["16:07","12:55","13:55", "14:40", "15:35", "16:30", "17:25", "18:15"]

schedulelist_manday = ["ОБЖ в 213","Русский язык в 306", "Литература в 306","Обществознание в 404","Алгебра в 305","Геометрия в 305"]
schedulelist_tuesday = ["Черчение в 213","Русский язык в 306", "ИКТ в 211/301","Литература в 306","Физ-ра в спортзале","Родной русский в 306","Английский язык в 302/210"]
schedulelist_wednesday = ["География в 207","Физика в 212", "Геометрия в 305","Биология в 206","Биология в 206","История в 403"]
schedulelist_thursday = ["География в 207","Алгебра в 305","Химия в 214", "Музыка в 209","Физ-ра в спортзале","Физика в 212","Английский в 302/210"]
schedulelist_friday = ["Алгебра в 305","Русский язык в 306", "Технология в мастерской/406","ИЗО в 209","Химия в 214","История в 403","Английский язык в 302/210"]

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
main_inline_full = InlineKeyboardMarkup(row_width=2)
main_inline_full.add(InlineKeyboardButton('Расписание на сегодня...', callback_data='raspisanie'))
main_inline_full.add(InlineKeyboardButton('Уведомление о начале и окончании урока...', callback_data='signal'))
rasp_inline_full = InlineKeyboardMarkup(row_width=2)
rasp_inline_full.add(InlineKeyboardButton(emoji.emojize(":check_mark_button:")+'Включить', callback_data='on_signal'))
rasp_inline_full.add(InlineKeyboardButton(emoji.emojize(":no_entry:")+'Отключить', callback_data='off_signal'))
admin_klass = InlineKeyboardMarkup(row_width=2)
admin_klass.add(InlineKeyboardButton('8В...', callback_data='admin_8V'))
admin_klass.add(InlineKeyboardButton('8A...', callback_data='admin_8A'))
admin_rasp_inline_full = InlineKeyboardMarkup(row_width=3)
admin_back_list = (InlineKeyboardButton(emoji.emojize(":backhand_index_pointing_left:")+"Пред...", callback_data='admin_back_list'))
admin_change_list = (InlineKeyboardButton(emoji.emojize(":pencil:")+ "Изменить...", callback_data='admin_change_list'))
admin_next_list = (InlineKeyboardButton("След..."+emoji.emojize(":backhand_index_pointing_right:"), callback_data='admin_next_list'))
admin_rasp_inline_full.add(admin_back_list, admin_change_list, admin_next_list)
admin_cheking = InlineKeyboardMarkup(row_width=2)
admin_cheking_no = (InlineKeyboardButton("Нет! Изменить..."+emoji.emojize(":no_entry:"), callback_data='admin_cheking_no'))
admin_cheking_yes = (InlineKeyboardButton("Всё верно"+emoji.emojize(":check_mark_button:"), callback_data='admin_cheking_yes'))
admin_cheking.add(admin_cheking_yes, admin_cheking_no)
#==========================================================FSM Machine (Костыль + Велосипед)
class Form(StatesGroup):
    name = State()
@dp.callback_query_handler(lambda c: c.data == 'admin_change_list')
async def cmd_start(call: CallbackQuery):
    await Form.name.set()
    await call.message.answer("Впишите нужное расписание с 0 урока по 6, в случаи отсутсвии урока ставьте знак '-'"
                              "\nПример правильного добавления: (Первый и последний урок отсутствует)\n"
                              +weekdays.get(schedule_int+1)+
                              "\n"
                              + emoji.emojize(":down_arrow:") + emoji.emojize(":down_arrow:") + emoji.emojize(":down_arrow:") +
                              "\n-"
                              "\nОБЖ в 213"
                              "\nРусский язык в 306"
                              "\nЛитература в 306"
                              "\nОбществознание в 404"
                              "\nАлгебра в 305"
                              "\n-"
                              "\n"
                              + emoji.emojize(":up_arrow:") + emoji.emojize(":up_arrow:") + emoji.emojize(":up_arrow:") +
                              "\nВремя, как и день недели подгоняются <u>автоматически</u>, указывать их не требуется", parse_mode="HTML")
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Ну ладно, отмена')
@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        print(data['name'] + "лал")
        global DataTextCustom
        DataTextCustom = data['name']
        await message.reply('Сохранено!\nИзменённое расписание на '+weekdays.get(schedule_int+1)+'\n <code>'+ DataTextCustom +'</code>\nВсё верно?',parse_mode="HTML", reply_markup=admin_cheking)
    await state.finish()
#==================================================
@dp.message_handler(commands=['start', 'help', 'menu'])#First message
async def send_welcome(message: types.Message):
    await bot.send_message(message.from_user.id,f'Привет житель Седьмого Континента!'+ emoji.emojize(":winking_face:")+'\nЯ помогу тебе со школьной рутиной, можешь положиться на меня...\nЯ могу подсказать расписание звонков,'+ emoji.emojize(":bell:")+'\nНаписать изменение расписания,'+ emoji.emojize(":pushpin:")+'\nИ много чего ещё...)\nНиже ты можешь выбрать интересующую категорию!'+ emoji.emojize(":backhand_index_pointing_down:"),parse_mode="Markdown", reply_markup=main_inline_full)
@dp.message_handler(commands=['admin'])#Admin panel
async def send_welcome(message: types.Message):
    await bot.send_message(message.from_user.id,'Привет учитель Седьмого Континента!\nЗдесь можно изменять, заменять и удалять уроки, и корректировать расписание при его изменении\nНиже выбери нужный класс\n'+ emoji.emojize(":backhand_index_pointing_down:")+ emoji.emojize(":backhand_index_pointing_down:")+ emoji.emojize(":backhand_index_pointing_down:"), reply_markup=admin_klass)
@dp.callback_query_handler(lambda c: c.data == 'admin_8V')
async def process_callback_button(callback_query: types.CallbackQuery):
    await admin_preview_list(callback_query, klass=1)
@dp.callback_query_handler(lambda c: c.data == 'admin_8A')
async def process_callback_button(callback_query: types.CallbackQuery):
    await admin_preview_list(callback_query, klass=2)
async def admin_preview_list(callback_query: types.CallbackQuery, klass):
    await bot.answer_callback_query(callback_query.id)
    global klass_int
    global schedule_int
    schedule_int = 0
    klass_int = klass
    with open('rasp.txt', mode="r+", encoding="utf-8") as file:
        textlist = file.read().split("===")  # transform in massive
        print(textlist[klass_int])
        print(str(str(textlist[klass_int]).split("\n")[datetime.datetime.today().weekday()]).split(","))
        schedulelist = str(str(textlist[klass_int]).split("\n")[schedule_int+4]).split(",")
        Massiv_sum = [list(a) for a in zip(timelist_start, schedulelist)]
        text = '<u>'+'\n<u>'.join('</u> > '.join(l) for l in Massiv_sum)
        await bot.send_message(callback_query.from_user.id, weekdays.get(schedule_int+1)+"\n"+text, parse_mode="HTML", reply_markup=admin_rasp_inline_full)
@dp.callback_query_handler(lambda c: c.data == 'admin_next_list')#next
async def process_callback_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    global klass_int
    global schedule_int
    if schedule_int < 4:
        schedule_int += 1
    with open('rasp.txt', mode="r+", encoding="utf-8") as file:
        textlist = file.read().split("===")  # transform in massive
        print(textlist[klass_int])
        print(str(str(textlist[klass_int]).split("\n")[datetime.datetime.today().weekday()]).split(","))
        schedulelist = str(str(textlist[klass_int]).split("\n")[schedule_int+4]).split(",")
        Massiv_sum = [list(a) for a in zip(timelist_start, schedulelist)]
        text = '<u>'+'\n<u>'.join('</u> > '.join(l) for l in Massiv_sum)
        await callback_query.message.edit_text(weekdays.get(schedule_int+1)+"\n"+text, parse_mode="HTML", reply_markup=admin_rasp_inline_full)
@dp.callback_query_handler(lambda c: c.data == 'admin_back_list')#back
async def process_callback_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    global klass_int
    global schedule_int
    if schedule_int > 0:
        schedule_int -= 1
    with open('rasp.txt', mode="r+", encoding="utf-8") as file:
        textlist = file.read().split("===")  # transform in massive
        print(textlist[klass_int])
        print(str(str(textlist[klass_int]).split("\n")[datetime.datetime.today().weekday()]).split(","))
        schedulelist = str(str(textlist[klass_int]).split("\n")[schedule_int+4]).split(",")
        Massiv_sum = [list(a) for a in zip(timelist_start, schedulelist)]
        text = '<u>'+'\n<u>'.join('</u> > '.join(l) for l in Massiv_sum)
        await callback_query.message.edit_text(weekdays.get(schedule_int+1)+"\n"+text, parse_mode="HTML", reply_markup=admin_rasp_inline_full)
@dp.callback_query_handler(lambda c: c.data == 'raspisanie')
async def process_callback_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_photo(callback_query.from_user.id, photo = open('rasp.jpeg', 'rb'), caption="Расписание обновленно 10.02.2023"+emoji.emojize(":winking_face:"))
@dp.callback_query_handler(lambda c: c.data == 'signal')#
async def process_callback_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,"Функция разработанная специально для тебя!\nВключи, и перед каждым уроком я буду подсказывать следующий урок"+emoji.emojize(":winking_face:"),reply_markup=rasp_inline_full)

@dp.callback_query_handler(lambda c: c.data == 'on_signal')#
async def process_callback_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,emoji.emojize(":check_mark_button:") + "Уведомления о уроках включены!")
    sql = sl.connect('DataBase.db')
    cursor = sql.cursor()
    cursor.execute('SELECT notifications FROM USER WHERE notifications="False" AND id="' + str(callback_query.from_user.id) + '"').fetchall()  # search myself
    cursor.execute('UPDATE USER SET notifications=? WHERE id=?',('True', callback_query.from_user.id))  # refresh info
    print(f'Статус изменен на True для следуещего пользователя {callback_query.from_user.id}')
    sql.commit()
    sql.close()
@dp.callback_query_handler(lambda c: c.data == 'off_signal')#
async def process_callback_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,emoji.emojize(":no_entry:") + "Уведомления о уроках выключены!")
    sql = sl.connect('DataBase.db')
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
    await time_print(time_str="16:30")#debug function
    return
    if datetime.datetime.today().weekday() == 0:
        for date in timelist_end:
            aioschedule.every().monday.at(time_str=date).do(time_print, time_str=date)
    if datetime.datetime.today().weekday() == 1:
        for date in timelist_end:
            aioschedule.every().tuesday.at(time_str=date).do(time_print, time_str=date)
    if datetime.datetime.today().weekday() == 2:
        for date in timelist_end:
            aioschedule.every().wednesday.at(time_str=date).do(time_print, time_str=date)
    if datetime.datetime.today().weekday() == 3:
        for date in timelist_end:
            aioschedule.every().thursday.at(time_str=date).do(time_print, time_str=date)
    if datetime.datetime.today().weekday() == 4:
        for date in timelist_end:
            aioschedule.every().friday.at(time_str=date).do(time_print, time_str=date)
            print(date)
    #asyncio.create_task(aioschelder_loop()) #comments for debug function
    print('Метка вызова времени'+str(datetime.datetime.today().weekday()) + datetime.datetime.today().strftime('%H:%M'))

async def time_print(time_str):
    print("Время сейчас, "+time_str)
    sql = sl.connect('DataBase.db')
    cursor = sql.cursor()
    users = sql.execute("SELECT id FROM USER WHERE notifications='True'").fetchall()
    clas = sql.execute("SELECT class FROM USER WHERE notifications='True'").fetchall()
    for i in range(len(users)):
        print(str(users[i][0])+ " айди")
        print(clas[i][0]+ " класс")
        print(str(datetime.datetime.today().weekday())+ " День недели")
        print(str(klass.get(clas[i][0]))+ " класс но цыфра")#number klass in base
        with open('rasp.txt', mode="r+", encoding="utf-8") as file:
            textlist = file.read().split("===")
            print(textlist[(klass.get(clas[i][0]))])#list all schedule
            usertextlist = textlist[(klass.get(clas[i][0]))]
            #print((str(usertextlist).split("\n")[datetime.datetime.today().weekday()+4]).split(","))#+4 for normal work
        schedulelist_str = (str(usertextlist).split("\n")[datetime.datetime.today().weekday()+2]).split(",")
        await bot.send_message(users[i][0], "<u>" + str(schedulelist_str[timelist_end.index(time_str)])+"</u>\n"+ str(secrets.choice(friendlylist)) +"<u>" + str(timelist_end[timelist_end.index(time_str)])+ "</u>", parse_mode="HTML")
# async def scheduler():
#     while True:
#         for timecicle in timelist_manday:
#             print(timecicle)
#             aioschedule.every().day.at(timecicle).do(time_print,timecicle)
#         print("Воу")
#         await aioschedule.run_pending()
#         await asyncio.sleep(2)
#
# async def on_startup(_):
#     asyncio.create_task(scheduler())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)