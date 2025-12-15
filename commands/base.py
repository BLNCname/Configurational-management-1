"""Базовый класс для всех команд эмулятора."""

from abc import ABC, abstractmethod


class Command(ABC):
    """Базовый класс для команд эмулятора."""

    def __init__(self, emulator):
        """
        Инициализация команды.

        Args:
            emulator: Ссылка на экземпляр эмулятора
        """
        self.emulator = emulator

    @abstractmethod
    def execute(self, args):
        """
        Выполнить команду.

        Args:
            args: Список аргументов команды

        Returns:
            str: Результат выполнения команды
        """
        pass

    @property
    @abstractmethod
    def name(self):
        """Имя команды."""
        pass

    @property
    def description(self):
        """Описание команды."""
        return "Описание команды не указано"
