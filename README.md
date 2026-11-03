# Практическая работа №2 — вариант №23

Дисциплина: «Прикладная разработка серверных частей веб-приложений на языке Питон».

## Этап 1. CLI

Утилита принимает JSON-файл и направляет результат вычисления в stdout.
Четыре входных файла расположены в `examples/`.

**Важно:** статистика массива в `src/computation.py` — временная
демонстрационная задача. По условию её нужно заменить вычислениями
по теме курсовой работы.

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m src.cli examples/input1.json
python -m src.cli examples/input2.json
python -m src.cli examples/input3.json
python -m src.cli examples/input4.json
```

## Этап 2. HTTP API

Сервер построен на `BaseHTTPRequestHandler`.
Все ответы — JSON, для запросов требуются:

- `Accept: text/json`;
- `Accept-Language: ru`.

При отсутствии любого из них возвращается HTTP 406.

Маршруты: `PUT /api/save/member/:uid`,
`POST /api/collect/member`, `GET /api/read/member`,
`PUT /api/save/task/:uid`, `POST /api/collect/task/:member`,
`GET /api/read/task`, `POST /api/collect/response/:task`,
`GET /api/read/response`, `POST /api/collect/report`.

Для выполнения задач используется `subprocess`; `--test-mode`
отключает фактическое вычисление. Вторая стадия хранит данные в памяти.

```cmd
python -m src.server --test-mode
python -m pytest tests -v
python -m coverage run --branch -m pytest tests/test_mbt.py
python -m coverage report -m
```

В `src/client.py` реализованы методы клиента с теми же именами,
что у `DataModel`. MBT запускается через `RuleBasedStateMachine`.

## Этап 3. TinyDB

Данные можно сохранять в файл с помощью документ-ориентированной СУБД
TinyDB. Интерфейс `DataModel` не меняется: слой хранения заменяется
`TinyDBRepository` с методами `save`, `read`, `collect`, `close`.

```cmd
python -m pip install -r requirements.txt
python -m src.server --backend tinydb --db data/variant23.json
```

## Тестирование

Сценарии MBT для памяти и TinyDB находятся в `tests/test_mbt.py`.
Для отчёта о покрытии ветвей:

```cmd
python -m coverage run --branch -m pytest tests/test_mbt.py -v
python -m coverage report -m
python -m coverage html
```

Откройте `htmlcov/index.html`, чтобы увидеть отчёт покрытия.
Численный результат покрытия необходимо получить при реальном запуске;
в документации он заранее не заявляется.

## Формула отчёта (23)

Выполняется объединение `Member`, `Task` и `Response`,
фильтрация ответов за последние 9 минут и проекция полей
`Member.ip`, `Response.duration`, `Task.tags`.

## Сдача

Опубликовать публичный Git-репозиторий с коммитами для всех этапов.
Распечатать страницу README в PDF через браузер (Ctrl+P)
и предоставить в СДО PDF и URL-адрес репозитория.

**Ограничение:** вычислительная задача — демонстрационная; требуется
замена в соответствии с темой курсовой работы.
