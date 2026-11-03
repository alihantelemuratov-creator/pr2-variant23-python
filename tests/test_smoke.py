"""Проверить основные операции HTTP API."""

import json
from threading import Thread

import pytest

from src.client import APIClient
from src.model import DataModel, MemoryRepository
from src.server import make_server


@pytest.fixture
def api_url():
    """Запустить локальный тестовый сервер."""
    server = make_server(
        "127.0.0.1", 0, DataModel(MemoryRepository()), test_mode=True
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_member_api(api_url):
    """Проверить добавление и чтение Member."""
    api = APIClient(api_url)
    result = api.save_member(10)
    assert result["uid"] == 10
    assert api.read_member(10)["uid"] == 10
    assert len(api.collect_member()) == 1


def test_task_api(api_url):
    """Проверить работу Task и Response."""
    api = APIClient(api_url)
    api.save_member(1)
    task = api.save_task(20, 1, json.dumps({"numbers": [1, 2]}))
    assert task["uid"] == 20
    assert api.read_task(20)["uid"] == 20
    assert len(api.collect_task(1)) == 1
    response = api.collect_response(20)[0]
    assert api.read_response(response["uid"]) == response
    assert len(api.collect_report()) == 1
