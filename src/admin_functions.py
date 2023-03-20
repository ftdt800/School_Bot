import datetime
import emoji
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from main import dp, bot, weekdays, timelist_start

admin_klass = InlineKeyboardMarkup(row_width=2)
admin_klass.add(InlineKeyboardButton('8A...', callback_data='admin_8A'))
admin_klass.add(InlineKeyboardButton('8В...', callback_data='admin_8V'))
admin_rasp_inline_full = InlineKeyboardMarkup(row_width=3)
admin_back_list = (InlineKeyboardButton(emoji.emojize(":backhand_index_pointing_left:")+"Пред...", callback_data='admin_back_list'))
admin_change_list = (InlineKeyboardButton(emoji.emojize(":pencil:")+ "Изменить...", callback_data='admin_change_list'))
admin_next_list = (InlineKeyboardButton("След..."+emoji.emojize(":backhand_index_pointing_right:"), callback_data='admin_next_list'))
admin_rasp_inline_full.add(admin_back_list, admin_change_list, admin_next_list)
admin_cheking = InlineKeyboardMarkup(row_width=2)
admin_cheking_no = (InlineKeyboardButton("Нет! Изменить..."+emoji.emojize(":no_entry:"), callback_data='admin_cheking_no'))
admin_cheking_yes = (InlineKeyboardButton("Всё верно"+emoji.emojize(":check_mark_button:"), callback_data='admin_cheking_yes'))
admin_cheking.add(admin_cheking_yes, admin_cheking_no)

class Form(StatesGroup):
    name = State()

def admin_menu(ID):
    menu = InlineKeyboardMarkup(row_width=2)
    menu.add(InlineKeyboardButton(text="Принять✅", callback_data=f"#y{str(ID)}"),
             InlineKeyboardButton(text="Отклонить❌", callback_data=f'#n{str(ID)}'))
    return menu
@dp.message_handler(commands=['admin'])#Admin panel
async def admin_panel(message: aiogram.types.Message):
    await bot.send_message(message.from_user.id,'Привет учитель Седьмого Континента!\nЗдесь можно изменять, заменять и удалять уроки, и корректировать расписание при его изменении\nНиже выбери нужный класс\n'+ emoji.emojize(":backhand_index_pointing_down:")+ emoji.emojize(":backhand_index_pointing_down:")+ emoji.emojize(":backhand_index_pointing_down:"), reply_markup=admin_klass)

@dp.callback_query_handler(lambda c: c.data == 'admin_8V')
async def process_callback_button(callback_query: aiogram.types.CallbackQuery):
    await admin_preview_list(callback_query, klass=1)
@dp.callback_query_handler(lambda c: c.data == 'admin_8A')
async def process_callback_button(callback_query: aiogram.types.CallbackQuery):
    await admin_preview_list(callback_query, klass=2)

async def admin_preview_list(callback_query: aiogram.types.CallbackQuery, klass):
    await bot.answer_callback_query(callback_query.id)
    global klass_int
    global schedule_int
    schedule_int = 0
    klass_int = klass
    with open('src/rasp.txt', mode="r+", encoding="utf-8") as file:
        textlist = file.read().split("===")  # transform in massive
        print(textlist[klass_int])
        print(str(str(textlist[klass_int]).split("\n")[datetime.datetime.today().weekday()]).split(","))
        schedulelist = str(str(textlist[klass_int]).split("\n")[schedule_int+4]).split(",")
        Massiv_sum = [list(a) for a in zip(timelist_start, schedulelist)]
        text = '<u>'+'\n<u>'.join('</u> > '.join(l) for l in Massiv_sum)
        await bot.send_message(callback_query.from_user.id, weekdays.get(schedule_int+1)+"\n"+text, parse_mode="HTML", reply_markup=admin_rasp_inline_full)
@dp.callback_query_handler(lambda c: c.data == 'admin_next_list')#next
async def process_callback_button(callback_query: aiogram.types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    global klass_int
    global schedule_int
    if schedule_int < 4:
        schedule_int += 1
    with open('src/rasp.txt', mode="r+", encoding="utf-8") as file:
        textlist = file.read().split("===")  # transform in massive
        print(textlist[klass_int])
        print(str(str(textlist[klass_int]).split("\n")[datetime.datetime.today().weekday()]).split(","))
        schedulelist = str(str(textlist[klass_int]).split("\n")[schedule_int+4]).split(",")
        Massiv_sum = [list(a) for a in zip(timelist_start, schedulelist)]
        text = '<u>'+'\n<u>'.join('</u> > '.join(l) for l in Massiv_sum)
        await callback_query.message.edit_text(weekdays.get(schedule_int+1)+"\n"+text, parse_mode="HTML", reply_markup=admin_rasp_inline_full)
@dp.callback_query_handler(lambda c: c.data == 'admin_back_list')#back
async def process_callback_button(callback_query: aiogram.types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    global klass_int
    global schedule_int
    if schedule_int > 0:
        schedule_int -= 1
    with open('src/rasp.txt', mode="r+", encoding="utf-8") as file:
        textlist = file.read().split("===")  # transform in massive
        print(textlist[klass_int])
        print(str(str(textlist[klass_int]).split("\n")[datetime.datetime.today().weekday()]).split(","))
        schedulelist = str(str(textlist[klass_int]).split("\n")[schedule_int+4]).split(",")
        Massiv_sum = [list(a) for a in zip(timelist_start, schedulelist)]
        text = '<u>'+'\n<u>'.join('</u> > '.join(l) for l in Massiv_sum)
        await callback_query.message.edit_text(weekdays.get(schedule_int+1)+"\n"+text, parse_mode="HTML", reply_markup=admin_rasp_inline_full)

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
async def cancel_handler(message: aiogram.types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Ну ладно, отмена')
@dp.message_handler(state=Form.name)
async def process_name(message: aiogram.types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        print(data['name'] + "лал")
        global DataTextCustom
        DataTextCustom = data['name']
        await message.reply('Сохранено!\nИзменённое расписание на '+weekdays.get(schedule_int+1)+'\n <code>'+ DataTextCustom +'</code>\nВсё верно?',parse_mode="HTML", reply_markup=admin_cheking)
    await state.finish()