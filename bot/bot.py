import logging

import asyncio
import signal
from time import sleep

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.markdown import link, text
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions, InputMediaAnimation
from aiogram.dispatcher.filters import IsReplyFilter, RegexpCommandsFilter, Regexp
from aiogram.utils.exceptions import MessageToDeleteNotFound
from MyFIlter import AclAdminFilter
from aiogram.contrib.fsm_storage.redis import RedisStorage2


from config import TOKEN
from config import CHAT_ID
from config import REDIS_HOST

# from config import TOKEN_TEST as TOKEN
# from config import CHAT_ID_TEST as CHAT_ID
# from config import REDIS_HOST_TEST as REDIS_HOST

from config import CAT_BIG_EYES
from config import JOIN_LINK
from config import JOIN_TEXT
from config import REDIS_PASS

from utils import FrogState
from messages import MESSAGES

import keyboards as kb

import re
import aioredis
import json

import FrogWorker as frog_worker


logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                        level=logging.DEBUG)

##############################
#          BOT INIT          #
##############################

like_dict = {'bad': 0, 'normal': 1, 'fun': 2, 'lol': 3}

bot = Bot(token=TOKEN)
storage = RedisStorage2(REDIS_HOST, 6379, db=1, password=REDIS_PASS)
loop = frog_worker.loop

dp = Dispatcher(bot, storage=storage, loop=loop)

# for logging
dp.middleware.setup(LoggingMiddleware())

##############################
#    ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ #
##############################


def get_count(btn_text: str) -> int:
    result = re.findall(r'\d+', btn_text)
    if len(result) == 0: result.append('0')
    return int(result[0])


async def like_setter(redis: aioredis.commands.Redis, likes_list: list):
    for item in like_dict.keys():
        await redis.set(item, str(likes_list[like_dict.get(item)]))


async def like_getter(redis: aioredis.commands.Redis):
    likes_list = [0] * 4
    for item in like_dict.keys():
        if await redis.get(item):
            likes_list[like_dict.get(item)] = int(await redis.get(item))
        else:
            return False
    return likes_list


async def like_to_redis(redis: aioredis.commands.Redis, code: str):
    if not await like_getter(redis):
        likes_list = [0] * 4
        likes_list[like_dict.get(code)] += 1
        await like_setter(redis, likes_list)
    else:
        likes_list = await like_getter(redis)
        likes_list[like_dict.get(code)] += 1
        await like_setter(redis, likes_list)


async def like_count(code: str, message: types.message,reaction_history=None):
    for buttom in message.reply_markup.inline_keyboard[0]:
        if reaction_history:
            if reaction_history == buttom.callback_data[8:]:
                buttom.text = buttom.text[:1] + str(get_count(buttom.text) - 1)
        if code == buttom.callback_data[8:]:
            buttom.text = buttom.text[:1] + str(get_count(buttom.text) + 1)
    await bot.edit_message_reply_markup(message_id=message.message_id,
                                        chat_id=message.chat.id,
                                        reply_markup=message.reply_markup)


@dp.callback_query_handler(Regexp('quality.*'), state='*')
async def process_callback_mem_quality(callback_query: types.CallbackQuery):
    code = callback_query.data[8:]
    redis = await aioredis.create_redis_pool('redis://' + REDIS_HOST, password=REDIS_PASS, db=0)
    #

    # to redis counting
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id
    redis_obj_name = f"{user_id}_{message_id}"

    if isinstance(code, str):
        code = str(code)
        if code in ['bad', 'normal', 'fun', 'lol']:
            await bot.answer_callback_query(callback_query.id, text=f'{code}')
            reaction_history = await redis.get(redis_obj_name)

            if reaction_history:
                reaction_history = reaction_history.decode("utf-8")
                if code != reaction_history:
                    await like_count(code, callback_query.message, reaction_history)
                    await redis.set(redis_obj_name, code)
                elif code == reaction_history:
                    pass
            else:
                await like_count(code, callback_query.message)
                await redis.set(redis_obj_name, code)
        else:
            await bot.answer_callback_query(callback_query.id)
        await like_to_redis(dp.redis, code)

#######################
#   START / HELP      #
#######################


@dp.message_handler(AclAdminFilter, commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(MESSAGES['start'], reply_markup=kb.kb_main_menu)


@dp.message_handler(AclAdminFilter, commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(MESSAGES['help'])

##########################
#      SETTINGS          #
##########################


@dp.message_handler(AclAdminFilter, commands=['🛠_settings'])
async def process_settings_menu(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    await state.set_state(FrogState.all()[3])
    await message.reply(MESSAGES['settings'], reply=False, reply_markup=kb.kb_settings_menu)


@dp.message_handler(AclAdminFilter, state=FrogState.SETTINGS_MODE, commands=['🛠_frequency'])
async def process_command_settings_frequency(message: types.Message):
    await bot.send_message(message.from_user.id, '🛠 Please set mem posting frequency', reply_markup=kb.kb_settings_menu_frequency)


@dp.callback_query_handler(AclAdminFilter, Regexp('frequency.*'), state=FrogState.SETTINGS_MODE)
async def process_callback_mem_quality(callback_query: types.CallbackQuery):
    code = callback_query.data[9:]
    if isinstance(code, str):
        code = int(code)
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await dp.redis.set('frequency', str(code))
        await bot.send_message(callback_query.from_user.id, text=f'Now posting frequency is 1 mem in {code} min')
    else:
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, text=f'ERROR in posting frequency  {code} ')


@dp.message_handler(AclAdminFilter, state=FrogState.SETTINGS_MODE, commands=['🛠_get_frequency'])
async def process_command_settings_sleep_time(message: types.Message):
    frequency = await dp.redis.get('frequency')
    await bot.send_message(message.from_user.id, f'🛠 Current posting frequency: 1 mem per **{frequency.decode("utf-8")}** min', parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(AclAdminFilter, state=FrogState.SETTINGS_MODE, commands=['🛠_sleep_time'])
async def process_command_settings_sleep_time(message: types.Message):
    await bot.send_message(message.from_user.id, '🛠 Please set mem posting sleep time')


@dp.message_handler(AclAdminFilter, state=FrogState.SETTINGS_MODE, commands=['🛠_mem_test'])
async def process_command_settings_mem_test():
    await bot.send_photo(chat_id=CHAT_ID, photo=CAT_BIG_EYES,
                         caption=text(link(title=JOIN_TEXT, url=JOIN_LINK)),
                         reply_markup=kb.inline_kb_meme_quality,
                         parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(AclAdminFilter, state='*', commands=['🏘_home'])
async def process_setstate_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.reset_state()
    await message.reply(MESSAGES['state_change'], reply=False, reply_markup=kb.kb_main_menu)


##########################
#      METRICS           #
##########################

@dp.message_handler(AclAdminFilter, commands=['📊_metrics'])
async def process_metrics_menu(message: types.Message):
    state = dp.current_state(user=message.from_user.id)

    await state.set_state(FrogState.all()[2])
    await message.reply(MESSAGES['metrics'], reply=False, reply_markup=kb.kb_metrics_menu)


@dp.message_handler(AclAdminFilter, state=FrogState.METRIC_MODE, commands=['📊_like_stats'])
async def process_command_metrics_like_stats(message: types.Message):

    likes_list = [0] * 4
    if await like_getter(dp.redis):
        likes_list = await like_getter(dp.redis)

    await bot.send_message(message.from_user.id, f'📊 Current metrics\n 😭: {likes_list[0]} \n 😒: {likes_list[1]} \n 😍: {likes_list[2]} \n 🤣: {likes_list[3]}')

##########################
#      add_mems          #
##########################


@dp.message_handler(AclAdminFilter, state='*', commands=['🐸_add_mems'])
async def process_setstate_command(message: types.Message):
    '''
    Вход в состояние отправки мемов
    :param message:
    :return:
    '''
    state = dp.current_state(user=message.from_user.id)

    await state.set_state(FrogState.all()[1])
    await message.reply(MESSAGES['state_change'], reply=False, reply_markup=kb.kb_add_mems)


@dp.message_handler(AclAdminFilter, state=FrogState.MEM_ADD_MODE, commands=['📤_get_queue_size'])
async def get_queue_size(message: types.Message):
    queue_size = frog_worker.get_queue_size()
    await bot.send_message(message.from_user.id,
                           f'📤🐸 Current queue size: {queue_size}')


@dp.callback_query_handler(AclAdminFilter, Regexp('edit.*'), state=FrogState.MEM_ADD_MODE)
async def process_callback_mem_edit(callback_query: types.CallbackQuery):
    '''
    Обработка инлайн кнопок отправить в канал мем
    Отменить отправку в канал
    :param callback_query:
    :return:
    '''

    if isinstance(callback_query.data, str):
        if callback_query.data == 'edit_ok':
            await bot.answer_callback_query(callback_query.id, text='Мем украден')
            await frog_worker.add_mem_to_posting_queue(callback_query)
            content_id = ''
            if callback_query.message.content_type == 'photo':
                content_id = callback_query.message.photo[0].file_id
            if callback_query.message.content_type == 'video':
                content_id = callback_query.message.video.file_id
            if callback_query.message.content_type == 'animation':
                content_id = callback_query.message.animation.file_id
            await bot.send_message(callback_query.from_user.id, f'Mem add to stolen queue successfully 🐸\n type: {callback_query.message.content_type} \n content_id: {content_id}')
        if callback_query.data == 'edit_cancel':
            await bot.answer_callback_query(callback_query.id, text='Отмена отмена')
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        else:
            await bot.answer_callback_query(callback_query.id)


@dp.message_handler(AclAdminFilter, IsReplyFilter, state=FrogState.MEM_ADD_MODE)
async def steal_with_new_text(message: types.Message):
    '''
    Обработка и отправка меме
    если админ хочет добавить кастомный комментарий к нему
    после первичной отправки и ответа ботом

    нужно ответить реплаем с текстом, который будет добавлен к картинке
    :param message:
    :return:
    '''
    if isinstance(message.reply_to_message.content_type, str):
        message.text = message.text + '\n' + message.reply_to_message.md_text
        await frog_worker.add_mem_to_posting_queue(message)
        content_id = ''
        if message.reply_to_message.content_type == 'photo':
            content_id = message.reply_to_message.photo[0].file_id
        if message.reply_to_message.content_type == 'video':
            content_id = message.reply_to_message.video.file_id
        if message.reply_to_message.content_type == 'animation':
            content_id = message.reply_to_message.animation.file_id
        await bot.send_message(message.from_user.id, f'Mem add to stolen queue successfully 🐸\n type: {message.reply_to_message.content_type} \n content_id: {content_id}')


@dp.message_handler(AclAdminFilter, state=FrogState.MEM_ADD_MODE, content_types=['photo'])
async def steal_photo(message: types.Message):

    await bot.send_photo(message.from_user.id, photo=message.photo[0].file_id,
                         caption=text(link(title=JOIN_TEXT, url=JOIN_LINK)),
                         reply_markup=kb.inline_kb_meme_edit,
                         parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(AclAdminFilter, state=FrogState.MEM_ADD_MODE, content_types=['video'])
async def steal_video(message: types.Message):
    await bot.send_video(message.from_user.id, video=message.video.file_id,
                         caption=text(link(title=JOIN_TEXT, url=JOIN_LINK)),
                         reply_markup=kb.inline_kb_meme_edit,
                         parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(AclAdminFilter, state=FrogState.MEM_ADD_MODE, content_types=['animation'])
async def steal_animation(message: types.Message):

    await bot.send_animation(message.from_user.id, animation=message.animation.file_id,
                             caption=text(link(title=JOIN_TEXT, url=JOIN_LINK)),
                             reply_markup=kb.inline_kb_meme_edit,
                             parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(AclAdminFilter, state=FrogState.MEM_ADD_MODE, content_types=types.ContentTypes.ANY)
async def steal_content(message: types.Message):
    await bot.send_message(message.from_user.id, f"I do not know how to steal this yet 🐸 \n Please contact with toad BO$$ content_type: {message.content_type}")




#####################
#    default answer #
#####################


@dp.message_handler(AclAdminFilter)
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


async def on_startup(dispatcher: Dispatcher):
    dispatcher.redis = await aioredis.create_redis_pool('redis://' + REDIS_HOST, password=REDIS_PASS, db=0)
    print("starting")


async def shutdown(loop, signal=None):
    if signal:
        logging.info(f"Received exit signal {signal.name}")
    tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    logging.info(f"Cancelling {len(tasks)} tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    logging.info(f"Closing database session")
    logging.info("Done.")
    loop.stop()


# Закртыие соединения с хранилкой состояний
async def shutdown_bot(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    await dispatcher.redis.wait_closed()


async def posting():
    while True:
        content_id = ''
        redis = await aioredis.create_redis_pool('redis://' + REDIS_HOST, password=REDIS_PASS, db=0)
        # for first mem to post without sleep
        frequency = 0
        if await redis.get('frequency'):
            frequency = int(await redis.get('frequency')) * 60

        message = await frog_worker.get_mem_to_posting_from_queue()
        await asyncio.sleep(frequency)

        if isinstance(message, types.Message):
            caption = message.text
            message_path_to_obj = message.reply_to_message
        if isinstance(message, types.CallbackQuery):
            caption = message.message.md_text
            message_path_to_obj = message.message
        try:
            await bot.delete_message(chat_id=message_path_to_obj.chat.id, message_id=message_path_to_obj.message_id)
            if message_path_to_obj.content_type == 'photo':
                await bot.send_photo(chat_id=CHAT_ID, photo=message_path_to_obj.photo[0].file_id,
                                     caption=caption,
                                     reply_markup=kb.inline_kb_meme_quality,
                                     parse_mode=ParseMode.MARKDOWN)
                content_id = message_path_to_obj.photo[0].file_id
            if message_path_to_obj.content_type == 'video':
                await bot.send_video(chat_id=CHAT_ID, video=message_path_to_obj.video.file_id,
                                     caption=caption,
                                     reply_markup=kb.inline_kb_meme_quality,
                                     parse_mode=ParseMode.MARKDOWN)
                content_id = message_path_to_obj.video.file_id
            if message_path_to_obj.content_type == 'animation':
                await bot.send_animation(chat_id=CHAT_ID, animation=message_path_to_obj.animation.file_id,
                                         caption=caption,
                                         reply_markup=kb.inline_kb_meme_quality,
                                         parse_mode=ParseMode.MARKDOWN)
                content_id = message_path_to_obj.animation.file_id
            await bot.send_message(message.from_user.id,
                                   f'Mem stolen successfully 🐸\n type: {message_path_to_obj.content_type}\ncontent_id: {content_id}')
        except MessageToDeleteNotFound as exc:
            logging.error('Error ToDelete Message. You posted this meme', exc_info=True)
            await bot.send_message(message.from_user.id,
                                   f'Error ToDelete Message. You posted this meme twice ⚠️🐸⚠️')

        frog_worker.mem_posted()


if __name__ == '__main__':
    sleep(5)
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(loop, signal=s)))
    try:
        dp.loop.create_task(posting())
        executor.start_polling(dp, on_startup=on_startup, on_shutdown=shutdown_bot)

    finally:
        logging.info("Successfully shutdown Bot")
        loop.close()