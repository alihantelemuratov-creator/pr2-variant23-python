"""HTTP-клиент варианта 23 с именами методов DataModel."""

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class APIClient:
    """Клиент API на стандартной библиотеке."""

    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Accept": "text/json",
            "Accept-Language": "ru",
        }

    def _request(self, method, path, **params):
        """Отправить запрос и получить поле data."""
        values = {k: v for k, v in params.items() if v is not None}
        query = "?" + urlencode(values) if values else ""
        request = Request(
            self.base_url + path + query,
            headers=self.headers,
            method=method,
        )
        with urlopen(request, timeout=10) as reply:
            return json.loads(reply.read().decode("utf-8"))["data"]

    def save_member(self, uid, ip="127.0.0.1", locale="ru"):
        """Создать участника."""
        return self._request(
            "PUT", f"/api/save/member/{uid}", ip=ip, locale=locale
        )

    def collect_member(self, **criteria):
        """Найти участников."""
        return self._request("POST", "/api/collect/member", **criteria)

    def read_member(self, uid):
        """Прочитать участника."""
        return self._request("GET", "/api/read/member", uid=uid)

    def save_task(self, uid, member, task_input, tags=""):
        """Создать задачу."""
        return self._request(
            "PUT", f"/api/save/task/{uid}",
            member=member, input=task_input, tags=tags,
        )

    def collect_task(self, member, **criteria):
        """Найти задачи участника."""
        return self._request(
            "POST", f"/api/collect/task/{member}", **criteria
        )

    def read_task(self, uid):
        """Прочитать задачу."""
        return self._request("GET", "/api/read/task", uid=uid)

    def collect_response(self, task):
        """Найти ответы."""
        return self._request(
            "POST", f"/api/collect/response/{task}"
        )

    def read_response(self, uid):
        """Прочитать ответ."""
        return self._request("GET", "/api/read/response", uid=uid)

    def collect_report(self):
        """Получить отчёт."""
        return self._request("POST", "/api/collect/report")
