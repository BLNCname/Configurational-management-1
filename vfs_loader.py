"""Модуль для загрузки и сохранения VFS из/в XML."""

import xml.etree.ElementTree as ET
import base64
from vfs import VFS, File, Directory


class VFSLoader:
    """Класс для загрузки и сохранения VFS."""

    @staticmethod
    def create_default_vfs(username="user"):
        """
        Создать VFS по умолчанию.

        Args:
            username: Имя пользователя

        Returns:
            VFS: Виртуальная файловая система
        """
        vfs = VFS(username)

        # Создаем базовую структуру директорий
        vfs.create_directory("/home")
        vfs.create_directory(f"/home/{username}")
        vfs.create_directory("/etc")
        vfs.create_directory("/tmp")
        vfs.create_directory("/var")

        # Создаем несколько файлов
        vfs.create_file(f"/home/{username}/welcome.txt",
                       "Добро пожаловать в эмулятор командной оболочки!\n", "644")
        vfs.create_file(f"/home/{username}/.bashrc",
                       "# Конфигурация bash\nexport PS1='\\u@\\h:\\w\\$ '\n", "644")
        vfs.create_file("/etc/hostname",
                       "emulator-host\n", "644")

        return vfs

    @staticmethod
    def load_from_xml(xml_path, username="user"):
        """
        Загрузить VFS из XML файла.

        Args:
            xml_path: Путь к XML файлу
            username: Имя пользователя

        Returns:
            VFS: Загруженная виртуальная файловая система
        """
        try:
            tree = ET.parse(xml_path)
            root_elem = tree.getroot()

            vfs = VFS(username)

            # Загружаем корневую директорию
            if root_elem.tag == 'filesystem':
                for child in root_elem:
                    VFSLoader._load_node(child, vfs.root, vfs)

            return vfs

        except Exception as e:
            print(f"Ошибка при загрузке VFS из XML: {e}")
            print("Создается VFS по умолчанию")
            return VFSLoader.create_default_vfs(username)

    @staticmethod
    def _load_node(xml_node, parent_dir, vfs):
        """
        Рекурсивно загрузить узел из XML.

        Args:
            xml_node: XML элемент
            parent_dir: Родительская директория
            vfs: VFS объект
        """
        name = xml_node.get('name', 'unnamed')
        permissions = xml_node.get('permissions', '755')
        owner = xml_node.get('owner', vfs.username)
        group = xml_node.get('group', vfs.username)

        if xml_node.tag == 'directory':
            # Пропускаем корневую директорию "/"
            if name == '/':
                for child in xml_node:
                    VFSLoader._load_node(child, parent_dir, vfs)
            else:
                dir_node = Directory(name, permissions, owner, group)
                parent_dir.add_child(dir_node)

                # Рекурсивно загружаем дочерние элементы
                for child in xml_node:
                    VFSLoader._load_node(child, dir_node, vfs)

        elif xml_node.tag == 'file':
            content = ""
            content_elem = xml_node.find('content')

            if content_elem is not None:
                encoding = content_elem.get('encoding', 'text')

                if encoding == 'base64':
                    try:
                        content = base64.b64decode(content_elem.text or "").decode('utf-8')
                    except Exception as e:
                        print(f"Ошибка декодирования base64 для файла {name}: {e}")
                        content = ""
                else:
                    content = content_elem.text or ""

            file_node = File(name, content, permissions, owner, group)
            parent_dir.add_child(file_node)

    @staticmethod
    def save_to_xml(vfs, xml_path):
        """
        Сохранить VFS в XML файл.

        Args:
            vfs: VFS объект
            xml_path: Путь к XML файлу

        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            root_elem = ET.Element('filesystem')

            # Сохраняем корневую директорию
            VFSLoader._save_node(vfs.root, root_elem, save_root=True)

            # Форматируем XML
            VFSLoader._indent(root_elem)

            # Записываем в файл
            tree = ET.ElementTree(root_elem)
            tree.write(xml_path, encoding='utf-8', xml_declaration=True)

            return True

        except Exception as e:
            print(f"Ошибка при сохранении VFS в XML: {e}")
            return False

    @staticmethod
    def _save_node(node, parent_elem, save_root=False):
        """
        Рекурсивно сохранить узел в XML.

        Args:
            node: VFSNode
            parent_elem: Родительский XML элемент
            save_root: Сохранять ли корень как директорию
        """
        if node.is_directory():
            if save_root:
                dir_elem = ET.SubElement(parent_elem, 'directory')
                dir_elem.set('name', node.name)
                dir_elem.set('permissions', node.permissions)
                dir_elem.set('owner', node.owner)
                dir_elem.set('group', node.group)
            else:
                dir_elem = parent_elem

            # Рекурсивно сохраняем дочерние элементы
            for child_name in sorted(node.children.keys()):
                child = node.children[child_name]
                VFSLoader._save_node(child, dir_elem)

        elif node.is_file():
            file_elem = ET.SubElement(parent_elem, 'file')
            file_elem.set('name', node.name)
            file_elem.set('permissions', node.permissions)
            file_elem.set('owner', node.owner)
            file_elem.set('group', node.group)

            # Сохраняем содержимое
            if node.content:
                content_elem = ET.SubElement(file_elem, 'content')
                # Используем base64 если есть непечатные символы
                try:
                    node.content.encode('ascii')
                    content_elem.text = node.content
                    content_elem.set('encoding', 'text')
                except UnicodeEncodeError:
                    content_elem.text = base64.b64encode(node.content.encode('utf-8')).decode('ascii')
                    content_elem.set('encoding', 'base64')

    @staticmethod
    def _indent(elem, level=0):
        """
        Форматировать XML с отступами.

        Args:
            elem: XML элемент
            level: Уровень вложенности
        """
        indent_str = "\n" + "  " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent_str + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent_str
            for child in elem:
                VFSLoader._indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent_str
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent_str
