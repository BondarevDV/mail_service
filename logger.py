#!/usr/bin/env python
# -*- coding: utf-8 -*-


# импортируем модуль

#!/usr/bin/env python
# -*- coding: utf-8 -*-


# импортируем модуль

import logging
from os import path, remove


def init(name_file_log='logger.log'):
    if path.isfile(name_file_log):
        remove(name_file_log)


        # создаём объект с именем модуля
    logger = logging.getLogger(__name__)
    # задаём уровень логгирования
    logger.setLevel(logging.INFO)
    # создаём обрабочтик файла лога
    handler = logging.FileHandler(name_file_log)
    # задаём уровень логгирования
    # форматируем записи
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #formatter = logging.Formatter('%(levelname)s - %(message)s')
    # устанавливаем формат для обработчика
    handler.setFormatter(formatter)
    # добавляем обработчик к логгеру
    logger.addHandler(handler)

    # записываем сообщение
    return logger
