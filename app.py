import logging
import os
import random
from pathlib import Path

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils.file_utils import get_unique_name

# Настройка логирования
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="[{asctime}] - {levelname}: {message}",
    style="{",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)

# Константы
IMAGE_DIR = Path("images")
IMAGE_DIR.mkdir(exist_ok=True)

TEMPLATES_DIR = "templates"
STATIC_PATHS = [
    ("/images", IMAGE_DIR),
    ("/templates/css", f"{TEMPLATES_DIR}/css"),
    ("/templates/page_pics", f"{TEMPLATES_DIR}/page_pics"),
    ("/templates/js", f"{TEMPLATES_DIR}/js")
]

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/gif"]
RANDOM_PICS = [
    "/templates/page_pics/cat.png",
    "/templates/page_pics/bird.png",
    "/templates/page_pics/dog.png",
]

# Инициализация приложения
app = FastAPI()

# Подключение статики
for url_path, directory in STATIC_PATHS:
    app.mount(url_path, StaticFiles(directory=directory), name=directory)

templates = Jinja2Templates(directory=TEMPLATES_DIR)


# Главная страница
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    logging.info("Открыта главная страница")
    selected_image_url = random.choice(RANDOM_PICS)
    return templates.TemplateResponse("index.html", {"request": request, "random_image_url": selected_image_url})


# Страница загрузки
@app.get("/upload", response_class=HTMLResponse)
async def upload_img(request: Request):
    logging.info("Открыта страница загрузки")
    return templates.TemplateResponse("upload.html", {"request": request})


# Обработка загрузки
@app.post("/upload")
async def upload_image(request: Request, file: UploadFile = File(...)):
    logging.info("Загрузка файла")

    if file.content_type not in ALLOWED_MIME_TYPES:
        error = "Недопустимый тип файла. Разрешены: {}.".format(
            ", ".join(t.split("/")[1] for t in ALLOWED_MIME_TYPES))
        logging.error(error)
        return templates.TemplateResponse("upload.html", {
            "request": request,
            "error": error
        })

    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE_BYTES:
        error = f"Файл превышает размер {MAX_FILE_SIZE_BYTES / (1024 * 1024)}MB."
        logging.error(error)
        return templates.TemplateResponse("upload.html", {
            "request": request,
            "error": error
        })

    new_filename = get_unique_name(Path(file.filename))
    file_path = IMAGE_DIR / new_filename

    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
        logging.info(f"Файл сохранён: {file_path}")
    except Exception as e:
        logging.error(f"Ошибка сохранения файла: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сохранения файла.")

    image_url = f"{str(request.base_url)}{IMAGE_DIR}/{new_filename}"
    return templates.TemplateResponse("upload.html", {"request": request, "image_url": image_url})


# Галерея изображений
@app.get("/images", response_class=HTMLResponse)
async def list_images(request: Request):
    logging.info("Открыта галерея")
    images = [
        {"name": f, "url": f"/images/{f}"}
        for f in os.listdir(IMAGE_DIR)
        if f.lower().endswith((".png", ".jpg", ".gif")) and (IMAGE_DIR / f).is_file()
    ]
    images.sort(key=lambda x: x["name"].lower())
    return templates.TemplateResponse("images.html", {"request": request, "images": images})


# Удаление изображения
@app.delete("/delete-image/{filename}")
async def delete_image(filename: str):
    file_path = IMAGE_DIR / filename

    if not file_path.exists():
        logging.error("Файл не найден")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден.")

    if not os.path.commonprefix([file_path.resolve(), IMAGE_DIR.resolve()]) == str(IMAGE_DIR.resolve()):
        logging.error("Недопустимый путь к файлу")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недопустимый путь к файлу.")

    try:
        file_path.unlink()
        logging.info(f"Файл удалён: {filename}")
        return {"message": f"Файл {filename} успешно удалён."}
    except Exception as e:
        logging.error(f"Ошибка удаления файла: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка удаления файла.")


# Запуск
if __name__ == '__main__':
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
