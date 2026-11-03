"""Хранение Member, Task и Response в памяти (этап 2)."""

from datetime import datetime, timezone


def utc_seconds():
    """Получить время UTC в секундах."""
    return int(datetime.now(timezone.utc).timestamp())


class MemoryRepository:
    """Слой данных для этапа 2."""

    def __init__(self):
        self.records = {name: {} for name in ("Member", "Task", "Response")}

    def save(self, table, item):
        """Записать объект."""
        self.records[table][item["uid"]] = dict(item)
        return dict(item)

    def read(self, table, uid):
        """Прочитать объект по UID."""
        item = self.records[table].get(uid)
        return dict(item) if item else None

    def collect(self, table, **criteria):
        """Найти объекты по полям."""
        values = sorted(self.records[table].values(), key=lambda x: x["uid"])
        return [
            dict(item) for item in values
            if all(item.get(key) == value for key, value in criteria.items())
        ]

    def close(self):
        """Хранилище в памяти не требует закрытия."""


class DataModel:
    """Операции модели данных с названиями методов API-клиента."""

    def __init__(self, repository):
        self.repository = repository

    def save_member(self, uid, ip, locale, datetime_value=None):
        """Создать участника."""
        item = {
            "uid": uid,
            "datetime": utc_seconds() if datetime_value is None
            else datetime_value,
            "ip": ip,
            "locale": locale,
        }
        return self.repository.save("Member", item)

    def collect_member(self, **criteria):
        """Найти участников."""
        return self.repository.collect("Member", **criteria)

    def read_member(self, uid):
        """Прочитать участника."""
        return self.repository.read("Member", uid)

    def save_task(self, uid, member, task_input, tags="", date=None):
        """Создать вычислительную задачу."""
        if self.read_member(member) is None:
            raise ValueError("Участник с таким member не найден")
        item = {
            "uid": uid,
            "datetime": utc_seconds() if date is None else date,
            "input": task_input,
            "member": member,
            "tags": tags,
            "completed": 0,
            "launched": 0,
        }
        return self.repository.save("Task", item)

    def finish_task(self, uid, response, status, failure, duration, run):
        """Записать результат вычисления."""
        task = self.read_task(uid)
        task["completed"] = int(status == "ok")
        task["launched"] = int(run)
        self.repository.save("Task", task)
        existing = self.repository.collect("Response")
        next_uid = max((r["uid"] for r in existing), default=0) + 1
        item = {
            "uid": next_uid,
            "datetime": utc_seconds(),
            "response": response,
            "status": status,
            "failure": failure,
            "task": uid,
            "duration": duration,
        }
        return self.repository.save("Response", item)

    def collect_task(self, member, **criteria):
        """Найти задачи участника."""
        return self.repository.collect("Task", member=member, **criteria)

    def read_task(self, uid):
        """Прочитать задачу."""
        return self.repository.read("Task", uid)

    def collect_response(self, task):
        """Найти результаты задачи."""
        return self.repository.collect("Response", task=task)

    def read_response(self, uid):
        """Прочитать результат."""
        return self.repository.read("Response", uid)

    def collect_report(self):
        """Построить отчёт по формуле (23)."""
        threshold = utc_seconds() - 9 * 60
        rows = []
        for response in self.repository.collect("Response"):
            if response["datetime"] <= threshold:
                continue
            task = self.read_task(response["task"])
            if task is None:
                continue
            member = self.read_member(task["member"])
            if member is not None:
                rows.append({
                    "ip": member["ip"],
                    "duration": response["duration"],
                    "tags": task["tags"],
                })
        return rows
