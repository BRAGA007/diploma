from typing import Any

from app.core.config import settings


def get_openapi_json_example(**kwargs) -> dict[str, Any]:
    return {
        "content": {
            "application/json": {
                "example": kwargs,
            },
        },
    }


def get_openapi_json_no_content_example() -> dict[str, Any]:
    return {
        "content": {
            "No Content": {"example": ""},
        },
    }


def get_openapi_xlsx_file_example() -> dict[str, Any]:
    return {
        "content": {
            settings.excel_content_type: {"example": ""},
        },
    }


def get_openapi_json_examples(examples: dict[str, dict[str, Any]] | list[dict[str, Any]]) -> dict[str, Any]:
    """
    Принимает на вход список или словарь со словарями-примерами.
    Формат примера ответа:

    ..
        {
            "summary": "Название примера (необязательно)",
            "description": "Описание примера (необязательно)",
            "value": {"field1": "example value 1", "field2": 123}, # Тело ответа
        }

    Если передается словарь, можно не заполнять summary, название будет взято из ключа,
    по которому лежит пример в переданном словаре.
    """
    return {
        "content": {
            "application/json": {
                "examples": examples,
            },
        },
    }
