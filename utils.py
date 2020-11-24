from aiogram.utils.helper import Helper, HelperMode, ListItem


class FrogState(Helper):
    mode = HelperMode.snake_case

    SETTINGS_MODE = ListItem()
    METRIC_MODE = ListItem()
    MEM_ADD_MODE = ListItem()
    MAIN_MENU_MOD = ListItem()


if __name__ == '__main__':
    print(FrogState.all())