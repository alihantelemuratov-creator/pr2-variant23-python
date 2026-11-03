"""HTTP API на BaseHTTPRequestHandler, вариант №23."""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from time import monotonic
from urllib.parse import parse_qs, urlsplit

from src.model import DataModel, MemoryRepository, TinyDBRepository


ROUTES = (
    ("PUT", r"/api/save/member/(?P<uid>\d+)", "save_member"),
    ("POST", r"/api/collect/member", "collect_member"),
    ("GET", r"/api/read/member", "read_member"),
    ("PUT", r"/api/save/task/(?P<uid>\d+)", "save_task"),
    ("POST", r"/api/collect/task/(?P<member>\d+)", "collect_task"),
    ("GET", r"/api/read/task", "read_task"),
    ("POST", r"/api/collect/response/(?P<task>\d+)", "collect_response"),
    ("GET", r"/api/read/response", "read_response"),
    ("POST", r"/api/collect/report", "collect_report"),
)


class APIHandler(BaseHTTPRequestHandler):
    """Проверять заголовки и запускать действия модели."""

    model = None
    test_mode = False

    def log_message(self, format_string, *args):
        """Не печатать служебные сообщения."""

    def do_GET(self):
        """Обработать GET."""
        self._handle("GET")

    def do_POST(self):
        """Обработать POST."""
        self._handle("POST")

    def do_PUT(self):
        """Обработать PUT."""
        self._handle("PUT")

    def _send_json(self, data, status=200):
        """Отправить JSON."""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle(self, method):
        """Выбрать маршрут после проверки заголовков."""
        if self.headers.get("Accept") != "text/json":
            self._send_json({"error": "Нужен Accept: text/json"}, 406)
            return
        if self.headers.get("Accept-Language") != "ru":
            self._send_json({"error": "Нужен Accept-Language: ru"}, 406)
            return
        parsed = urlsplit(self.path)
        params = {
            key: values[0] for key, values in parse_qs(parsed.query).items()
        }
        for http_method, pattern, action in ROUTES:
            matched = re.fullmatch(pattern, parsed.path)
            if http_method == method and matched is not None:
                self._call(action, params, matched.groupdict())
                return
        self._send_json({"error": "Маршрут не найден"}, 404)

    def _call(self, action, params, path_vars):
        """Вызвать обработчик и вернуть его данные."""
        try:
            result = getattr(self, "_api_" + action)(params, path_vars)
        except (ValueError, TypeError, KeyError) as exc:
            self._send_json({"error": str(exc)}, 400)
            return
        self._send_json({"data": result})

    def _api_save_member(self, params, path_vars):
        """Создать участника."""
        return self.model.save_member(
            uid=int(path_vars["uid"]),
            ip=params.get("ip", "127.0.0.1"),
            locale=params.get("locale", "ru"),
            datetime_value=_optional_int(params, "datetime"),
        )

    def _api_collect_member(self, params, path_vars):
        """Найти участников."""
        filters = {
            key: int(value) if key in ("uid", "datetime") else value
            for key, value in params.items()
            if key in ("uid", "datetime", "ip", "locale")
        }
        return self.model.collect_member(**filters)

    def _api_read_member(self, params, path_vars):
        """Прочитать участника."""
        return self.model.read_member(int(params["uid"]))

    def _api_save_task(self, params, path_vars):
        """Создать и запустить задачу."""
        task = self.model.save_task(
            uid=int(path_vars["uid"]),
            member=int(params["member"]),
            task_input=params["input"],
            tags=params.get("tags", ""),
            date=_optional_int(params, "datetime"),
        )
        self._execute(task)
        return self.model.read_task(task["uid"])

    def _api_collect_task(self, params, path_vars):
        """Найти задачи."""
        filters = {
            key: params[key] for key in ("tags",) if key in params
        }
        return self.model.collect_task(int(path_vars["member"]), **filters)

    def _api_read_task(self, params, path_vars):
        """Прочитать задачу."""
        return self.model.read_task(int(params["uid"]))

    def _api_collect_response(self, params, path_vars):
        """Найти результаты задачи."""
        return self.model.collect_response(int(path_vars["task"]))

    def _api_read_response(self, params, path_vars):
        """Прочитать результат."""
        return self.model.read_response(int(params["uid"]))

    def _api_collect_report(self, params, path_vars):
        """Построить отчёт."""
        return self.model.collect_report()

    def _execute(self, task):
        """Запустить вычисление либо тестовую заглушку."""
        if self.test_mode:
            self.model.finish_task(
                task["uid"], "Тестовый режим", "mock", "", 0, False
            )
            return
        started = monotonic()
        output, status, failure = _run_cli(task["input"])
        duration = max(0, int((monotonic() - started) * 1000))
        self.model.finish_task(
            task["uid"], output, status, failure, duration, True
        )


def _optional_int(params, key):
    """Прочитать целочисленный параметр."""
    return int(params[key]) if key in params else None


def _run_cli(source):
    """Запустить CLI через subprocess с временным файлом."""
    filename = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", delete=False
        ) as handle:
            handle.write(source)
            filename = handle.name
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", filename],
            capture_output=True, text=True, encoding="utf-8",
            timeout=15, check=False,
        )
        status = "ok" if result.returncode == 0 else "failed"
        return result.stdout.strip(), status, result.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return "", "failed", str(exc)
    finally:
        if filename and os.path.exists(filename):
            os.unlink(filename)


def make_server(host, port, model, test_mode=False):
    """Создать сервер для заданной модели."""
    handler = type(
        "Variant23Handler", (APIHandler,),
        {"model": model, "test_mode": test_mode},
    )
    return ThreadingHTTPServer((host, port), handler)


def main(argv=None):
    """Запустить HTTP API с хранением в памяти."""
    parser = argparse.ArgumentParser(description="HTTP API варианта №23")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--backend", choices=("memory", "tinydb"),
                        default="memory")
    parser.add_argument("--db", default="data/variant23.json")
    args = parser.parse_args(argv)
    if args.backend == "tinydb":
        Path(args.db).parent.mkdir(parents=True, exist_ok=True)
        repo = TinyDBRepository(args.db)
    else:
        repo = MemoryRepository()
    server = make_server(
        args.host, args.port, DataModel(repo), args.test_mode
    )
    print(f"Сервер: http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Сервер остановлен")
    finally:
        server.server_close()
        repo.close()


if __name__ == "__main__":
    main()
