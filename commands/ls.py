"""Команда ls - список файлов и директорий."""

from commands.base import Command


class LsCommand(Command):
    """Команда для вывода списка файлов и директорий."""

    @property
    def name(self):
        return "ls"

    @property
    def description(self):
        return "Вывод списка файлов и директорий"

    def execute(self, args):
        """Выполнить команду ls."""
        # Парсим аргументы
        show_hidden = False
        show_long = False
        target_path = None

        for arg in args:
            if arg == '-a':
                show_hidden = True
            elif arg == '-l':
                show_long = True
            elif arg == '-la' or arg == '-al':
                show_hidden = True
                show_long = True
            elif not arg.startswith('-'):
                target_path = arg

        # Если путь не указан, используем текущую директорию
        if target_path is None:
            target_path = self.emulator.vfs.get_current_directory()

        # Получаем узел
        node = self.emulator.vfs.get_node(target_path)

        if node is None:
            return f"ls: не удается получить доступ к '{target_path}': Нет такого файла или каталога"

        # Если это файл, просто выводим его имя
        if node.is_file():
            if show_long:
                return self._format_long_entry(node)
            else:
                return node.name

        # Если это директория, выводим её содержимое
        if node.is_directory():
            children_names = node.list_children(show_hidden)

            if not children_names:
                return ""  # Пустая директория

            if show_long:
                return self._format_long_listing(node, children_names)
            else:
                return self._format_short_listing(children_names, node)

    def _format_short_listing(self, names, directory):
        """
        Форматировать короткий вывод (без -l).

        Args:
            names: Список имен файлов
            directory: Директория

        Returns:
            str: Отформатированный вывод
        """
        result = []
        for name in names:
            child = directory.get_child(name)
            if child and child.is_directory():
                # Директории выделяем (в GUI цвет не поддерживается, но можем добавить /)
                result.append(name)
            elif child and child.is_file():
                # Исполняемые файлы выделяем - проверяем бит execute у любой группы (user/group/other)
                is_executable = any(int(digit) & 1 for digit in child.permissions if digit.isdigit())
                if is_executable:
                    result.append(name + '*')
                else:
                    result.append(name)
            else:
                result.append(name)

        # Выводим в несколько колонок (упрощенно - по 4 в строку)
        output = []
        for i in range(0, len(result), 4):
            output.append('  '.join(result[i:i+4]))

        return '\n'.join(output)

    def _format_long_listing(self, directory, names):
        """
        Форматировать длинный вывод (с -l).

        Args:
            directory: Директория
            names: Список имен файлов

        Returns:
            str: Отформатированный вывод
        """
        lines = []
        for name in names:
            child = directory.get_child(name)
            if child:
                lines.append(self._format_long_entry(child))

        return '\n'.join(lines)

    def _format_long_entry(self, node):
        """
        Форматировать одну запись в длинном формате.

        Args:
            node: Узел VFS

        Returns:
            str: Отформатированная строка
        """
        # Тип файла
        if node.is_directory():
            file_type = 'd'
        else:
            file_type = '-'

        # Права доступа
        perms = node.get_permissions_string()

        # Количество ссылок (упрощенно)
        links = 2 if node.is_directory() else 1

        # Владелец и группа
        owner = node.owner
        group = node.group

        # Размер
        if node.is_file():
            size = node.get_size()
        else:
            size = 4096  # Стандартный размер директории

        # Дата модификации
        date_str = node.modified_time.strftime("%b %d %H:%M")

        # Имя
        name = node.name
        if node.is_directory():
            name += '/'

        return f"{file_type}{perms} {links:2d} {owner:8s} {group:8s} {size:8d} {date_str} {name}"
