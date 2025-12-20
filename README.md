# Эмулятор командной оболочки UNIX

Эмулятор командной оболочки UNIX с графическим интерфейсом, поддерживающий виртуальную файловую систему и основные команды.

## Описание

Данный проект представляет собой эмулятор командной оболочки операционной системы UNIX. Эмулятор работает в графическом интерфейсе (GUI) и предоставляет пользователю возможность взаимодействовать с виртуальной файловой системой через привычные команды командной строки.

## Требования

- Python 3.7+
- tkinter (обычно входит в стандартную поставку Python)
- Никаких дополнительных зависимостей

## Команды сборки и запуска

### Базовый запуск
```bash
python emulator.py
```

### Запуск с параметрами
```bash
# Загрузить VFS из XML файла
python emulator.py --vfs-path vfs_examples/minimal.xml

# Выполнить стартовый скрипт
python emulator.py --startup-script scripts/test_basic_commands.txt

# Включить отладочный вывод
python emulator.py --debug

# Комбинация параметров
python emulator.py --vfs-path vfs_examples/deep_structure.xml --startup-script scripts/test_chmod.txt
```

## Поддерживаемые команды

### ls - Список файлов и директорий
```bash
ls              # Список файлов в текущей директории
ls /home        # Список файлов в указанной директории
ls -l           # Детальный формат (права, владелец, размер)
ls -a           # Показать скрытые файлы (начинающиеся с .)
ls -la          # Комбинация флагов
```

### cd - Смена текущей директории
```bash
cd /home/user   # Абсолютный путь
cd documents    # Относительный путь
cd ..           # На уровень вверх
cd ~            # Домашняя директория
cd -            # Предыдущая директория
cd              # Переход в домашнюю директорию
```

### whoami - Вывод имени пользователя
```bash
whoami          # Выводит имя текущего пользователя
```

### pwd - Вывод текущей рабочей директории
```bash
pwd             # Выводит полный путь текущей директории
```

### tail - Вывод последних строк файла
```bash
tail file.txt        # Последние 10 строк
tail -n 5 file.txt   # Последние 5 строк
```

### tree - Древовидный вывод структуры
```bash
tree            # Дерево текущей директории
tree /home      # Дерево указанной директории
```

### chmod - Изменение прав доступа
```bash
# Символьный формат
chmod u+x file.sh              # Добавить право на выполнение владельцу
chmod go-w file.txt            # Убрать право на запись у группы и остальных
chmod a+r file.txt             # Добавить право на чтение всем
chmod u+rwx,g-w file.txt       # Комбинированное изменение

# Числовой формат
chmod 755 script.sh            # rwxr-xr-x
chmod 644 file.txt             # rw-r--r--
```

### exit - Выход из эмулятора
```bash
exit            # Завершает работу эмулятора
```

## Примеры использования

### Пример 1: Базовая навигация
```bash
$ python emulator.py
[user@hostname ~]$ ls
documents  projects  readme.txt  welcome.txt

[user@hostname ~]$ cd documents
[user@hostname ~/documents]$ ls
personal  work

[user@hostname ~/documents]$ cd ..
[user@hostname ~]$ whoami
user
```

### Пример 2: Работа с правами
```bash
[user@hostname ~]$ ls -l welcome.txt
-rw-r--r--  1 user     user          45 Dec 15 10:30 welcome.txt

[user@hostname ~]$ chmod u+x welcome.txt
[user@hostname ~]$ ls -l welcome.txt
-rwxr--r--  1 user     user          45 Dec 15 10:30 welcome.txt*

[user@hostname ~]$ chmod 644 welcome.txt
[user@hostname ~]$ ls -l welcome.txt
-rw-r--r--  1 user     user          45 Dec 15 10:30 welcome.txt
```

### Пример 3: Использование tree и tail
```bash
[user@hostname ~]$ tree
/home/user
├── documents/
│   ├── work/
│   │   └── report.txt
│   └── personal/
│       └── notes.txt
├── projects/
│   └── python/
│       └── main.py*
└── readme.txt

3 directories, 4 files

[user@hostname ~]$ tail -n 5 documents/work/report.txt
Раздел 1
Раздел 2
Заключение
```

## Виртуальная файловая система (VFS)

VFS хранится в XML формате. Пример структуры:

```xml
<?xml version='1.0' encoding='utf-8'?>
<filesystem>
  <directory name="/" permissions="755" owner="root" group="root">
    <directory name="home" permissions="755" owner="root" group="root">
      <directory name="user" permissions="755" owner="user" group="user">
        <file name="welcome.txt" permissions="644" owner="user" group="user">
          <content encoding="text">Привет, мир!</content>
        </file>
      </directory>
    </directory>
  </directory>
</filesystem>
```

## Структура проекта

```
Configurational-management-1/
├── README.md                      # Документация
├── emulator.py                    # Главный модуль эмулятора
├── parser.py                      # Парсер команд
├── config.py                      # Обработка конфигурации
├── vfs.py                         # Виртуальная файловая система
├── vfs_loader.py                  # Загрузка/сохранение VFS
├── script_runner.py               # Выполнение стартовых скриптов
├── commands/                      # Модули команд
│   ├── __init__.py
│   ├── base.py
│   ├── ls.py
│   ├── cd.py
│   ├── whoami.py
│   ├── tail.py
│   ├── tree.py
│   ├── chmod.py
│   └── exit.py
├── vfs_examples/                  # Примеры виртуальных ФС
│   ├── minimal.xml
│   ├── multi_files.xml
│   └── deep_structure.xml
└── scripts/                       # Тестовые скрипты
    ├── test_startup.txt
    ├── test_vfs.txt
    ├── test_basic_commands.txt
    └── test_chmod.txt
```