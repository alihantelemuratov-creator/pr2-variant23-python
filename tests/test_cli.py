"""Проверка CLI, этап 1."""

from pathlib import Path

from src.computation import calculate, process_file


def test_calculate():
    """Сумма, количество и среднее."""
    result = calculate({"numbers": [1, 2, 3]})
    assert result["count"] == 3
    assert result["sum"] == 6
    assert result["average"] == 2


def test_four_examples():
    """Выполнить все четыре файла, предусмотренные заданием."""
    folder = Path(__file__).resolve().parent.parent / "examples"
    assert all(process_file(folder / f"input{i}.json")
               for i in range(1, 5))
