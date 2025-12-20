"""Команда tree - древовидный вывод структуры директорий."""

from commands.base import Command


class TreeCommand(Command):
    """Команда для древовидного вывода структуры директорий."""

    @property
    def name(self):
        return "tree"

    @property
    def description(self):
        return "Древовидный вывод структуры директорий"

    def execute(self, args):
        """Выполнить команду tree."""
        # Определяем путь
        if args:
            target_path = args[0]
        else:
            target_path = self.emulator.vfs.get_current_directory()

        # Получаем узел
        node = self.emulator.vfs.get_node(target_path)

        if node is None:
            return f"tree: {target_path}: Нет такого файла или каталога"

        if not node.is_directory():
            return f"tree: {target_path}: Не является каталогом"

        # Формируем дерево
        lines = [target_path]
        self._build_tree(node, "", lines, is_last=True)

        # Подсчет статистики
        dir_count, file_count = self._count_items(node)

        lines.append("")
        lines.append(f"{dir_count} directories, {file_count} files")

        return '\n'.join(lines)

    def _build_tree(self, directory, prefix, lines, is_last=True):
        """
        Рекурсивно построить дерево.

        Args:
            directory: Директория
            prefix: Префикс для текущего уровня
            lines: Список строк результата
            is_last: Является ли элемент последним в списке
        """
        children_names = sorted(directory.children.keys())

        for i, name in enumerate(children_names):
            child = directory.get_child(name)
            is_last_child = (i == len(children_names) - 1)

            # Формируем символы дерева
            if is_last_child:
                connector = "└── "
                extension = "    "
            else:
                connector = "├── "
                extension = "│   "

            # Добавляем строку
            if child.is_directory():
                lines.append(f"{prefix}{connector}{name}/")
                # Рекурсивно обходим поддиректорию
                self._build_tree(child, prefix + extension, lines, is_last_child)
            else:
                # Исполняемые файлы помечаем звездочкой - проверяем бит execute у любой группы
                is_executable = any(int(digit) & 1 for digit in child.permissions if digit.isdigit())
                if is_executable:
                    lines.append(f"{prefix}{connector}{name}*")
                else:
                    lines.append(f"{prefix}{connector}{name}")

    def _count_items(self, directory):
        """
        Подсчитать количество директорий и файлов.

        Args:
            directory: Директория

        Returns:
            tuple: (количество_директорий, количество_файлов)
        """
        dir_count = 0
        file_count = 0

        for child in directory.children.values():
            if child.is_directory():
                dir_count += 1
                sub_dirs, sub_files = self._count_items(child)
                dir_count += sub_dirs
                file_count += sub_files
            else:
                file_count += 1

        return dir_count, file_count
