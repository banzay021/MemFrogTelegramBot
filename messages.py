from utils import FrogState


help_message = 'Этот бот позволяте администрировать группу\n' \
               f'Необходимо выбрать одну из опций меню.\n' \
               'Чтобы отправлять фото/видео, нажми "/🐸_add_mems"\n' \
               'Чтобы сбросить текущее состояние, отправь "/🏘_home"'

start_message = 'Привет! Это тестовый вариант работы ЖаБота .\n' + help_message
invalid_key_message = 'Ключ "{key}" не подходит.\n' + help_message
state_change_success_message = 'Текущее состояние успешно изменено'
state_reset_message = 'Состояние успешно сброшено'
current_state_message = 'Текущее состояние - "{current_state}", что удовлетворяет условию "один из {states}"'
mode_error = 'Необходимо передвавать номер мода как аргумент к команде'

MESSAGES = {
    'start': start_message,
    'help': help_message,
    'invalid_key': invalid_key_message,
    'state_change': state_change_success_message,
    'state_reset': state_reset_message,
    'current_state': current_state_message,
    'mode_error': mode_error,
}