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
            # Используем VFS username, так как он может отличаться от системного
            target_path = f"/home/{self.emulator.vfs.username}"
            # Если такой директории нет, пробуем /home/user
            if not self.emulator.vfs.get_node(target_path):
                target_path = "/home/user"
        else:
            target_path = args[0]

        # Пытаемся сменить директорию
        if self.emulator.vfs.change_directory(target_path):
            # Успешно сменили директорию
            return None  # Нет вывода при успехе
        else:
            # Ошибка - директория не найдена
            return f"cd: {target_path}: Нет такого файла или каталога"
