"""Команда tail - вывод последних строк файла."""

from commands.base import Command


class TailCommand(Command):
    """Команда для вывода последних строк файла."""

    @property
    def name(self):
        return "tail"

    @property
    def description(self):
        return "Вывод последних строк файла"

    def execute(self, args):
        """Выполнить команду tail."""
        # Параметры по умолчанию
        num_lines = 10
        file_path = None

        # Парсим аргументы
        i = 0
        while i < len(args):
            if args[i] == '-n' and i + 1 < len(args):
                try:
                    num_lines = int(args[i + 1])
                    i += 2
                except ValueError:
                    return f"tail: неверное число строк: '{args[i + 1]}'"
            elif not args[i].startswith('-'):
                file_path = args[i]
                i += 1
            else:
                i += 1

        # Проверка наличия имени файла
        if file_path is None:
            return "tail: отсутствует операнд - имя файла"

        # Получаем узел файла
        node = self.emulator.vfs.get_node(file_path)

        if node is None:
            return f"tail: не удается открыть '{file_path}' для чтения: Нет такого файла или каталога"

        if not node.is_file():
            return f"tail: ошибка чтения '{file_path}': Это каталог"

        # Читаем содержимое файла
        content = node.read()

        # Разделяем на строки
        lines = content.splitlines()

        # Берем последние N строк
        if num_lines >= len(lines):
            result_lines = lines
        else:
            result_lines = lines[-num_lines:]

        return '\n'.join(result_lines)
