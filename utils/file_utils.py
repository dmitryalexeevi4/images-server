import uuid
from pathlib import Path

ALLOW_EXTENSIONS = [".jpg", ".png", ".gif"]
MAX_FILE_SIZE = 5 * 1024 * 1024


def is_allowed_file(filename: Path) -> bool:
    """Проверяем, есть ли расширение в списке разрешенных."""
    ext = filename.suffix.lower()
    print(ext)
    return ext in ALLOW_EXTENSIONS


def get_unique_name(filename: Path) -> str:
    ext = filename.suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    print(f"{unique_name=}")
    return unique_name
