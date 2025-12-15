"""Команда cd - смена текущей директории."""

from commands.base import Command


class CdCommand(Command):
    """Команда для смены директории."""

    @property
    def name(self):
        return "cd"

    @property
    def description(self):
        return "Смена текущей директории"

    def execute(self, args):
        """Выполнить команду cd."""
        # Если аргументов нет, переходим в домашнюю директорию
        if not args:
            target_path = f"/home/{self.emulator.username}"
        else:
            target_path = args[0]

        # Пытаемся сменить директорию
        if self.emulator.vfs.change_directory(target_path):
            # Успешно сменили директорию
            return None  # Нет вывода при успехе
        else:
            # Ошибка - директория не найдена
            return f"cd: {target_path}: Нет такого файла или каталога"
