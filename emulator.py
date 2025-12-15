"""Главный модуль эмулятора командной оболочки UNIX."""

import tkinter as tk
from tkinter import scrolledtext
import platform
import getpass
import socket
from parser import CommandParser
from commands.ls import LsCommand
from commands.cd import CdCommand
from commands.exit import ExitCommand


class ShellEmulator:
    """Эмулятор командной оболочки UNIX с графическим интерфейсом."""

    def __init__(self):
        """Инициализация эмулятора."""
        self.running = True
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.current_dir = "/"

        # Инициализация команд
        self.commands = {}
        self._register_commands()

        # Инициализация GUI
        self._init_gui()

    def _register_commands(self):
        """Регистрация всех доступных команд."""
        command_classes = [LsCommand, CdCommand, ExitCommand]
        for cmd_class in command_classes:
            cmd = cmd_class(self)
            self.commands[cmd.name] = cmd

    def _init_gui(self):
        """Инициализация графического интерфейса."""
        self.root = tk.Tk()
        self.root.title(f"Эмулятор - [{self.username}@{self.hostname}]")
        self.root.geometry("800x600")

        # Текстовое поле для вывода
        self.output_text = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            width=80,
            height=30,
            font=("Courier", 10),
            bg="black",
            fg="white"
        )
        self.output_text.pack(padx=10, pady=(10, 5), fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED)

        # Фрейм для поля ввода
        input_frame = tk.Frame(self.root)
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        # Метка с приглашением командной строки
        self.prompt_label = tk.Label(
            input_frame,
            text=self._get_prompt(),
            font=("Courier", 10),
            bg="black",
            fg="green"
        )
        self.prompt_label.pack(side=tk.LEFT)

        # Поле ввода команд
        self.input_entry = tk.Entry(
            input_frame,
            font=("Courier", 10),
            bg="black",
            fg="white",
            insertbackground="white"
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self._on_enter)
        self.input_entry.focus()

        # История команд
        self.history = []
        self.history_index = 0
        self.input_entry.bind("<Up>", self._history_up)
        self.input_entry.bind("<Down>", self._history_down)

        # Приветственное сообщение
        self._print_output("Эмулятор командной оболочки UNIX")
        self._print_output(f"Система: {platform.system()} {platform.release()}")
        self._print_output(f"Пользователь: {self.username}@{self.hostname}")
        self._print_output("Введите 'exit' для выхода\n")

    def _get_prompt(self):
        """Получить строку приглашения командной строки."""
        return f"[{self.username}@{self.hostname} {self.current_dir}]$ "

    def _update_prompt(self):
        """Обновить строку приглашения."""
        self.prompt_label.config(text=self._get_prompt())

    def _print_output(self, text):
        """
        Вывести текст в окно вывода.

        Args:
            text (str): Текст для вывода
        """
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def _on_enter(self, event):
        """
        Обработчик нажатия Enter.

        Args:
            event: Событие клавиатуры
        """
        command_line = self.input_entry.get()
        self.input_entry.delete(0, tk.END)

        # Добавляем в историю
        if command_line.strip():
            self.history.append(command_line)
            self.history_index = len(self.history)

        # Выводим введенную команду
        self._print_output(f"{self._get_prompt()}{command_line}")

        # Парсим и выполняем команду
        self._execute_command(command_line)

        # Обновляем приглашение
        self._update_prompt()

        # Если пользователь вышел, закрываем окно
        if not self.running:
            self.root.after(500, self.root.destroy)

    def _execute_command(self, command_line):
        """
        Выполнить введенную команду.

        Args:
            command_line (str): Строка с командой
        """
        command, args = CommandParser.parse(command_line)

        if command is None:
            return

        if command in self.commands:
            try:
                result = self.commands[command].execute(args)
                if result:
                    self._print_output(result)
            except Exception as e:
                self._print_output(f"Ошибка выполнения команды: {e}")
        else:
            self._print_output(f"{command}: команда не найдена")

    def _history_up(self, event):
        """Обработчик стрелки вверх - предыдущая команда из истории."""
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.history[self.history_index])

    def _history_down(self, event):
        """Обработчик стрелки вниз - следующая команда из истории."""
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.history[self.history_index])
        elif self.history_index == len(self.history) - 1:
            self.history_index = len(self.history)
            self.input_entry.delete(0, tk.END)

    def run(self):
        """Запустить эмулятор."""
        self.root.mainloop()


def main():
    """Главная функция."""
    emulator = ShellEmulator()
    emulator.run()


if __name__ == "__main__":
    main()
