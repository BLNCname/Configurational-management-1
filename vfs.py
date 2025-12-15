"""Модуль виртуальной файловой системы."""

import os
from datetime import datetime


class VFSNode:
    """Базовый класс для узлов файловой системы."""

    def __init__(self, name, permissions="755", owner="root", group="root"):
        """
        Инициализация узла.

        Args:
            name: Имя файла/директории
            permissions: Права доступа (строка из 3 цифр)
            owner: Владелец
            group: Группа
        """
        self.name = name
        self.permissions = permissions
        self.owner = owner
        self.group = group
        self.modified_time = datetime.now()

    def is_directory(self):
        """Проверить, является ли узел директорией."""
        return False

    def is_file(self):
        """Проверить, является ли узел файлом."""
        return False

    def get_permissions_string(self):
        """Получить строковое представление прав доступа (например, rwxr-xr-x)."""
        perm_map = {
            '0': '---',
            '1': '--x',
            '2': '-w-',
            '3': '-wx',
            '4': 'r--',
            '5': 'r-x',
            '6': 'rw-',
            '7': 'rwx'
        }

        if len(self.permissions) != 3:
            return '---------'

        result = ''
        for digit in self.permissions:
            result += perm_map.get(digit, '---')

        return result


class File(VFSNode):
    """Класс для представления файла."""

    def __init__(self, name, content="", permissions="644", owner="root", group="root"):
        """
        Инициализация файла.

        Args:
            name: Имя файла
            content: Содержимое файла
            permissions: Права доступа
            owner: Владелец
            group: Группа
        """
        super().__init__(name, permissions, owner, group)
        self.content = content

    def is_file(self):
        return True

    def get_size(self):
        """Получить размер файла в байтах."""
        return len(self.content.encode('utf-8'))

    def read(self):
        """Прочитать содержимое файла."""
        return self.content

    def write(self, content):
        """
        Записать содержимое в файл.

        Args:
            content: Новое содержимое
        """
        self.content = content
        self.modified_time = datetime.now()


class Directory(VFSNode):
    """Класс для представления директории."""

    def __init__(self, name, permissions="755", owner="root", group="root"):
        """
        Инициализация директории.

        Args:
            name: Имя директории
            permissions: Права доступа
            owner: Владелец
            group: Группа
        """
        super().__init__(name, permissions, owner, group)
        self.children = {}

    def is_directory(self):
        return True

    def add_child(self, node):
        """
        Добавить дочерний узел.

        Args:
            node: Узел (File или Directory)
        """
        self.children[node.name] = node

    def get_child(self, name):
        """
        Получить дочерний узел по имени.

        Args:
            name: Имя узла

        Returns:
            VFSNode или None
        """
        return self.children.get(name)

    def remove_child(self, name):
        """
        Удалить дочерний узел.

        Args:
            name: Имя узла

        Returns:
            bool: True если удален, False если не найден
        """
        if name in self.children:
            del self.children[name]
            return True
        return False

    def list_children(self, show_hidden=False):
        """
        Получить список дочерних узлов.

        Args:
            show_hidden: Показывать ли скрытые файлы (начинающиеся с .)

        Returns:
            list: Список имен дочерних узлов
        """
        if show_hidden:
            return sorted(self.children.keys())
        else:
            return sorted([name for name in self.children.keys() if not name.startswith('.')])


class VFS:
    """Виртуальная файловая система."""

    def __init__(self, username="user"):
        """
        Инициализация VFS.

        Args:
            username: Имя пользователя для домашней директории
        """
        self.username = username
        self.root = Directory("/", "755", "root", "root")
        self.current_path = "/"
        self.previous_path = "/"

    def _normalize_path(self, path):
        """
        Нормализовать путь (убрать .., ., повторяющиеся /).

        Args:
            path: Путь для нормализации

        Returns:
            str: Нормализованный путь
        """
        # Если путь относительный, делаем его абсолютным
        if not path.startswith('/'):
            if self.current_path == '/':
                path = '/' + path
            else:
                path = self.current_path + '/' + path

        # Разделяем на компоненты
        parts = []
        for part in path.split('/'):
            if part == '' or part == '.':
                continue
            elif part == '..':
                if parts:
                    parts.pop()
            else:
                parts.append(part)

        # Собираем обратно
        if not parts:
            return '/'
        return '/' + '/'.join(parts)

    def resolve_path(self, path):
        """
        Преобразовать путь с учетом ~ и -.

        Args:
            path: Путь

        Returns:
            str: Преобразованный путь
        """
        if path == '~':
            return f'/home/{self.username}'
        elif path.startswith('~/'):
            return f'/home/{self.username}' + path[1:]
        elif path == '-':
            return self.previous_path
        else:
            return path

    def get_node(self, path):
        """
        Получить узел по пути.

        Args:
            path: Путь к узлу

        Returns:
            VFSNode или None
        """
        path = self.resolve_path(path)
        path = self._normalize_path(path)

        if path == '/':
            return self.root

        parts = path.strip('/').split('/')
        current = self.root

        for part in parts:
            if not current.is_directory():
                return None
            current = current.get_child(part)
            if current is None:
                return None

        return current

    def create_file(self, path, content="", permissions="644"):
        """
        Создать файл.

        Args:
            path: Путь к файлу
            content: Содержимое файла
            permissions: Права доступа

        Returns:
            bool: True если создан, False если ошибка
        """
        path = self._normalize_path(path)
        dir_path = os.path.dirname(path)
        file_name = os.path.basename(path)

        parent = self.get_node(dir_path)
        if parent is None or not parent.is_directory():
            return False

        file_node = File(file_name, content, permissions, self.username, self.username)
        parent.add_child(file_node)
        return True

    def create_directory(self, path, permissions="755"):
        """
        Создать директорию.

        Args:
            path: Путь к директории
            permissions: Права доступа

        Returns:
            bool: True если создана, False если ошибка
        """
        path = self._normalize_path(path)
        dir_path = os.path.dirname(path)
        dir_name = os.path.basename(path)

        parent = self.get_node(dir_path)
        if parent is None or not parent.is_directory():
            return False

        dir_node = Directory(dir_name, permissions, self.username, self.username)
        parent.add_child(dir_node)
        return True

    def change_directory(self, path):
        """
        Сменить текущую директорию.

        Args:
            path: Путь к новой директории

        Returns:
            bool: True если успешно, False если ошибка
        """
        path = self.resolve_path(path)
        path = self._normalize_path(path)

        node = self.get_node(path)
        if node is None or not node.is_directory():
            return False

        self.previous_path = self.current_path
        self.current_path = path
        return True

    def get_current_directory(self):
        """Получить текущую директорию."""
        return self.current_path
