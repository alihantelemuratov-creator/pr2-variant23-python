"""Демонстрационная вычислительная задача.

Замените её вычислениями из своей курсовой работы.
"""

import json
from pathlib import Path
from statistics import mean


def calculate(payload):
    """Вычислить статистику числового массива из JSON."""
    numbers = payload.get("numbers")
    if not isinstance(numbers, list) or not numbers:
        raise ValueError("Поле numbers должно быть непустым списком")
    if any(type(number) not in (int, float) for number in numbers):
        raise ValueError("Все элементы numbers должны быть числами")
    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "average": mean(numbers),
        "minimum": min(numbers),
        "maximum": max(numbers),
    }


def process_file(path):
    """Прочитать JSON-файл и вернуть результат вычислений."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Входные данные должны быть объектом JSON")
    return calculate(payload)
