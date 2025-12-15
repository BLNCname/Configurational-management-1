"""Команда chmod - изменение прав доступа."""

from commands.base import Command
import re


class ChmodCommand(Command):
    """Команда для изменения прав доступа к файлам и директориям."""

    @property
    def name(self):
        return "chmod"

    @property
    def description(self):
        return "Изменение прав доступа к файлам и директориям"

    def execute(self, args):
        """Выполнить команду chmod."""
        if len(args) < 2:
            return "chmod: отсутствует операнд\nИспользование: chmod РЕЖИМ ФАЙЛ"

        mode = args[0]
        file_path = args[1]

        # Получаем узел
        node = self.emulator.vfs.get_node(file_path)

        if node is None:
            return f"chmod: не удается получить доступ к '{file_path}': Нет такого файла или каталога"

        # Парсим и применяем права
        try:
            new_permissions = self._parse_and_apply_mode(mode, node.permissions)
            node.permissions = new_permissions
            return None  # Успешно, нет вывода
        except ValueError as e:
            return f"chmod: {e}"

    def _parse_and_apply_mode(self, mode, current_perms):
        """
        Парсить символьный формат прав и применить их.

        Args:
            mode: Строка с режимом (например, u+x, go-w, u+rwx,g-x)
            current_perms: Текущие права (строка из 3 цифр)

        Returns:
            str: Новые права (строка из 3 цифр)

        Raises:
            ValueError: Если формат неверный
        """
        # Проверяем, не числовой ли формат (опционально поддержим для полноты)
        if re.match(r'^\d{3}$', mode):
            # Числовой формат
            for digit in mode:
                if digit not in '01234567':
                    raise ValueError(f"неверный режим: '{mode}'")
            return mode

        # Символьный формат
        # Разбиваем по запятым для поддержки множественных изменений
        changes = mode.split(',')

        # Конвертируем текущие права в числовой формат
        user_perm = int(current_perms[0])
        group_perm = int(current_perms[1])
        other_perm = int(current_perms[2])

        for change in changes:
            change = change.strip()

            # Парсим формат: [ugoa]+[-+=][rwx]+
            match = re.match(r'^([ugoa]+)([-+=])([rwx]+)$', change)

            if not match:
                raise ValueError(f"неверный режим: '{change}'")

            who, operator, perms = match.groups()

            # Преобразуем буквы прав в числа
            perm_value = 0
            if 'r' in perms:
                perm_value += 4
            if 'w' in perms:
                perm_value += 2
            if 'x' in perms:
                perm_value += 1

            # Применяем изменения к указанным группам
            for target in who:
                if target == 'u':
                    user_perm = self._apply_operation(user_perm, operator, perm_value)
                elif target == 'g':
                    group_perm = self._apply_operation(group_perm, operator, perm_value)
                elif target == 'o':
                    other_perm = self._apply_operation(other_perm, operator, perm_value)
                elif target == 'a':
                    # Применяем ко всем
                    user_perm = self._apply_operation(user_perm, operator, perm_value)
                    group_perm = self._apply_operation(group_perm, operator, perm_value)
                    other_perm = self._apply_operation(other_perm, operator, perm_value)

        # Формируем результат
        return f"{user_perm}{group_perm}{other_perm}"

    def _apply_operation(self, current, operator, value):
        """
        Применить операцию к правам.

        Args:
            current: Текущее значение прав (0-7)
            operator: Оператор (+, -, =)
            value: Значение для применения

        Returns:
            int: Новое значение прав (0-7)
        """
        if operator == '+':
            # Добавить права
            return current | value
        elif operator == '-':
            # Убрать права
            return current & ~value
        elif operator == '=':
            # Установить права
            return value
        else:
            return current
