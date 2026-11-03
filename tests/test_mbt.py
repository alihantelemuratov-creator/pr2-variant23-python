"""MBT: RuleBasedStateMachine из hypothesis."""

import json
from threading import Thread

from hypothesis import settings
from hypothesis.stateful import RuleBasedStateMachine, initialize, rule
from hypothesis.strategies import integers

from src.client import APIClient
from src.model import DataModel, MemoryRepository
from src.server import make_server


class APIMachine(RuleBasedStateMachine):
    """Сравнить ответы API с ожидаемыми свойствами."""

    @initialize()
    def start(self):
        """Создать тестовый HTTP-сервер."""
        self.server = make_server(
            "127.0.0.1", 0, DataModel(MemoryRepository()), True
        )
        self.thread = Thread(
            target=self.server.serve_forever, daemon=True
        )
        self.thread.start()
        self.client = APIClient(
            f"http://127.0.0.1:{self.server.server_port}"
        )
        self.client.save_member(1)

    @rule(uid=integers(min_value=1, max_value=50))
    def member(self, uid):
        """Генерировать участника."""
        created = self.client.save_member(uid)
        assert self.client.read_member(uid) == created
        assert created in self.client.collect_member()

    @rule(uid=integers(min_value=1, max_value=50))
    def task(self, uid):
        """Генерировать задачу и проверить ответ."""
        task = self.client.save_task(
            uid, 1, json.dumps({"numbers": [uid, 2]})
        )
        assert self.client.read_task(uid) == task
        assert task in self.client.collect_task(1)
        responses = self.client.collect_response(uid)
        assert responses
        for response in responses:
            assert self.client.read_response(response["uid"]) == response
        assert isinstance(self.client.collect_report(), list)

    def teardown(self):
        """Остановить HTTP-сервер."""
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()


TestAPI = APIMachine.TestCase
TestAPI.settings = settings(max_examples=10, stateful_step_count=5)
