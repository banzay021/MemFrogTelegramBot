import logging

import asyncio

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import link, text
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions, InputMediaAnimation
from aiogram.dispatcher.filters import IsReplyFilter

#from config import TOKEN #TOKEN_TEST as TOKEN
#from config import CHAT_ID #CHAT_ID_TEST as CHAT_ID


from config import TOKEN_TEST as TOKEN
from config import CHAT_ID_TEST as CHAT_ID

from config import ACL
from config import CAT_BIG_EYES
from config import JOIN_LINK


from utils import FrogState
from messages import MESSAGES

import keyboards as kb

import re

metrics_count_bad = 0
metrics_conut_normal = 0
metrics_count_fun = 0
metrics_count_lol = 0

def like_inc(var):
    var+=1

logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG)

admin_only = lambda message: message.from_user.id in ACL

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

dp.middleware.setup(LoggingMiddleware())

queue = asyncio.Queue()


def get_count(btn_text: str) -> int:
    result = re.findall(r'\d+', btn_text)
    if len(result) == 0: result.append('0')
    return int(result[0])


async def like_count(code: str, message: types.message):
    for buttom in message.reply_markup.inline_keyboard[0]:
        if code == buttom.callback_data[8:]:
            b = str(get_count(buttom.text) + 1)
            buttom.text = buttom.text[:1] + str(get_count(buttom.text) + 1)
    await bot.edit_message_reply_markup(message_id=message.message_id,
                                        chat_id=message.chat.id,
                                        reply_markup=message.reply_markup)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('quality'),state='*')
async def process_callback_mem_quality(callback_query: types.CallbackQuery):
    code = callback_query.data[8:]
    if isinstance(code, str):
        code = str(code)
    if code == 'bad':
        await bot.answer_callback_query(callback_query.id, text='Нажата bad кнопка')
        await like_count(code, callback_query.message)
        like_inc(metrics_count_bad)
    if code == 'normal':
        await bot.answer_callback_query(callback_query.id, text='Нажата normal кнопка')
        await like_count(code, callback_query.message)
        like_inc(metrics_conut_normal)
    if code == 'fun':
        await bot.answer_callback_query(callback_query.id, text='Нажата fun кнопка')
        await like_count(code, callback_query.message)
        like_inc(metrics_count_fun)
    if code == 'lol':
        await bot.answer_callback_query(callback_query.id, text='Нажата lol кнопка')
        await like_count(code, callback_query.message)
        like_inc(metrics_count_lol)
    else:
        await bot.answer_callback_query(callback_query.id)
    # await bot.send_message(callback_query.from_user.id, f'Нажата инлайн кнопка! code={code}')


@dp.message_handler(admin_only, commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(MESSAGES['start'], reply_markup=kb.kb_main_menu)


@dp.message_handler(admin_only, commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(MESSAGES['help'])


##########################
#      METRICS           #
##########################

@dp.message_handler(admin_only, commands=['📊_metrics'])
async def process_metrics_menu(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    await state.set_state(FrogState.all()[2])
    await message.reply(MESSAGES['metrics'], reply=False, reply_markup=kb.kb_metrics_menu)


@dp.message_handler(admin_only, state=FrogState.METRIC_MODE, commands=['📊_like_stats'])
async def process_command_metrics_like_stats(message: types.Message):
    await bot.send_message(message.from_user.id, f'📊 Current metrics (From boot reboot)\n 😭: {metrics_count_bad} \n 😒: {metrics_conut_normal} \n 😍: {metrics_count_fun} \n 🤣: {metrics_count_lol}')

##########################
#      SETTINGS          #
##########################

@dp.message_handler(admin_only, commands=['🛠_settings'])
async def process_settings_menu(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    await state.set_state(FrogState.all()[3])
    await message.reply(MESSAGES['settings'], reply=False, reply_markup=kb.kb_settings_menu)


@dp.message_handler(admin_only, state=FrogState.SETTINGS_MODE, commands=['🛠_frequency'])
async def process_command_settings_frequency(message: types.Message):
    await bot.send_message(message.from_user.id, '🛠 Please set mem posting frequency', reply_markup=kb.kb_settings_menu_frequency)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('frequency') and c.message.chat.id in ACL)
async def process_callback_mem_quality(callback_query: types.CallbackQuery):
    code = callback_query.data[9:]
    if isinstance(code, str):
        code = int(code)
        await bot.answer_callback_query(callback_query.id, text=f'Now posting frequency is 1 mem in {code} min')
    else:
        await bot.answer_callback_query(callback_query.id, text=f'ERROR in posting frequency  {code} ')


@dp.message_handler(admin_only, state=FrogState.SETTINGS_MODE, commands=['🛠_sleep_time'])
async def process_command_settings_sleep_time(message: types.Message):
    await bot.send_message(message.from_user.id, '🛠 Please set mem posting sleep time')


@dp.message_handler(admin_only, state=FrogState.SETTINGS_MODE, commands=['🛠_mem_test'])
async def process_command_settings_mem_test():
    await bot.send_photo(chat_id=CHAT_ID, photo=CAT_BIG_EYES,
                         caption=text(link(title="@frog", url=JOIN_LINK)),
                         reply_markup=kb.inline_kb_meme_quality,
                         parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(admin_only, state='*', commands=['🏘_home'])
async def process_setstate_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.reset_state()
    await message.reply(MESSAGES['state_change'], reply=False, reply_markup=kb.kb_main_menu)

##########################
#      add_mems          #
##########################


@dp.message_handler(admin_only, state='*', commands=['🐸_add_mems'])
async def process_setstate_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    await state.set_state(FrogState.all()[1])
    await message.reply(MESSAGES['state_change'], reply=False, reply_markup=kb.kb_add_mems)

# @dp.message_handler(admin_only, state=FrogState.MEM_ADD_MODE, content_types=['photo', 'video', 'animation'])
# async def steal_mem(message: types.Message):
#     if message.media_group_id is not None:
#         if 'photo' in message.content_type:
#             media.append(InputMediaPhoto(message.photo[0].file_id))
#         if 'video' in message.content_type:
#             media.append(InputMediaVideo(message.video[0].file_id))
#         if 'animation' in message.content_type:
#             media.append(InputMediaAnimation(message.animation[0].file_id))
#
#     if
#         await bot.send_media_group(chat_id=CHAT_ID, media=message.media_group_id)
#         await bot.send_message(message.from_user.id, 'Mem stolen successfully 🐸')


@dp.callback_query_handler(admin_only, lambda c: c.data and c.data.startswith('edit'), state=FrogState.MEM_ADD_MODE)
async def process_callback_mem_edit(callback_query: types.CallbackQuery):

    if isinstance(callback_query.data, str):
        if callback_query.data == 'edit_ok':
            await bot.answer_callback_query(callback_query.id, text='Спиздить по тихому')
            content_id = ''
            if callback_query.message.content_type == 'photo':
                await bot.send_photo(chat_id=CHAT_ID, photo=callback_query.message.photo[0].file_id,
                                     caption=callback_query.message.md_text,
                                     reply_markup=kb.inline_kb_meme_quality,
                                     parse_mode=ParseMode.MARKDOWN)
                content_id = callback_query.message.photo[0].file_id
            if callback_query.message.content_type == 'video':
                await bot.send_video(chat_id=CHAT_ID, video=callback_query.message.video.file_id,
                                     caption=callback_query.message.md_text,
                                     reply_markup=kb.inline_kb_meme_quality,
                                     parse_mode=ParseMode.MARKDOWN)
                content_id = callback_query.message.video.file_id
            if callback_query.message.content_type == 'animation':
                await bot.send_animation(chat_id=CHAT_ID, animation=callback_query.message.animation.file_id,
                                         caption=callback_query.message.md_text,
                                         reply_markup=kb.inline_kb_meme_quality,
                                         parse_mode=ParseMode.MARKDOWN)
                content_id = callback_query.message.animation.file_id

            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
            await bot.send_message(callback_query.from_user.id, f'Mem stolen successfully 🐸\n type: {callback_query.message.content_type} \n content_id: {content_id}')
        if callback_query.data == 'edit_cancel':
            await bot.answer_callback_query(callback_query.id, text='Не пиздить мем')
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        else:
            await bot.answer_callback_query(callback_query.id)


@dp.message_handler(IsReplyFilter,admin_only, state=FrogState.MEM_ADD_MODE)
async def steal_animation(message: types.Message):
    if isinstance(message.reply_to_message.content_type, str):
        content_id = ''
        message_text_new = message.text + '\n' + message.reply_to_message.md_text
        if message.reply_to_message.content_type == 'photo':
            await bot.send_photo(chat_id=CHAT_ID, photo=message.reply_to_message.photo[0].file_id,
                                 caption=message_text_new,
                                 reply_markup=kb.inline_kb_meme_quality,
                                 parse_mode=ParseMode.MARKDOWN)
            content_id = message.reply_to_message.photo[0].file_id
        if message.reply_to_message.content_type == 'video':
            await bot.send_video(chat_id=CHAT_ID, video=message.reply_to_message.video.file_id,
                                 caption=message_text_new,
                                 reply_markup=kb.inline_kb_meme_quality,
                                 parse_mode=ParseMode.MARKDOWN)
            content_id = message.reply_to_message.video.file_id
        if message.reply_to_message.content_type == 'animation':
            await bot.send_animation(chat_id=CHAT_ID, animation=message.reply_to_message.animation.file_id,
                                     caption=message_text_new,
                                     reply_markup=kb.inline_kb_meme_quality,
                                     parse_mode=ParseMode.MARKDOWN)
            content_id = message.reply_to_message.animation.file_id

        await bot.delete_message(chat_id=message.reply_to_message.chat.id, message_id=message.reply_to_message.message_id)
        await bot.send_message(message.from_user.id, f'Mem stolen successfully 🐸\n type: {message.reply_to_message.content_type} \n content_id: {content_id}')


@dp.message_handler(admin_only, state=FrogState.MEM_ADD_MODE, content_types=['photo'])
async def steal_photo(message: types.Message):

    await bot.send_photo(message.from_user.id, photo=message.photo[0].file_id,
                         caption=text(link(title="@frog", url=JOIN_LINK)),
                         reply_markup=kb.inline_kb_meme_edit,
                         parse_mode=ParseMode.MARKDOWN)

@dp.message_handler(admin_only, state=FrogState.MEM_ADD_MODE, content_types=['video'])
async def steal_video(message: types.Message):

    await bot.send_video(message.from_user.id, video=message.video.file_id,
                         caption=text(link(title="@frog", url=JOIN_LINK)),
                         reply_markup=kb.inline_kb_meme_edit,
                         parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(admin_only, state=FrogState.MEM_ADD_MODE, content_types=['animation'])
async def steal_animation(message: types.Message):

    await bot.send_animation(message.from_user.id, animation=message.animation.file_id,
                             caption=text(link(title="@frog", url=JOIN_LINK)),
                             reply_markup=kb.inline_kb_meme_edit,
                             parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(admin_only, state=FrogState.MEM_ADD_MODE,content_types=types.ContentTypes.ANY)
async def steal_content(message: types.Message):
    await bot.send_message(message.from_user.id, f"I do not know how to steal this yet 🐸 \n Please contact with toad BO$$ content_type: {message.content_type}")


@dp.message_handler(admin_only)
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


# Закртыие соединения с хранилкой состояний
async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_shutdown=shutdown)