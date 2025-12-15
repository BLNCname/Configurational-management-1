"""Команда выхода из эмулятора."""

from commands.base import Command


class ExitCommand(Command):
    """Команда для выхода из эмулятора."""

    @property
    def name(self):
        return "exit"

    @property
    def description(self):
        return "Выход из эмулятора"

    def execute(self, args):
        """Выполнить команду exit."""
        # Флаг для завершения работы эмулятора
        self.emulator.running = False
        return "Выход из эмулятора..."
