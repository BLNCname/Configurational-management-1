"""Парсер команд для эмулятора командной оболочки."""

import shlex


class CommandParser:
    """Парсер для разбора введенных пользователем команд."""

    @staticmethod
    def parse(input_line):
        """
        Разобрать строку ввода на команду и аргументы.

        Args:
            input_line (str): Строка ввода пользователя

        Returns:
            tuple: (команда, список_аргументов) или (None, []) если строка пустая
        """
        # Убираем пробелы в начале и конце
        input_line = input_line.strip()

        # Если строка пустая, возвращаем None
        if not input_line:
            return None, []

        try:
            # Используем shlex для корректной обработки кавычек и пробелов
            parts = shlex.split(input_line)
        except ValueError:
            # В случае ошибки парсинга (незакрытые кавычки и т.д.)
            # Разделяем простым split
            parts = input_line.split()

        if not parts:
            return None, []

        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        return command, args
