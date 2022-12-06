import tkinter
from tkinter import ttk
from tkinter import messagebox

import os
import pyperclip
from PIL import Image, ImageDraw, ImageFont

import config
from bool_wrapper import BoolWrapper


class App:
    def __init__(self, language="en"):

        if language not in config.language:
            language = "en"

        self.window = tkinter.Tk()
        self.window.title(config.controls_names["main"]["window_name"][language])
        self.window.geometry("480x110")
        self.window.resizable(width=False, height=False)

        self.label_boolean_expression = tkinter.Label(self.window,
                                                      text=config.controls_names["main"]["label1"][language])
        self.label_boolean_expression.grid(column=0, row=0, columnspan=3, padx=15, pady=5)

        self.entry_boolean_expression = ttk.Entry(self.window, width=60)
        self.entry_boolean_expression.grid(column=0, row=1, columnspan=3, padx=15, pady=5)

        self.button_create_scheme = ttk.Button(self.window, text=config.controls_names["main"]["button1"][language],
                                               width=15, command=self._create_scheme)
        self.button_create_scheme.grid(column=0, row=2, padx=10, pady=5)

        self.button_create_table = ttk.Button(self.window, text=config.controls_names["main"]["button2"][language],
                                              width=28, command=self._create_excel_file)
        self.button_create_table.grid(column=1, row=2, padx=10, pady=5)

        self.button_simplify = ttk.Button(self.window, text=config.controls_names["main"]["button3"][language],
                                          width=22, command=self._minimize_expression)
        self.button_simplify.grid(column=2, row=2, padx=10, pady=5)

        self.menu_main = tkinter.Menu(self.window)
        self.window.config(menu=self.menu_main)

        self.menu_additional = tkinter.Menu(self.menu_main, tearoff=0)
        self.is_true_false_values_in_truth_table = tkinter.BooleanVar()
        self.is_true_false_values_in_truth_table.set(False)
        self.menu_additional.add_checkbutton(label=config.controls_names["main"]["submenu1"][language],
                                             onvalue=1, offvalue=0, variable=self.is_true_false_values_in_truth_table)
        self.menu_language = tkinter.Menu(self.menu_additional, tearoff=0)
        self.menu_additional.add_separator()

        lang_keys = list(config.language.keys())
        self.selected_language = tkinter.StringVar()
        self.selected_language.set(language)
        for i in range(len(config.language)):
            self.menu_language.add_radiobutton(label=config.language[lang_keys[i]], value=lang_keys[i],
                                               variable=self.selected_language,
                                               command=self._change_language)
        self.menu_additional.add_cascade(label=config.controls_names["main"]["submenu2"][language],
                                         menu=self.menu_language)

        def _show_operators():
            child = tkinter.Toplevel(self.window)
            child.title(config.controls_names["operators"]["window_name"][self.selected_language.get()])
            child.geometry("280x110")
            child.resizable(width=False, height=False)

            label_operators = ttk.Label(child, text='not = [/, ~, !]\n'
                                                    'xor = [^]\n'
                                                    'and = [&, *]\n'
                                                    'or  = [|, +]')
            label_operators.grid(column=1, row=0, padx=100, pady=20)

        self.menu_help = tkinter.Menu(self.menu_main, tearoff=0)
        self.menu_help.add_command(label=config.controls_names["main"]["submenu3"][language], command=_show_operators)
        self.menu_main.add_cascade(label=config.controls_names["main"]["menu1"][language], menu=self.menu_additional)
        self.menu_main.add_cascade(label=config.controls_names["main"]["menu2"][language], menu=self.menu_help)

    def _change_language(self):
        language = self.selected_language.get()

        self.window.title(config.controls_names["main"]["window_name"][language])

        self.menu_main.entryconfig(1, label=config.controls_names["main"]["menu1"][language])
        self.menu_main.entryconfig(2, label=config.controls_names["main"]["menu2"][language])

        self.menu_additional.entryconfig(0, label=config.controls_names["main"]["submenu1"][language])
        self.menu_additional.entryconfig(2, label=config.controls_names["main"]["submenu2"][language])
        self.menu_help.entryconfig(0, label=config.controls_names["main"]["submenu3"][language])

        self.label_boolean_expression.config(text=config.controls_names["main"]["label1"][language])

        self.button_create_scheme.config(text=config.controls_names["main"]["button1"][language])
        self.button_create_table.config(text=config.controls_names["main"]["button2"][language])
        self.button_simplify.config(text=config.controls_names["main"]["button3"][language])

    def run(self):
        self.window.mainloop()

    def _create_scheme(self):
        language = self.selected_language.get()

        if self.entry_boolean_expression.get() == "":
            messagebox.showerror(config.controls_names["error"]["title"][language],
                                 config.controls_names["error"]["error1"][language])
            return

        wrapper = BoolWrapper(self.entry_boolean_expression.get(), language=language)
        if wrapper.analise_input() is False:
            return

        # Создаем дочернее окно под вывод схемы
        scheme_window = tkinter.Toplevel(self.window)
        scheme_window.title(config.controls_names["scheme"]["window_name"][language])
        scheme_window.geometry("800x500")
        scheme_window.minsize(width=800, height=500)

        # Фрейм для кнопок
        buttons_frame = tkinter.Frame(scheme_window)
        buttons_frame.grid(row=0, column=0, sticky=tkinter.W + tkinter.E)

        # Фрейм для канваса
        canvas_frame = tkinter.Frame(scheme_window, borderwidth=1, relief="sunken", background="white")
        canvas_frame.grid(column=0, row=1, columnspan=3, padx=10, pady=10, sticky=tkinter.NSEW)

        # Делаем динамическое изменение размеров фрейма под размер окна
        scheme_window.columnconfigure(0, weight=1)
        scheme_window.rowconfigure(1, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        scrollbar_vertical = tkinter.Scrollbar(canvas_frame)
        scrollbar_vertical.grid(column=1, row=0, sticky=tkinter.NS)

        scrollbar_horizontal = tkinter.Scrollbar(canvas_frame, orient="horizontal")
        scrollbar_horizontal.grid(column=0, row=1, sticky=tkinter.EW)

        canvas = tkinter.Canvas(canvas_frame, bg=canvas_frame.cget("background"),
                                yscrollcommand=scrollbar_vertical.set,
                                xscrollcommand=scrollbar_horizontal.set,
                                borderwidth=0, highlightthickness=0)
        canvas.grid(column=0, row=0, padx=10, pady=10, sticky=tkinter.NSEW)

        scrollbar_vertical.config(command=canvas.yview)
        scrollbar_horizontal.config(command=canvas.xview)

        scale = 1
        BOX_SIZE = 60
        LINE_SIZE = 150
        LINE_SIZE_LITE = 25
        check_state_boxes = tkinter.BooleanVar()
        check_state_boxes.set(False)

        def _calculate_image_size() -> tuple:
            _width = _height = 0
            stack = []
            _width += (LINE_SIZE * scale)
            for lexeme in wrapper.converted_boolean_expression:
                # Если это переменная
                if lexeme not in wrapper.operators['all']:
                    stack.append(lexeme)
                    _height += (BOX_SIZE * scale)
                else:
                    if lexeme in wrapper.operators['not']:
                        variable = stack.pop()
                        stack.append(f'{lexeme}({variable})')
                        _width += ((BOX_SIZE + LINE_SIZE) * scale)
                    else:
                        variable1 = stack.pop()
                        variable2 = stack.pop()
                        stack.append(f'{variable2} {lexeme} {variable1}')
                        _width += ((LINE_SIZE_LITE + BOX_SIZE + LINE_SIZE) * scale)
            return _width, _height

        # Создаем буферную картинку, на которой будем дублировать отрисовку и которую пользователь сохранит себе
        width, height = _calculate_image_size()
        image = Image.new("RGB", (width + 5, height + 5), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        def _draw_canvas():
            # Рисуем схему
            elements_color = (0, 0, 0)
            background = canvas_frame.cget("background")
            row = 0
            share_bus = 30
            box_size = scale * BOX_SIZE
            line_size = scale * LINE_SIZE
            line_size_lite = scale * LINE_SIZE_LITE
            font_size = 5 + (scale * 5)

            try:
                font = ImageFont.truetype(config.paths['font'], font_size + 5)
            except Exception:
                messagebox.showerror(config.controls_names["error"]["title"][language],
                                     f'{config.controls_names["scheme"]["error1"][language]} [{config.paths["font"]}]')
                font = ImageFont.load_default()

            def _draw_variable(var: str) -> tuple:
                nonlocal row
                if var in wrapper.boolean_variables:
                    if var not in used_variables:
                        if check_state_boxes.get() is True:
                            canvas.create_rectangle(0, row * box_size, box_size, (row + 1) * box_size, outline="#000",
                                                    fill=background, width=2)
                            draw.rectangle([0, row * box_size, box_size, (row + 1) * box_size], outline="#000",
                                           fill=background, width=2)
                        canvas.create_text(box_size / 2, row * box_size + box_size / 3, text=var,
                                           font=f'Consolas {font_size}')
                        draw.text([box_size / 2, row * box_size + box_size / 3 - 10], text=var, fill=elements_color,
                                  font=font)
                        canvas.create_line(0, row * box_size + box_size / 2, box_size + line_size,
                                           row * box_size + box_size / 2, width=2)
                        draw.line([0, row * box_size + box_size / 2, box_size + line_size,
                                   row * box_size + box_size / 2], width=2, fill=elements_color)

                        used_variables.append(var)
                        variables_positions.update({var: {
                            "start": [box_size, row * box_size + box_size / 2],
                            "end": [box_size + line_size, row * box_size + box_size / 2]
                        }})
                        x_end = variables_positions[var]['end'][0]
                        y_end = variables_positions[var]['end'][1]
                    else:
                        _x1 = variables_positions[var]['start'][0] + share_bus
                        _y1 = variables_positions[var]['start'][1]
                        _x2 = _x1
                        _y2 = row * box_size + box_size / 2
                        if check_state_boxes.get() is True:
                            canvas.create_rectangle(0, row * box_size, box_size, (row + 1) * box_size, outline="#000",
                                                    fill=background, width=2)
                            draw.rectangle([0, row * box_size, box_size, (row + 1) * box_size], outline="#000",
                                           fill=background, width=2)
                        canvas.create_line(_x1, _y1, _x2, _y2, width=2)
                        draw.line([_x1, _y1, _x2, _y2], width=2, fill=elements_color)
                        canvas.create_line(_x1, _y2, _x1 + line_size - share_bus, _y2, width=2)
                        draw.line([_x1, _y2, _x1 + line_size - share_bus, _y2], width=2, fill=elements_color)
                        canvas.create_text(_x1 + box_size / 2, row * box_size + box_size / 3, text=var,
                                           font=f'Consolas {font_size}')
                        draw.text([_x1 + box_size / 2, row * box_size + box_size / 3 - 10], text=var,
                                  fill=elements_color, font=font)
                        x_end = _x1 + line_size - share_bus
                        y_end = _y2
                    row += 1
                    return x_end, y_end
                return None, None

            stack = []
            used_variables = []
            variables_positions = {}
            for lexeme in wrapper.converted_boolean_expression:
                # Если это переменная
                if lexeme not in wrapper.operators['all']:
                    stack.append(lexeme)
                else:
                    if lexeme in wrapper.operators['not']:
                        variable = stack.pop()

                        # Рисуем переменную
                        x, y = _draw_variable(variable)

                        # Если это было выражение
                        if x is None:
                            x = variables_positions[variable]['end'][0]
                            y = variables_positions[variable]['end'][1]

                        # Рисуем оператор НЕ
                        circle_size = scale * 8
                        canvas.create_polygon(
                            x, y,
                            x, y - box_size / 2,
                               x + box_size, y,
                               x + box_size + circle_size / 2, y - circle_size / 2,
                               x + box_size + circle_size, y,
                               x + box_size + circle_size / 2, y + circle_size / 2,
                               x + box_size, y,
                            x, y + box_size / 2,
                            x, y
                        )
                        draw.polygon([
                            x, y,
                            x, y - box_size / 2,
                               x + box_size, y,
                               x + box_size + circle_size / 2, y - circle_size / 2,
                               x + box_size + circle_size, y,
                               x + box_size + circle_size / 2, y + circle_size / 2,
                               x + box_size, y,
                            x, y + box_size / 2,
                            x, y
                        ], fill=elements_color)

                        if check_state_boxes.get() is True:
                            # Чекаем размер
                            canvas.create_rectangle(x, y - box_size / 2, x + box_size, y + box_size / 2)
                            draw.rectangle([x, y - box_size / 2, x + box_size, y + box_size / 2], outline="#000",
                                           fill=background, width=2)

                        canvas.create_line(x + box_size + circle_size, y, x + box_size + circle_size + line_size, y,
                                           width=2)
                        draw.line([x + box_size + circle_size, y, x + box_size + circle_size + line_size, y], width=2,
                                  fill=elements_color)
                        variables_positions.update({f'{lexeme}({variable})': {
                            "start": [x + box_size + circle_size, y],
                            "end": [x + box_size + circle_size + line_size, y]
                        }})
                        stack.append(f'{lexeme}({variable})')
                    else:
                        variable1 = stack.pop()
                        variable2 = stack.pop()

                        # Рисуем переменную 1
                        x1, y1 = _draw_variable(variable1)

                        # Если это было выражение
                        if x1 is None:
                            x1 = variables_positions[variable1]['end'][0]
                            y1 = variables_positions[variable1]['end'][1]

                        # Рисуем переменную 2
                        x2, y2 = _draw_variable(variable2)

                        # Если это было выражение
                        if x2 is None:
                            x2 = variables_positions[variable2]['end'][0]
                            y2 = variables_positions[variable2]['end'][1]

                        # Соединяем две переменные
                        # Равняем их по иксу
                        x = x1
                        if x1 != x2:
                            max_x, y = (x1, y2) if x1 > x2 else (x2, y1)
                            min_x, y = (x1, y1) if x1 < x2 else (x2, y2)
                            canvas.create_line(min_x, y, max_x, y, width=2)
                            draw.line([min_x, y, max_x, y], width=2, fill=elements_color)
                            x = max_x

                        avr_y = (y1 + y2) / 2
                        min_y = y1 if y1 < y2 else y2
                        max_y = y1 if y1 > y2 else y2
                        y1 = avr_y - box_size / 6
                        y2 = avr_y + box_size / 6

                        canvas.create_line(x, min_y, x, y1, width=2)
                        canvas.create_line(x, max_y, x, y2, width=2)
                        draw.line([x, min_y, x, y1], width=2, fill=elements_color)
                        draw.line([x, max_y, x, y2], width=2, fill=elements_color)

                        canvas.create_line(x, y1, x + line_size_lite, y1, width=2)
                        canvas.create_line(x, y2, x + line_size_lite, y2, width=2)
                        draw.line([x, y1, x + line_size_lite, y1], width=2, fill=elements_color)
                        draw.line([x, y2, x + line_size_lite, y2], width=2, fill=elements_color)

                        x = x + line_size_lite
                        y = avr_y
                        flies_size = scale * 10

                        if lexeme in wrapper.operators['xor']:
                            canvas.create_polygon(
                                x, y1,
                                x - flies_size, y - box_size / 2,
                                x + 2 * box_size / 3, y - box_size / 2,
                                x + box_size, y,
                                x + 2 * box_size / 3, y + box_size / 2,
                                x - flies_size, y + box_size / 2,
                                x, y2,
                                x, y1
                            )
                            draw.polygon([
                                x, y1,
                                x - flies_size, y - box_size / 2,
                                x + 2 * box_size / 3, y - box_size / 2,
                                x + box_size, y,
                                x + 2 * box_size / 3, y + box_size / 2,
                                x - flies_size, y + box_size / 2,
                                x, y2,
                                x, y1
                            ], fill=elements_color)
                            tail_size = scale * 5
                            canvas.create_polygon(
                                x, y1,
                                x - flies_size, y - box_size / 2,
                                x - flies_size + tail_size, y - box_size / 2,
                                x + tail_size, y1,
                                x + tail_size, y2,
                                x - flies_size + tail_size, y + box_size / 2,
                                x - flies_size, y + box_size / 2,
                                x, y2,
                                x, y1,
                                fill="#fc0303"
                            )
                            draw.polygon([
                                x, y1,
                                x - flies_size, y - box_size / 2,
                                x - flies_size + tail_size, y - box_size / 2,
                                x + tail_size, y1,
                                x + tail_size, y2,
                                x - flies_size + tail_size, y + box_size / 2,
                                x - flies_size, y + box_size / 2,
                                x, y2,
                                x, y1,
                            ], fill=(252, 3, 3))
                        elif lexeme in wrapper.operators['and']:
                            canvas.create_polygon(
                                x, y,
                                x, y - box_size / 2,
                                   x + 2 * box_size / 3, y - box_size / 2,
                                   x + box_size, y,
                                   x + 2 * box_size / 3, y + box_size / 2,
                                x, y + box_size / 2,
                                x, y
                            )
                            draw.polygon([
                                x, y,
                                x, y - box_size / 2,
                                   x + 2 * box_size / 3, y - box_size / 2,
                                   x + box_size, y,
                                   x + 2 * box_size / 3, y + box_size / 2,
                                x, y + box_size / 2,
                                x, y
                            ], fill=elements_color)
                        elif lexeme in wrapper.operators['or']:
                            canvas.create_polygon(
                                x, y1,
                                x - flies_size, y - box_size / 2,
                                x + 2 * box_size / 3, y - box_size / 2,
                                x + box_size, y,
                                x + 2 * box_size / 3, y + box_size / 2,
                                x - flies_size, y + box_size / 2,
                                x, y2,
                                x, y1
                            )
                            draw.polygon([
                                x, y1,
                                x - flies_size, y - box_size / 2,
                                x + 2 * box_size / 3, y - box_size / 2,
                                x + box_size, y,
                                x + 2 * box_size / 3, y + box_size / 2,
                                x - flies_size, y + box_size / 2,
                                x, y2,
                                x, y1
                            ], fill=elements_color)

                        if check_state_boxes.get() is True:
                            # Чекаем размер
                            canvas.create_rectangle(x, y - box_size / 2, x + box_size, y + box_size / 2)
                            draw.rectangle([x, y - box_size / 2, x + box_size, y + box_size / 2], outline="#000",
                                           fill=background, width=2)

                        canvas.create_line(x + box_size, y, x + box_size + line_size, y, width=2)
                        draw.line([x + box_size, y, x + box_size + line_size, y], width=2, fill=elements_color)
                        variables_positions.update({f'{variable2} {lexeme} {variable1}': {
                            "start": [x + box_size, y],
                            "end": [x + box_size + line_size, y]
                        }})
                        stack.append(f'{variable2} {lexeme} {variable1}')
            canvas.config(scrollregion=canvas.bbox('all'))

        _draw_canvas()

        def _save_canvas():
            try:
                os.makedirs(config.paths['output'], exist_ok=True)
                image.save(f"{config.paths['scheme']}", 'PNG')
                messagebox.showinfo(config.controls_names["info"]["title"][language],
                                    config.controls_names["scheme"]["info1"][language])
            except ValueError:
                messagebox.showerror(config.controls_names["error"]["title"][language],
                                     config.controls_names["scheme"]["error2"][language])

        button_image = ttk.Button(buttons_frame, text=config.controls_names["scheme"]["button1"][language],
                                  command=_save_canvas)
        button_image.grid(row=0, column=0, padx=10, pady=10)

        def _increase_size():
            nonlocal scale, width, height, image, draw
            if scale < 3:
                scale += 1
                canvas.delete("all")
                width, height = _calculate_image_size()
                image = Image.new("RGB", (width + 5, height + 5), (255, 255, 255))
                draw = ImageDraw.Draw(image)
                _draw_canvas()

        def _decrease_size():
            nonlocal scale, width, height, image, draw
            if scale > 1:
                scale -= 1
                canvas.delete("all")
                width, height = _calculate_image_size()
                image = Image.new("RGB", (width + 5, height + 5), (255, 255, 255))
                draw = ImageDraw.Draw(image)
                _draw_canvas()

        def _redraw_canvas():
            nonlocal width, height, image, draw
            canvas.delete("all")
            width, height = _calculate_image_size()
            image = Image.new("RGB", (width + 5, height + 5), (255, 255, 255))
            draw = ImageDraw.Draw(image)
            _draw_canvas()

        button_increase_size = ttk.Button(buttons_frame, text=config.controls_names["scheme"]["button2"][language],
                                          command=_increase_size)
        button_increase_size.grid(row=0, column=1, padx=10, pady=10)

        button_decrease_size = ttk.Button(buttons_frame, text=config.controls_names["scheme"]["button3"][language],
                                          command=_decrease_size)
        button_decrease_size.grid(row=0, column=2, padx=10, pady=10)

        checkbutton_boxes = ttk.Checkbutton(buttons_frame, text=config.controls_names["scheme"]["check1"][language],
                                            var=check_state_boxes, command=_redraw_canvas)
        checkbutton_boxes.grid(row=0, column=3, padx=10, pady=10)

    def _create_excel_file(self):
        language = self.selected_language.get()

        if self.entry_boolean_expression.get() == "":
            messagebox.showerror(config.controls_names["error"]["title"][language],
                                 config.controls_names["error"]["error1"][language])
            return

        wrapper = BoolWrapper(self.entry_boolean_expression.get(), language=language)
        if wrapper.analise_input() is False:
            return
        wrapper.create_truth_table()
        if wrapper.write_truth_table_to_excel(self.is_true_false_values_in_truth_table.get()):
            messagebox.showinfo(config.controls_names["info"]["title"][language],
                                config.controls_names["info"]["info1"][language])

    def _minimize_expression(self):
        language = self.selected_language.get()

        if self.entry_boolean_expression.get() == "":
            messagebox.showerror(config.controls_names["error"]["title"][language],
                                 config.controls_names["error"]["error1"][language])
            return

        wrapper = BoolWrapper(self.entry_boolean_expression.get(), language=language)
        if wrapper.analise_input() is False:
            return
        wrapper.create_truth_table()

        child_window = tkinter.Toplevel(self.window)
        child_window.geometry("520x310")
        child_window.title(config.controls_names["simple"]["window_name"][language])
        child_window.resizable(width=False, height=False)

        check_state_math = tkinter.BooleanVar()
        check_state_math.set(False)

        check_state_sop = tkinter.BooleanVar()
        check_state_sop.set(True)

        checkbutton_math = ttk.Checkbutton(child_window, text=config.controls_names["simple"]["check3"][language],
                                           var=check_state_math)
        checkbutton_math.grid(column=0, row=1, columnspan=2, padx=5, pady=5)

        def _set_sop():
            form_type = config.controls_names["simple"]["check1"][language] if check_state_sop.get() is True else \
                config.controls_names["simple"]["check2"][language]
            label_full_expression.config(text=f'{form_type}:')

        checkbutton_sop = ttk.Checkbutton(child_window, text=config.controls_names["simple"]["check1"][language],
                                          var=check_state_sop, command=_set_sop)
        checkbutton_sop.grid(column=0, row=0, columnspan=2, padx=5, pady=5)

        def _minimize():
            if not wrapper.create_kmap(is_sop=check_state_sop.get(), is_math=check_state_math.get()):
                messagebox.showerror(config.controls_names["error"]["title"][language],
                                     f'{config.controls_names["simple"]["error1"][language]} [{len(wrapper.boolean_variables)}].')
                return

            entry_full_expression["state"] = "normal"
            entry_full_expression.delete(0, tkinter.END)
            entry_full_expression.insert(0, wrapper.get_sop_or_pos_expression(is_sop=check_state_sop.get(),
                                                                              is_math=check_state_math.get()))
            entry_full_expression["state"] = "readonly"

            entry_minimized_expression["state"] = "normal"
            entry_minimized_expression.delete(0, tkinter.END)
            entry_minimized_expression.insert(0, wrapper.get_minimize_expression(is_sop=check_state_sop.get(),
                                                                                 is_math=check_state_math.get()))
            entry_minimized_expression["state"] = "readonly"

            button_copy_full_expression["state"] = "normal"
            button_copy_minimized_expression["state"] = "normal"
            button_write_to_excel["state"] = "normal"

        button_create_kmap = ttk.Button(child_window, text=config.controls_names["simple"]["button1"][language],
                                        command=_minimize)
        button_create_kmap.grid(column=0, row=2, columnspan=2, padx=5, pady=5)

        label_full_expression = tkinter.Label(child_window, text="")
        label_full_expression.grid(column=0, row=3, sticky=tkinter.W, padx=15, pady=5)
        _set_sop()

        entry_full_expression = ttk.Entry(child_window, width=80)
        entry_full_expression.grid(column=0, row=4, columnspan=2, padx=15, pady=5)
        entry_full_expression["state"] = "readonly"

        label_minimized_expression = tkinter.Label(child_window,
                                                   text=config.controls_names["simple"]["label1"][language])
        label_minimized_expression.grid(column=0, row=5, sticky=tkinter.W, padx=15, pady=5)

        entry_minimized_expression = ttk.Entry(child_window, width=80)
        entry_minimized_expression.grid(column=0, row=6, columnspan=2, padx=15, pady=5)
        entry_minimized_expression["state"] = "readonly"

        def _copy_min_expression():
            pyperclip.copy(entry_minimized_expression.get())
            messagebox.showinfo(config.controls_names["info"]["title"][language],
                                config.controls_names["simple"]["info1"][language])

        def _copy_full_expression():
            pyperclip.copy(entry_full_expression.get())
            messagebox.showinfo(config.controls_names["info"]["title"][language],
                                config.controls_names["simple"]["info2"][language])

        button_copy_full_expression = ttk.Button(child_window,
                                                 text=config.controls_names["simple"]["button2"][language],
                                                 command=_copy_full_expression)
        button_copy_full_expression.grid(column=0, row=7, padx=5, pady=10)
        button_copy_full_expression["state"] = "disable"

        button_copy_minimized_expression = ttk.Button(child_window,
                                                      text=config.controls_names["simple"]["button3"][language],
                                                      command=_copy_min_expression)
        button_copy_minimized_expression.grid(column=1, row=7, padx=5, pady=10)
        button_copy_minimized_expression["state"] = "disable"

        def _write_to_excel():
            if wrapper.write_truth_table_to_excel(_dont_close=True):
                if wrapper.write_kmap_to_excel(check_state_math.get()):
                    messagebox.showinfo(config.controls_names["info"]["title"][language],
                                        config.controls_names["simple"]["info3"][language])

        button_write_to_excel = ttk.Button(child_window, text=config.controls_names["simple"]["button4"][language],
                                           command=_write_to_excel)
        button_write_to_excel.grid(column=0, row=8, columnspan=2, padx=5, pady=5)
        button_write_to_excel["state"] = "disable"
