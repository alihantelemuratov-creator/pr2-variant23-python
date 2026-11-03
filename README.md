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

## Этап 3

Подключение TinyDB в следующем коммите.
