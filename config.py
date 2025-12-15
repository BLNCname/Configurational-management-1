"""Модуль для обработки конфигурации и параметров командной строки."""

import argparse
import sys


class Config:
    """Класс для хранения и обработки конфигурации эмулятора."""

    def __init__(self):
        """Инициализация конфигурации."""
        self.vfs_path = None
        self.startup_script = None
        self.debug = False

    @staticmethod
    def parse_args(args=None):
        """
        Парсинг аргументов командной строки.

        Args:
            args: Список аргументов (если None, используется sys.argv)

        Returns:
            Config: Объект конфигурации
        """
        parser = argparse.ArgumentParser(
            description='Эмулятор командной оболочки UNIX',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''
Примеры использования:
  python emulator.py
  python emulator.py --vfs-path vfs_examples/minimal.xml
  python emulator.py --startup-script scripts/test_startup.txt
  python emulator.py --vfs-path vfs.xml --startup-script start.txt --debug
            '''
        )

        parser.add_argument(
            '--vfs-path',
            type=str,
            help='Путь к файлу виртуальной файловой системы (XML)'
        )

        parser.add_argument(
            '--startup-script',
            type=str,
            help='Путь к стартовому скрипту для выполнения команд'
        )

        parser.add_argument(
            '--debug',
            action='store_true',
            help='Включить отладочный вывод'
        )

        parsed_args = parser.parse_args(args)

        config = Config()
        config.vfs_path = parsed_args.vfs_path
        config.startup_script = parsed_args.startup_script
        config.debug = parsed_args.debug

        return config

    def print_debug_info(self):
        """Вывести отладочную информацию о конфигурации."""
        print("=" * 60)
        print("КОНФИГУРАЦИЯ ЭМУЛЯТОРА")
        print("=" * 60)
        print(f"VFS Path: {self.vfs_path if self.vfs_path else 'По умолчанию (в памяти)'}")
        print(f"Startup Script: {self.startup_script if self.startup_script else 'Не указан'}")
        print(f"Debug Mode: {'Включен' if self.debug else 'Выключен'}")
        print("=" * 60)
        print()
