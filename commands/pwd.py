"""Команда pwd - вывод текущей директории."""

from commands.base import Command


class PwdCommand(Command):
    """Команда для вывода текущей рабочей директории."""

    @property
    def name(self):
        return "pwd"

    @property
    def description(self):
        return "Вывод текущей рабочей директории"

    def execute(self, args):
        """Выполнить команду pwd."""
        return self.emulator.vfs.get_current_directory()
