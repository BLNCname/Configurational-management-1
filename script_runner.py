"""Модуль для выполнения стартовых скриптов."""

import os


class ScriptRunner:
    """Класс для выполнения команд из стартового скрипта."""

    def __init__(self, emulator):
        """
        Инициализация ScriptRunner.

        Args:
            emulator: Экземпляр эмулятора
        """
        self.emulator = emulator

    def run_script(self, script_path):
        """
        Выполнить команды из файла скрипта.

        Args:
            script_path (str): Путь к файлу скрипта

        Returns:
            bool: True если скрипт выполнен успешно, False если файл не найден
        """
        if not os.path.exists(script_path):
            print(f"Ошибка: файл скрипта '{script_path}' не найден")
            return False

        print(f"\n{'=' * 60}")
        print(f"ВЫПОЛНЕНИЕ СТАРТОВОГО СКРИПТА: {script_path}")
        print(f"{'=' * 60}\n")

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Убираем пробелы и символы новой строки
                line = line.strip()

                # Пропускаем пустые строки и комментарии
                if not line or line.startswith('#'):
                    continue

                # Имитируем диалог с пользователем
                prompt = self.emulator._get_prompt()
                print(f"{prompt}{line}")

                # Выполняем команду
                try:
                    self.emulator._execute_command_silent(line)
                except Exception as e:
                    print(f"Ошибка в строке {line_num}: {e}")
                    # Продолжаем выполнение скрипта несмотря на ошибку

            print(f"\n{'=' * 60}")
            print(f"СКРИПТ ЗАВЕРШЕН")
            print(f"{'=' * 60}\n")
            return True

        except Exception as e:
            print(f"Ошибка при чтении файла скрипта: {e}")
            return False
