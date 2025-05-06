from src import settings
from telebot import TeleBot, formatting, types
from src.user_cases import get_free_intervals, get_free_windows

bot = TeleBot(settings.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start_messages(message):
    text = f'Чтобы начать пользоваться ботом нажмите на \
кнопку {formatting.hbold('Меню')} и выберите нужную команду:\n\n\
{formatting.hbold('✏️ Показать окошки')} - бот автоматически разобьёт \
интервалы больше 45 минут на окошки кратные одному часу.\n\n\
{formatting.hbold('⏱️ Показать интервалы')} - бот покажет доступные \
для записи интервалы за месяц выбранной длины.'
    bot.send_message(message.chat.id, text=text, parse_mode='HTML')


@bot.message_handler(commands=['windows'])
def get_windows(message):
    free_windows = get_free_windows()
    masters_windows = []
    for master_id in free_windows:
        master_name = formatting.hbold(free_windows[master_id]['name'])
        all_windows = []
        for working_day in free_windows[master_id]['working_days']:
            date = working_day['date']
            windows = ', '.join(working_day['windows'])
            all_windows.append(f'{date}\n{windows}\n')
        all_windows = formatting.hcode('\n'.join(all_windows)) if all_windows \
            else formatting.hitalic('Нет свободных окошек\n')
        masters_windows.append(f'{master_name}\n\n{all_windows}')
    text = formatting.format_text(*masters_windows, separator="\n")
    if not text:
        text = 'Свободных окошек на ближайшее время нет'
    bot.send_message(message.chat.id, text=text, parse_mode='HTML')


@bot.message_handler(commands=['intervals'])
def intervals_param(message):
    # Создаем клавиатуру и каждую из кнопок
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    param_button_15 = types.InlineKeyboardButton(
        text="15 м", callback_data='15')
    param_button_45 = types.InlineKeyboardButton(
        text="45 м", callback_data='45')
    param_button_90 = types.InlineKeyboardButton(
        text="1 ч 30 м", callback_data='90')
    keyboard.add(param_button_15, param_button_45, param_button_90)
    bot.send_message(
        message.chat.id, "Выберите минимальный интервал", reply_markup=keyboard)


def get_intervals(seance_length, delta):
    free_intervals = get_free_intervals(seance_length, delta)
    masters_intervals = []
    for master_id in free_intervals:
        master_name = formatting.hbold(free_intervals[master_id]['name'])
        all_intervals = []
        for working_day in free_intervals[master_id]['working_days']:
            date = formatting.hitalic(working_day['date'])
            intervals = []
            for interval in working_day['free_intervals']:
                intervals.append(interval['text_interval'])
            intervals = '\n'.join(intervals)
            all_intervals.append(f'{date}\n{intervals}\n')
        all_intervals = '\n'.join(all_intervals) if all_intervals \
            else formatting.hitalic('Нет свободных интервалов\n')
        masters_intervals.append(f'{master_name}\n\n{all_intervals}')
    text = []
    for master_interval in masters_intervals:
        text.append(formatting.format_text(master_interval, separator="\n"))
    if not text:
        text.append('Свободных интервалов на ближайшее время нет')
    return text


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        delta = {"weeks": 0, "months": 1}
        texts = []
        if call.data == "15":
            texts = get_intervals(15*60, delta)
        elif call.data == "45":
            texts = get_intervals(45*60, delta)
        elif call.data == "90":
            texts = get_intervals(90*60, delta)
        bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
        )
        for text in texts:
            bot.send_message(
                call.message.chat.id,
                text=text, parse_mode='HTML',
            )


if __name__ == '__main__':
    bot.infinity_polling()

    # formatting.hbold(message.from_user.first_name), # Жирный
    # formatting.hitalic(message.from_user.first_name), # Наклонный
    # formatting.hunderline(message.from_user.first_name), # Подчёркнутый
    # formatting.hstrikethrough(message.from_user.first_name), # Зачёркнутый
    # formatting.hcode(message.from_user.first_name), # Копировать по нажатию
    # formatting.hcite(message.from_user.first_name), # Цитата
    # formatting.hspoiler(message.from_user.first_name), # Спойлер
