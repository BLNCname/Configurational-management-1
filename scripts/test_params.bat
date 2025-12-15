@echo off
REM Тестовый скрипт для проверки параметров командной строки (Windows)
REM Этап 2

echo ========================================
echo Тест 1: Запуск без параметров
echo ========================================
timeout /t 2 /nobreak >nul
REM python emulator.py

echo.
echo ========================================
echo Тест 2: Запуск с отладкой
echo ========================================
python emulator.py --debug
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Тест 3: Запуск со стартовым скриптом
echo ========================================
python emulator.py --startup-script scripts/test_startup.txt --debug
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo Тесты завершены
echo ========================================
