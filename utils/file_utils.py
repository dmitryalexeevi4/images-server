import uuid
from pathlib import Path


def get_unique_name(filename: Path) -> str:
    ext = filename.suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    print(f"{unique_name=}")
    return unique_name
