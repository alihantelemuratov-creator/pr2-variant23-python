"""CLI: прочитать входной файл и вывести JSON в stdout."""

import argparse
import json
import sys

from src.computation import process_file


def main(argv=None):
    """Запустить вычисление по пути к входному файлу."""
    parser = argparse.ArgumentParser(description="Вычисления: ПР2, №23")
    parser.add_argument("file", help="Путь к файлу JSON")
    args = parser.parse_args(argv)
    try:
        result = process_file(args.file)
    except (OSError, ValueError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
