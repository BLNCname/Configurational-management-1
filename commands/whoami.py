"""Команда whoami - вывод текущего пользователя."""

from commands.base import Command


class WhoamiCommand(Command):
    """Команда для вывода имени текущего пользователя."""

    @property
    def name(self):
        return "whoami"

    @property
    def description(self):
        return "Вывод имени текущего пользователя"

    def execute(self, args):
        """Выполнить команду whoami."""
        return self.emulator.username
