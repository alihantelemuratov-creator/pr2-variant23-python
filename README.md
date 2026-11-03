# Практическая работа №2 — вариант №23 (этап 1)

Дисциплина: «Прикладная разработка серверных частей веб-приложений на языке Питон».

## Цель

Создать CLI-утилиту, которая получает входной файл и выводит результат
в стандартный вывод. Показать четыре примера.

**Важно:** вычисления в `src/computation.py` — временный учебный пример
со статистикой массива чисел. Необходимо заменить на тему курсовой работы.

## Установка и запуск (Windows)

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m src.cli examples/input1.json
python -m src.cli examples/input2.json
python -m src.cli examples/input3.json
python -m src.cli examples/input4.json
```

## Формат данных

Входной JSON: `{"numbers": [1, 2, 3, 4, 5]}`.
Выходной JSON: количество, сумма, среднее, минимум и максимум.

## Тестирование

```cmd
python -m pytest tests -v
```

## Коммит

```cmd
git init
git add .
git commit -m "feat(cli): реализован этап 1 с четырьмя примерами"
```

Следующий этап: HTTP API, клиент и MBT.
