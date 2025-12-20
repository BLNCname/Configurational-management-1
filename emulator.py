"""Главный модуль эмулятора командной оболочки UNIX."""

import tkinter as tk
from tkinter import scrolledtext
import platform
import getpass
import socket
from parser import CommandParser
from config import Config
from script_runner import ScriptRunner
from vfs import VFS
from vfs_loader import VFSLoader
from commands.ls import LsCommand
from commands.cd import CdCommand
from commands.exit import ExitCommand
from commands.whoami import WhoamiCommand
from commands.tail import TailCommand
from commands.tree import TreeCommand
from commands.chmod import ChmodCommand
from commands.pwd import PwdCommand


class ShellEmulator:
    """Эмулятор командной оболочки UNIX с графическим интерфейсом."""

    def __init__(self, config=None):
        """Инициализация эмулятора.

        Args:
            config: Объект конфигурации (Config)
        """
        self.config = config if config else Config()
        self.running = True
        self.hostname = socket.gethostname()

        # Инициализация VFS
        if self.config.vfs_path:
            # При загрузке из XML всегда используем "user" как username
            self.vfs = VFSLoader.load_from_xml(self.config.vfs_path, "user")
        else:
            # Для VFS по умолчанию используем системное имя пользователя
            system_username = getpass.getuser()
            self.vfs = VFSLoader.create_default_vfs(system_username)

        # Устанавливаем текущую директорию в домашнюю
        # Используем username из VFS, а не системный
        home_dir = f"/home/{self.vfs.username}"
        if not self.vfs.get_node(home_dir):
            # Если нет /home/username, пробуем /home/user
            home_dir = "/home/user"

        if self.vfs.get_node(home_dir):
            self.vfs.change_directory(home_dir)
        else:
            # Fallback to root if home doesn't exist
            self.vfs.change_directory("/")

        # Инициализация команд
        self.commands = {}
        self._register_commands()

        # Script runner
        self.script_runner = ScriptRunner(self)

        # Инициализация GUI
        self._init_gui()

    def _register_commands(self):
        """Регистрация всех доступных команд."""
        command_classes = [
            LsCommand, CdCommand, ExitCommand,
            WhoamiCommand, TailCommand, TreeCommand,
            ChmodCommand, PwdCommand
        ]
        for cmd_class in command_classes:
            cmd = cmd_class(self)
            self.commands[cmd.name] = cmd

    def _init_gui(self):
        """Инициализация графического интерфейса."""
        self.root = tk.Tk()
        self.root.title(f"Эмулятор - [{self.vfs.username}@{self.hostname}]")
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
        self._print_output(f"Пользователь: {self.vfs.username}@{self.hostname}")
        self._print_output("Введите 'exit' для выхода\n")

    def _get_prompt(self):
        """Получить строку приглашения командной строки."""
        current_dir = self.vfs.get_current_directory()
        # Сокращаем путь если это домашняя директория
        # Используем vfs.username, так как он может отличаться от системного username
        vfs_home = f"/home/{self.vfs.username}"
        if current_dir.startswith(vfs_home):
            display_dir = "~" + current_dir[len(vfs_home):]
            if not display_dir or display_dir == "~":
                display_dir = "~"
        else:
            display_dir = current_dir
        return f"[{self.vfs.username}@{self.hostname} {display_dir}]$ "

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
        Выполнить введенную команду с выводом в GUI.

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

    def _execute_command_silent(self, command_line):
        """
        Выполнить команду без вывода в GUI (для скриптов).
        Вывод идет в консоль.

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
                    print(result)
            except Exception as e:
                print(f"Ошибка выполнения команды: {e}")
        else:
            print(f"{command}: команда не найдена")

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
        # Выполнить стартовый скрипт если указан
        if self.config.startup_script:
            # Откладываем выполнение скрипта, чтобы GUI успел загрузиться
            self.root.after(100, lambda: self.script_runner.run_script(self.config.startup_script))

        self.root.mainloop()


def main():
    """Главная функция."""
    # Парсим аргументы командной строки
    config = Config.parse_args()

    # Выводим отладочную информацию если включен режим отладки
    if config.debug:
        config.print_debug_info()

    # Создаем и запускаем эмулятор
    emulator = ShellEmulator(config)
    emulator.run()


if __name__ == "__main__":
    main()
