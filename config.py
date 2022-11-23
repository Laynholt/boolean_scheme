paths = {
    "output": "output",
    "file": "output/data.xlsx",
    "scheme": "output/scheme.png",
    "font": "stuff/Consolas.ttf"
}

language = {
    "ru": "Русский",
    "en": "English"
}
controls_names = {
    # Main window
    "main": {
        "window_name":  {"ru": "Конструктор схем", "en": "Schema builder"},
        "menu1":        {"ru": "Дополнительно", "en": "Additionally"},
        "menu2":        {"ru": "Помощь", "en": "Help"},
        "submenu1":     {"ru": "Отображать значения в таблице истинности в виде True/False",
                         "en": "Display values in truth table as True/False"},
        "submenu2":     {"ru": "Выбор языка", "en": "Language selection"},
        "submenu3":     {"ru": "Знаки операторов", "en": "Operator signs"},
        "label1":       {"ru": "Введите выражение:", "en": "Enter an expression:"},
        "button1":      {"ru": "Создать схему", "en": "Create scheme"},
        "button2":      {"ru": "Создать таблицу истинности", "en": "Create truth table"},
        "button3":      {"ru": "Упростить выражение", "en": "Simplify Expression"},
    },
    # Operators window
    "operators": {
        "window_name":  {"ru": "Операторы", "en": "Operators"},
    },
    # Scheme window
    "scheme": {
        "window_name":  {"ru": "Схема выражения", "en": "Expression scheme"},
        "check1":       {"ru": "Отображать боксы", "en": "Show boxes"},
        "button1":      {"ru": "Сохранить изображение", "en": "Save image"},
        "button2":      {"ru": "Увеличить", "en": "Increase"},
        "button3":      {"ru": "Уменьшить", "en": "Decrease"},

        # Errors
        "error1":       {"ru": "Не удалось открыть шрифт по пути:", "en": "Failed to open font path:"},
        "error2":       {"ru": "Не удалось сохранить изображение!", "en": "Failed to save image!"},

        # Warnings

        # Info
        "info1":        {"ru": "Изображение успешно сохранено!", "en": "Image saved successfully!"},
    },
    # Simplify Expression window
    "simple": {
        "window_name":  {"ru": "Минимизация выражения", "en": "Expression minimization"},
        "check1":       {"ru": "Дизъюнктивная нормальная форма", "en": "Disjunctive normal form"},
        "check2":       {"ru": "Конъюнктивная нормальная форма", "en": "Conjunctive normal form"},
        "check3":       {"ru": "Использовать математические знаки операторов", "en": "Use Mathematical Operator Signs"},
        "button1":      {"ru": "Минимизировать", "en": "Minimize"},
        "button2":      {"ru": "Копировать полное выражение", "en": "Copy full expression"},
        "button3":      {"ru": "Копировать упрощенное выражение", "en": "Copy simplified expression"},
        "button4":      {"ru": "Записать K-карту в эксель", "en": "Write K-map to excel"},
        "label1":       {"ru": "Оптимальное выражение:", "en": "Optimal expression:"},

        # Errors
        "error1":       {"ru": "В данной реализации поддерживается только количество [2, 3, 4]!\n\nВы ввели",
                         "en": "Only the number of variables [2, 3, 4] is supported in this implementation!\n\nYou have entered"},

        # Warnings

        # Info
        "info1":        {"ru": "Оптимальное выражение было скопировано в буфер обмена!",
                         "en": "The optimal expression has been copied to the clipboard!"},
        "info2":        {"ru": "Полное выражение было скопировано в буфер обмена!",
                         "en": "The full expression has been copied to the clipboard!"},
        "info3":        {"ru": "Информация успешно записана в файл!",
                         "en": "The information has been successfully written to the file!"},
    },

    "error": {
        "title":    {"ru": "Ошибка", "en": "Error"},
        "error1":   {"ru": "Необходимо ввести булевское выражение!", "en": "Boolean expression required!"},
        "error2":   {"ru": "Некорректный ввод булевского выражения!", "en": "Incorrect boolean expression input!"},
        "error3":   {"ru": "Количество ( и ) скобок не совпадает!", "en": "The number ( and ) of parentheses do not match!"},
        "error4":   {"ru": "Ошибка при парсинге выражения!\nОтсутствует бинарный оператор перед",
                     "en": "Error parsing expression!\nMissing binary operator before"},
        "error5":   {"ru": "Ошибка при парсинге выражения!\nОтсутствует переменная перед",
                     "en": "Error parsing expression!\nMissing variable before"},
        "error6":   {"ru": "Ошибка при парсинге выражения!\nОтсутствует переменная после оператора",
                     "en": "Error parsing expression!\nMissing variable after operator"},
        "error7":   {"ru": "Ошибка при парсинге выражения!\nОтсутствует оператор после ) и перед переменной",
                     "en": "Error parsing expression!\nMissing operator after ) and before variable"},
        "error8": {"ru": "Не удалось создать файл", "en": "Failed to create file"},
        "error9": {"ru": "Вероятнее всего он уже открыт.\nЗакройте файл и повторите попытку.",
                   "en": "It is most likely already open.\nClose the file and try again."},

    },

    "info": {
        "title":    {"ru": "Инфо", "en": "Info"},
        "info1":    {"ru": "Таблица истинности успешно создана!", "en": "Truth table created successfully!"},
    }
}
