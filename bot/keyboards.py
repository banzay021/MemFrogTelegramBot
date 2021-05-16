from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

##########################
#     MAIN menu          #
##########################

button_settings = KeyboardButton('/🛠_settings')
button_metrics = KeyboardButton('/📊_metrics')
button_add_mems = KeyboardButton('/🐸_add_mems')

button_home = KeyboardButton('/🏘_home')
inline_button_home = InlineKeyboardButton('🏘_home', callback_data='/🏘_home')

kb_main_menu = ReplyKeyboardMarkup().add(
    button_settings).add(button_metrics).add(button_add_mems).add(button_home)

##########################
#     Settings menu      #
##########################

button_frequency = KeyboardButton('/🛠_frequency')
button_sleep_time = KeyboardButton('/🛠_sleep_time')
button_mem_test = KeyboardButton('/🛠_mem_test')

kb_settings_menu = ReplyKeyboardMarkup().add(
    button_frequency).add(button_sleep_time).add(button_mem_test).add(button_home)

kb_settings_menu_frequency = InlineKeyboardMarkup(row_width=3)

inline_button_frequency_1 = InlineKeyboardButton('2 min', callback_data='frequency 2')
inline_button_frequency_2 = InlineKeyboardButton('5 min', callback_data='frequency 5')
inline_button_frequency_3 = InlineKeyboardButton('15 min', callback_data='frequency 15')
inline_button_frequency_4 = InlineKeyboardButton('20 min', callback_data='frequency 20')
inline_button_frequency_5 = InlineKeyboardButton('30 min', callback_data='frequency 30')
inline_button_frequency_6 = InlineKeyboardButton('0 min', callback_data='frequency 0')

kb_settings_menu_frequency.add(inline_button_frequency_1, inline_button_frequency_2, inline_button_frequency_3)
kb_settings_menu_frequency.add(inline_button_frequency_4, inline_button_frequency_5, inline_button_frequency_6)

##########################
#     Metrics  menu      #
##########################

button_metrics_like_stats = KeyboardButton('/📊_like_stats')

kb_metrics_menu = ReplyKeyboardMarkup().add(button_metrics_like_stats).add(button_home)

##########################
#     MEM add  menu      #
##########################

kb_add_mems = ReplyKeyboardMarkup().add(button_home)


inline_btn_1 = InlineKeyboardButton('Первая кнопка!', callback_data='button1')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)

inline_kb_full = InlineKeyboardMarkup(row_width=2).add(inline_btn_1)
inline_kb_full.add(InlineKeyboardButton('Вторая кнопка', callback_data='btn2'))
inline_btn_3 = InlineKeyboardButton('кнопка 3', callback_data='btn3')
inline_btn_4 = InlineKeyboardButton('кнопка 4', callback_data='btn4')
inline_btn_5 = InlineKeyboardButton('кнопка 5', callback_data='btn5')
inline_kb_full.add(inline_btn_3, inline_btn_4, inline_btn_5)
inline_kb_full.row(inline_btn_3, inline_btn_4, inline_btn_5)
inline_kb_full.insert(InlineKeyboardButton("query=''", switch_inline_query=''))
inline_kb_full.insert(InlineKeyboardButton("query='qwerty'", switch_inline_query='qwerty'))
inline_kb_full.insert(InlineKeyboardButton("Inline в этом же чате", switch_inline_query_current_chat='wasd'))
inline_kb_full.add(InlineKeyboardButton('Уроки aiogram', url='https://surik00.gitbooks.io/aiogram-lessons/content/'))

##########################
#     Inline edit before send       #
##########################

inline_btn_send = InlineKeyboardButton(f'✅', callback_data='edit_ok')
inline_btn_cancel = InlineKeyboardButton(f'❌', callback_data='edit_cancel')
inline_kb_meme_edit = InlineKeyboardMarkup(row_width=2)
inline_kb_meme_edit.row(inline_btn_send, inline_btn_cancel)


##########################
#     Inline likes       #
##########################

count_bad = ''
conut_normal = ''
count_fun = ''
count_lol = ''

inline_btn_bad = InlineKeyboardButton(f'😭{count_bad}', callback_data='quality_bad')
inline_btn_normal = InlineKeyboardButton(f'😒{conut_normal}', callback_data='quality_normal')
inline_btn_fun = InlineKeyboardButton(f'😍{count_fun}', callback_data='quality_fun')
inline_btn_lol = InlineKeyboardButton(f'🤣{count_lol}', callback_data='quality_lol')
inline_kb_meme_quality = InlineKeyboardMarkup(row_width=4)
inline_kb_meme_quality.row(inline_btn_bad, inline_btn_normal, inline_btn_fun, inline_btn_lol)
