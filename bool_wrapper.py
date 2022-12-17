import re
import os
import xlsxwriter
from math import log2
from itertools import product, groupby

from tkinter import messagebox

import config

ALL_OPERATORS = "!~/^&*|+"


def strip_bad_symbols(text: str) -> str:
    result = re.sub(rf"[^a-z{ALL_OPERATORS})(]", "", text)
    return result


class BoolWrapper:
    def __init__(self, input_string: str, language="en"):
        self.language = language
        self.input_string = input_string

        self.boolean_expression = ""
        self.boolean_variables = []
        self.converted_boolean_expression = []
        self.truth_table = {}
        self.kmap = []
        self.groups = []

        self.number_of_variables = 0
        self.rows = 0
        self.cols = 0

        self._workbook = None

        # NOT > XOR > AND > OR
        self.priorities = {
            '!': 3, '~': 3, '/': 3,  # NOT
            '^': 2,  # XOR
            '&': 1, '*': 1,  # AND
            '|': 0, '+': 0,  # OR
            '(': -1  # Чтобы не крашилось при анализе
        }
        self.operators = {
            'not': '!~/',
            'xor': '^',
            'and': '&*',
            'or': '|+',
            'all': ALL_OPERATORS
        }

    def analise_input(self) -> bool:
        self.input_string = ' ' + self.input_string + ' '
        self.input_string = self.input_string.replace(" or ", " | ").replace(" and ", " & ").replace(" xor ",
                                                                                                     " ^ ").replace(
            " not ", " / ")

        # Удаляем все плохие символы и смотрим, изменилась ли строка
        self.boolean_expression = strip_bad_symbols(self.input_string.lower())
        if len(self.boolean_expression) != len(self.input_string.replace(' ', '')):
            messagebox.showerror(config.controls_names["error"]["title"][self.language],
                                 config.controls_names["error"]["error2"][self.language])
            return False

        # Смотрим, были ли в строке хоть какие-то операторы
        if len(self.boolean_expression) == len(re.sub(r"[^a-z)(]", "", self.boolean_expression)):
            messagebox.showerror(config.controls_names["error"]["title"][self.language],
                                 config.controls_names["error"]["error2"][self.language])
            return False

        # Смотрим, были ли в строке хоть какие-то переменные
        if len(self.boolean_expression) == len(re.sub(rf"[^{ALL_OPERATORS})(]", "", self.boolean_expression)):
            messagebox.showerror(config.controls_names["error"]["title"][self.language],
                                 config.controls_names["error"]["error2"][self.language])
            return False

        # Проверяем порядок скобок, если они есть
        stack = []
        for symbol in self.boolean_expression:
            if symbol == '(':
                stack.append(symbol)
            elif symbol == ')':
                if len(stack) == 0:
                    messagebox.showerror(config.controls_names["error"]["title"][self.language],
                                         config.controls_names["error"]["error3"][self.language])
                    return False
                stack.pop()
        if len(stack) > 0:
            messagebox.showerror(config.controls_names["error"]["title"][self.language],
                                 config.controls_names["error"]["error3"][self.language])
            return False

        # Пытаемся распарсить строку в обратную польскую запись
        return self.parse_to_reverse_polish_notation()

    def parse_to_reverse_polish_notation(self) -> bool:
        stack = []
        variable_name = ""

        # Проходимся по всеё строке
        error_output_string = ""
        prev_symbol = ""
        for symbol in self.boolean_expression:
            # Если это буква, то составляем имя переменной
            if symbol.isalpha():
                variable_name += symbol
            else:
                error_output_string += f'{variable_name} {symbol}'
                # Добавляем переменную из variable_name в выходную строку
                if len(variable_name):
                    if symbol in self.operators['not'] or symbol == '(':
                        messagebox.showerror(config.controls_names["error"]["title"][self.language],
                                             f'{config.controls_names["error"]["error4"][self.language]} {symbol}!\n'
                                             f'[{error_output_string}].')
                        return False

                    if variable_name not in self.boolean_variables:
                        self.boolean_variables.append(variable_name)
                    self.converted_boolean_expression.append(variable_name)
                    variable_name = ""

                else:
                    # Если до встречи опреатора не было переменной
                    if symbol in self.operators['xor'] or symbol in self.operators['and'] or \
                            symbol in self.operators['or'] or symbol == ')':
                        if prev_symbol != ')':
                            messagebox.showerror(config.controls_names["error"]["title"][self.language],
                                                 f'{config.controls_names["error"]["error5"][self.language]} {symbol}!\n'
                                                 f'[{error_output_string}].')
                            return False
                    if symbol in self.operators['not']:
                        if prev_symbol == ')':
                            messagebox.showerror(config.controls_names["error"]["title"][self.language],
                                                 f'{config.controls_names["error"]["error4"][self.language]} {symbol}!\n'
                                                 f'[{error_output_string}].')
                            return False

                if symbol == '(':
                    stack.append(symbol)
                elif symbol == ')':
                    # Если ), то выводим все операторы до )
                    current_operator = stack[-1]
                    while current_operator != '(':
                        self.converted_boolean_expression.append(current_operator)
                        stack.pop()
                        current_operator = stack[-1]
                    stack.pop()
                else:
                    # Иначе это символ оператора
                    # Если стек пустой, то просто добавляем
                    if len(stack) == 0:
                        stack.append(symbol)
                    else:
                        # Если в стеке уже что-то есть, то сравниваем приоритеты и выводим из стека всё, что больше
                        while self.priorities[symbol] < self.priorities[stack[-1]]:
                            self.converted_boolean_expression.append(stack.pop())

                            if len(stack) == 0:
                                break
                        stack.append(symbol)
            prev_symbol = symbol

        # Если последний символ был оператором, и после него не было никакой переменной, то выдаем ошибку
        if self.boolean_expression[-1] in self.operators['all']:
            messagebox.showerror(config.controls_names["error"]["title"][self.language],
                                 f'{config.controls_names["error"]["error6"][self.language]} {stack[-1]}!\n'
                                 f'[{error_output_string}].')
            return False

        # Добавляем последнюю переменную и все оставшиеся операторы
        if len(variable_name):
            if self.boolean_expression[len(self.boolean_expression) - len(variable_name) - 1] == ')':
                messagebox.showerror(config.controls_names["error"]["title"][self.language],
                                     f'{config.controls_names["error"]["error7"][self.language]} [{variable_name}]!\n'
                                     f'[{error_output_string}].')
                return False

            if variable_name not in self.boolean_variables:
                self.boolean_variables.append(variable_name)
            self.converted_boolean_expression.append(variable_name)

        while len(stack):
            self.converted_boolean_expression.append(stack.pop())

        self.boolean_variables.sort()
        # print(self.boolean_expression)
        # print(self.converted_boolean_expression)
        # print(self.boolean_variables)
        return True

    def create_truth_table(self):
        stack = []
        number_of_variables = len(self.boolean_variables)

        variables_truth_table_values = list(product([False, True], repeat=number_of_variables))

        # Заполняем таблицу для переменных
        for i in range(number_of_variables):
            variable_values = []
            for j in range(pow(2, number_of_variables)):
                variable_values.append(variables_truth_table_values[j][i])
            self.truth_table.update({self.boolean_variables[i]: variable_values})

        # Заполняем таблицу для результатов операций
        for lexeme in self.converted_boolean_expression:
            # Если это переменная
            if lexeme not in self.operators['all']:
                stack.append(lexeme)
            else:
                if lexeme in self.operators['not']:
                    variable = stack.pop()
                    variable_values = []

                    for i in range(pow(2, number_of_variables)):
                        variable_values.append(not self.truth_table[variable][i])
                    stack.append(f'{lexeme}({variable})')
                    self.truth_table.update({f'{lexeme}({variable})': variable_values})

                else:
                    variable1 = stack.pop()
                    variable2 = stack.pop()
                    variable_values = []

                    if lexeme in self.operators['xor']:
                        for i in range(pow(2, number_of_variables)):
                            variable_values.append(self.truth_table[variable1][i] ^ self.truth_table[variable2][i])
                    elif lexeme in self.operators['and']:
                        for i in range(pow(2, number_of_variables)):
                            variable_values.append(self.truth_table[variable1][i] and self.truth_table[variable2][i])
                    elif lexeme in self.operators['or']:
                        for i in range(pow(2, number_of_variables)):
                            variable_values.append(self.truth_table[variable1][i] or self.truth_table[variable2][i])
                    stack.append(f'{variable2} {lexeme} {variable1}')
                    self.truth_table.update({f'{variable2} {lexeme} {variable1}': variable_values})

    def write_truth_table_to_excel(self, is_true_false_mode: bool = False, _dont_close: bool = False) -> bool:
        filename = f'{config.paths["file"]}'
        try:
            os.makedirs(config.paths["output"], exist_ok=True)

            self._workbook = xlsxwriter.Workbook(filename=filename)
            worksheet = self._workbook.add_worksheet('TruthTable')
            cell_format = self._workbook.add_format({'italic': True, 'bold': True, 'align': 'center'})

            row = col = 0
            current_column = 0
            for variable, values in self.truth_table.items():
                worksheet.write(row, col, variable, cell_format)
                # Устанавливаем для текущего столбца нужную ширину
                worksheet.set_column(current_column, current_column, len(variable) + 2)
                for i in range(len(values)):
                    row += 1
                    if is_true_false_mode:
                        worksheet.write(row, col, values[i])
                    else:
                        worksheet.write(row, col, 1 if values[i] is True else 0)
                row = 0
                col += 1
                current_column += 1
            if not _dont_close:
                self._workbook.close()
                self._workbook = None
        except IOError:
            messagebox.showerror(config.controls_names["error"]["title"][self.language],
                                 f'{config.controls_names["error"]["error8"][self.language]} [{filename}].\n'
                                 f'{config.controls_names["error"]["error9"][self.language]}')
            return False
        return True

    def create_kmap(self, is_sop: bool = True, is_math: bool = True) -> bool:
        self.number_of_variables = len(self.boolean_variables)
        if self.number_of_variables > 4 or self.number_of_variables < 2:
            return False

        value = 0 if is_sop else 1
        self.kmap = [value] * pow(2, self.number_of_variables)
        value = 1 if is_sop else 0
        truth_table_result_values = list(self.truth_table.values())[-1]
        # if number_of_variables == 2
        self.rows = 2
        self.cols = 2

        if self.number_of_variables == 3:
            self.rows = 4
            self.cols = 2
        elif self.number_of_variables == 4:
            self.rows = 4
            self.cols = 4

        # Перезаписываем значения для активных выходов результата таблицы истинности
        for i in range(self.rows):
            # Переводим в код Грея
            gray_i = i ^ (i >> 1)
            for j in range(self.cols):
                gray_j = j ^ (j >> 1)
                self.kmap[gray_i * self.cols + gray_j] = 0 if truth_table_result_values[
                                                                  i * self.cols + j] is False else 1

        # Функции для дальнейшей работы

        def _at(_i: int, _j: int) -> int:
            """
            Получаем значение по конкретным индексам
            :param _i: строка
            :param _j: столбец
            :return: значение по данным индексам
            """
            if 0 <= _i < self.rows and 0 <= _j < self.cols:
                return self.kmap[_i * self.cols + _j]
            _i = (_i + self.rows) % self.rows
            _j = (_j + self.cols) % self.cols
            return self.kmap[_i * self.cols + _j]

        def _at_index(_i: int, _j: int) -> int:
            """
            Получаем номер индекса по конкретным индексам
            :param _i: строка
            :param _j: столбец
            :return: номер индекса по данным индексам
            """
            if 0 <= _i < self.rows and 0 <= _j < self.cols:
                _gray_i = _i ^ (_i >> 1)
                _gray_j = _j ^ (_j >> 1)
                _element = _gray_i * self.cols + _gray_j
                return _element
            _i = (_i + self.rows) % self.rows
            _j = (_j + self.cols) % self.cols
            _gray_i = _i ^ (_i >> 1)
            _gray_j = _j ^ (_j >> 1)
            _element = _gray_i * self.cols + _gray_j
            return _element

        def _find_group(_i: int, _j: int, group_size: int, directions: list, step: int) -> bool:
            was_grouped = False
            is_group = True

            d = 0
            for k in range(4):
                for t in range(group_size - 1):
                    _next = (d + t) % len(directions)
                    _i1 = _i + directions[_next][0]
                    _j1 = _j + directions[_next][1]

                    # TODO check this mean
                    if _at(_i1, _j1) is not value:
                        is_group = False
                        break

                if is_group:
                    was_grouped = True
                    self.groups.append([])
                    _index = _at_index(_i, _j)
                    if _index not in self.groups[-1]:
                        self.groups[-1].append(_index)

                    for t in range(group_size - 1):
                        _next = (d + t) % len(directions)
                        _i1 = _i + directions[_next][0]
                        _j1 = _j + directions[_next][1]

                        _index = _at_index(_i1, _j1)
                        if _index not in self.groups[-1]:
                            self.groups[-1].append(_index)
                is_group = True
                d += step
            return was_grouped

        def _find_group_for_element(_i: int, _j: int):
            was_grouped = False

            # Паттерны поиска
            directions_pairs = [[0, -1], [-1, 0], [0, 1], [1, 0]]
            directions_quads1 = [[0, -1], [-1, -1], [-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1]]
            directions_quads2 = [[0, -1], [0, -2], [0, -3], [-1, 0], [-2, 0], [-3, 0], [0, 1], [0, 2], [0, 3], [1, 0],
                                 [2, 0], [3, 0]]
            directions_octs = [
                [0, -1], [0, -2], [0, -3], [1, 0], [1, -1], [1, -2], [1, -3],  # left
                [-1, 0], [-2, 0], [-3, 0], [0, -1], [-1, -1], [-2, -1], [-3, -1],  # top
                [0, 1], [0, 2], [0, 3], [1, 0], [1, 1], [1, 2], [1, 3],  # right
                [1, 0], [2, 0], [3, 0], [0, -1], [1, -1], [2, -1], [3, -1]  # bottom
            ]

            # Анализируем пары элементов
            was_grouped = _find_group(_i, _j, 2, directions_pairs, 1)

            # Анализируем четверки элементов
            result = _find_group(_i, _j, 4, directions_quads1, 2)
            was_grouped = True if result is True else False

            result = _find_group(_i, _j, 4, directions_quads2, 3)
            was_grouped = True if result is True else False

            # Анализируем восьмерки элементов
            result = _find_group(_i, _j, 8, directions_octs, 7)
            was_grouped = True if result is True else False

            if not was_grouped:
                self.groups.append([_at_index(_i, _j)])

        def _delete_duplicates():
            for k in range(len(self.groups)):
                self.groups[k].sort()
            self.groups.sort()
            self.groups = list(group for group, _ in groupby(self.groups))
            self.groups.sort(key=len)

        def _optimize():
            values_without_current = []
            removed_groups = []

            for group1 in self.groups:
                for group2 in self.groups:
                    if group1 == group2:
                        continue
                    elif group2 in removed_groups:
                        continue

                    values_without_current.extend(group2)
                values_without_current.sort()
                values_without_current = list(set(values_without_current))

                count = 0
                for k in range(len(group1)):
                    if group1[k] in values_without_current:
                        count += 1

                if count == len(group1):
                    removed_groups.append(group1)
                values_without_current = []
            self.groups = list(group for group in self.groups if group not in removed_groups)

        for _i in range(self.rows):
            for _j in range(self.cols):
                if _at(_i, _j) == value:
                    _find_group_for_element(_i, _j)
        _delete_duplicates()
        _optimize()

        return True

    def _build_word(self, is_sop: bool, is_math: bool, bits: int, word_sop: str, word_pos: str, compare) -> tuple:
        logical_operators = [" v ", " ^ ", "/"]
        math_operators = [" + ", " ", "!"]

        if not is_sop:
            if len(word_pos) > 0:
                word_pos = (math_operators[0] if is_math is True else logical_operators[0]) + word_pos

            word_pos = self.boolean_variables[bits - 1].upper() + word_pos
            word_pos = ((math_operators[2] if is_math is True else logical_operators[2]) + word_pos) \
                if compare else word_pos
        else:
            if len(word_sop) > 0:
                word_sop = (math_operators[1] if is_math is True else logical_operators[1]) + word_sop

            word_sop = self.boolean_variables[bits - 1].upper() + word_sop
            word_sop = word_sop if compare else \
                ((math_operators[2] if is_math is True else logical_operators[2]) + word_sop)
        return word_sop, word_pos

    def get_sop_or_pos_expression(self, is_sop: bool, is_math: bool) -> str:
        truth_table_result_values = list(self.truth_table.values())[-1]

        logical_operators = [" v ", " ^ ", "/"]
        math_operators = [" + ", " ", "!"]
        first_print = True
        output = ""

        count = 0
        for _value in truth_table_result_values:
            if (is_sop and _value == 0) or (not is_sop and _value == 1):
                count += 1
                continue

            bits = self.number_of_variables
            current_bit = count
            word_sop = ""
            word_pos = ""

            if not first_print:
                if not is_sop:
                    output += math_operators[1] if is_math is True else logical_operators[1]
                else:
                    output += math_operators[0] if is_math is True else logical_operators[0]

            while bits:
                word_sop, word_pos = self._build_word(is_sop, is_math, bits, word_sop, word_pos, current_bit & 1)
                current_bit >>= 1
                bits -= 1
            output += word_sop if is_sop else f"({word_pos})"
            first_print = False
            count += 1
        return output

    def get_minimize_expression(self, is_sop: bool, is_math: bool) -> str:
        logical_operators = [" v ", " ^ ", "/"]
        math_operators = [" + ", " ", "!"]
        first_print = True
        output = ""

        for group in self.groups:
            if not first_print:
                if not is_sop:
                    output += math_operators[1] if is_math is True else logical_operators[1]
                else:
                    output += math_operators[0] if is_math is True else logical_operators[0]

            word_sop = ""
            word_pos = ""

            if len(group) == 1:
                bits = self.number_of_variables
                _value = group[0]

                while bits:
                    word_sop, word_pos = self._build_word(is_sop, is_math, bits, word_sop, word_pos, _value & 1)
                    _value >>= 1
                    bits -= 1
                output += word_sop if is_sop else f"({word_pos})"
            else:
                bits = self.number_of_variables

                while bits:
                    buf = (group[0] >> (self.number_of_variables - bits)) & 1
                    is_bit_up = True if buf else False
                    save_bit = True

                    for _value in group:
                        if ((_value >> (self.number_of_variables - bits)) & 1) != buf:
                            save_bit = False
                            break

                    if save_bit:
                        word_sop, word_pos = self._build_word(is_sop, is_math, bits, word_sop, word_pos, is_bit_up)
                    bits -= 1
                output += word_sop if is_sop else f"({word_pos})"
            first_print = False
        return output

    def write_kmap_to_excel(self, is_math: bool) -> bool:
        filename = f'{config.paths["file"]}'
        try:
            os.makedirs(config.paths["output"], exist_ok=True)

            if self._workbook is None:
                self._workbook = xlsxwriter.Workbook(filename=filename)
            worksheet = self._workbook.add_worksheet('Kmap')
            cell_format = self._workbook.add_format({'italic': True, 'bold': True, 'align': 'center'})

            row = col = current_column = 0

            # Выводим к-карту со значениями
            variables_in_row = int(log2(self.rows))
            variables_in_col = int(log2(self.cols))

            logical_operators = [" /"]
            math_operators = [" !"]

            row_headers = []
            column_headers = []

            # Заполняем заголовки колонок
            for i in range(self.cols):
                gray_col = i ^ (i >> 1)
                column_header = ""
                for j in range(variables_in_col):
                    column_header += "  " if ((gray_col >> (variables_in_col - 1 - j)) & 1) else \
                        math_operators[0] if is_math is True else logical_operators[0]
                    column_header += self.boolean_variables[variables_in_row + j]
                column_headers.append(column_header)

            # Заполняем заголовки строк
            for i in range(self.rows):
                gray_row = i ^ (i >> 1)
                row_header = ""
                for j in range(variables_in_row):
                    row_header += "  " if ((gray_row >> (variables_in_row - 1 - j)) & 1) else \
                        math_operators[0] if is_math is True else logical_operators[0]
                    row_header += self.boolean_variables[j]
                row_headers.append(row_header)

            row_headers_length = len(max(row_headers, key=len))
            row_headers_length = row_headers_length if row_headers_length >= len("K-map") else len("K-map")

            worksheet.write(row, col, "K-map", cell_format)
            # Устанавливаем для текущего столбца нужную ширину
            worksheet.set_column(current_column, current_column, row_headers_length + 2)
            row += 2

            # Записываем все заголовки строк
            for i in range(self.rows):
                worksheet.write(row, col, row_headers[i], cell_format)
                row += 1

            row = 1
            col = 1
            current_column = 1
            # Записываем данные и заголовски столбцов
            for i in range(self.cols):
                # Заголовок столбца
                worksheet.write(row, col, column_headers[i], cell_format)
                worksheet.set_column(current_column, current_column, len(column_headers[i]) + 2)
                row += 1

                # Данные
                for j in range(self.rows):
                    worksheet.write(row, col, self.kmap[j * self.cols + i])
                    row += 1
                row = 1
                col += 1
                current_column += 1

            shift_row = 4
            row = self.rows + shift_row
            col = 0
            current_column = 0
            # Выводим к-карту с индексами
            worksheet.write(row, col, "K-map indexes", cell_format)
            row_headers_length = row_headers_length if row_headers_length >= len("K-map indexes") else len(
                "K-map indexes")
            # Устанавливаем для текущего столбца нужную ширину
            worksheet.set_column(current_column, current_column, row_headers_length + 2)
            row += 2

            # Записываем все заголовки строк
            for i in range(self.rows):
                worksheet.write(row, col, row_headers[i], cell_format)
                row += 1

            row = self.rows + shift_row + 1
            col = 1
            current_column = 1
            # Записываем данные и заголовски столбцов
            for i in range(self.cols):
                # Заголовок столбца
                worksheet.write(row, col, column_headers[i], cell_format)
                worksheet.set_column(current_column, current_column, len(column_headers[i]) + 2)
                row += 1
                gray_col = i ^ (i >> 1)

                # Данные
                for j in range(self.rows):
                    gray_row = j ^ (j >> 1)
                    worksheet.write(row, col, gray_row * self.cols + gray_col)
                    row += 1
                row = self.rows + shift_row + 1
                col += 1
                current_column += 1

            shift_col = 4
            row = 0
            col = self.cols + shift_col
            current_column = col
            worksheet.write(row, col, "Groups", cell_format)
            row += 1
            # Выводим группы
            worksheet.set_column(current_column, current_column, len("Octant") + 2)
            for group in self.groups:
                if len(group) == 1:
                    worksheet.write(row, col, "Union", cell_format)
                elif len(group) == 2:
                    worksheet.write(row, col, "Pair", cell_format)
                elif len(group) == 4:
                    worksheet.write(row, col, "Quad", cell_format)
                elif len(group) == 8:
                    worksheet.write(row, col, "Octant", cell_format)

                col += 1
                current_column += 1

                for j in range(len(group)):
                    worksheet.write(row, col, group[j])
                    worksheet.set_column(current_column, current_column, len(str(group[j])) + 2)
                    col += 1
                    current_column += 1

                row += 1
                col = self.cols + shift_col
                current_column = col

            self._workbook.close()
            self._workbook = None
        except IOError:
            messagebox.showerror(config.controls_names["error"]["title"][self.language],
                                 f'{config.controls_names["error"]["error8"][self.language]} [{filename}].\n'
                                 f'{config.controls_names["error"]["error9"][self.language]}')
            return False
        return True
