"""Команда ls - список файлов и директорий."""

from commands.base import Command


class LsCommand(Command):
    """Команда-заглушка для вывода списка файлов (Этап 1)."""

    @property
    def name(self):
        return "ls"

    @property
    def description(self):
        return "Вывод списка файлов и директорий"

    def execute(self, args):
        """Выполнить команду ls (заглушка)."""
        result = f"Команда: {self.name}"
        if args:
            result += f"\nАргументы: {' '.join(args)}"
        else:
            result += "\nАргументы отсутствуют"
        return result
