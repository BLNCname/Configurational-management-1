"""Команда cd - смена текущей директории."""

from commands.base import Command


class CdCommand(Command):
    """Команда-заглушка для смены директории (Этап 1)."""

    @property
    def name(self):
        return "cd"

    @property
    def description(self):
        return "Смена текущей директории"

    def execute(self, args):
        """Выполнить команду cd (заглушка)."""
        result = f"Команда: {self.name}"
        if args:
            result += f"\nАргументы: {' '.join(args)}"
        else:
            result += "\nАргументы отсутствуют"
        return result
