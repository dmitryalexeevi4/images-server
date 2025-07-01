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

logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
log_file = logs_dir / "app.log"

logging.basicConfig(
    level=logging.ERROR,
    format="[{asctime}] - {levelname}: {message}",
    style="{",
    handlers=[
        logging.FileHandler(log_file, mode="a", encoding="utf-8"),
        logging.StreamHandler(),
    ]
)

app = FastAPI()

image_dir = Path("images")
image_dir.mkdir(exist_ok=True)

app.mount("/images", StaticFiles(directory=image_dir), name="images")
app.mount("/templates/css", StaticFiles(directory="templates/css"), name="templates/css")
app.mount("/templates/page_pics", StaticFiles(directory="templates/page_pics"), name="templates/page_pics")
app.mount("/templates/js", StaticFiles(directory="templates/js"), name="templates/js")

templates = Jinja2Templates(directory="templates")

# Константы для валидации
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/gif"]

RANDOM_PICS = [
    "/templates/page_pics/cat.png",
    "/templates/page_pics/bird.png",
    "/templates/page_pics/dog.png",
]


# Маршрут для главной страницы
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Случайно выбираем изображение из списка
    selected_image_url = random.choice(RANDOM_PICS)
    # Передаем выбранное изображение в шаблон index.html
    return templates.TemplateResponse("index.html", {"request": request, "random_image_url": selected_image_url})


@app.get("/upload", response_class=HTMLResponse)
async def upload_img(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    # 1. Валидация MIME-типа
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип файла. Разрешены только {', '.join(t.split('/')[1] for t in ALLOWED_MIME_TYPES)}."
        )

    # 2. Валидация размера файла
    file_content = await file.read()  # Читаем весь файл в память для проверки размера
    if len(file_content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Размер файла превышает {MAX_FILE_SIZE_BYTES / (1024 * 1024)}MB."
        )

    # 3. Сохранение файла, если валидация пройдена
    new_filename = get_unique_name(Path(file.filename))
    file_location = os.path.join(image_dir, new_filename)
    try:
        with open(file_location, "wb") as f:
            f.write(file_content)  # Записываем прочитанный контент
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось сохранить файл.")

    save_path = image_dir / new_filename
    return {'message': f'Файл {file.filename} получен\n Сохраним в {save_path}'}


# Маршрут для страницы галереи изображений
@app.get("/images", response_class=HTMLResponse)
async def list_images(request: Request):
    images_data = []
    for filename in os.listdir(image_dir):
        file_path = os.path.join(image_dir, filename)
        # Проверяем, что это файл и что его расширение соответствует изображению
        if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.gif')):
            image_url = f"/{image_dir}/{filename}"
            images_data.append({
                "name": filename,
                "url": image_url,
            })

    images_data.sort(key=lambda x: x['name'].lower())  # Сортируем по имени

    # images.html - шаблон для галереи
    return templates.TemplateResponse("images.html", {"request": request, "images": images_data})


# Маршрут для удаления файла
@app.delete("/delete-image/{filename}")
async def delete_image_endpoint(filename: str):
    file_path = os.path.join(image_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден.")

    # Дополнительная проверка, чтобы убедиться, что файл находится внутри UPLOAD_DIRECTORY
    if not os.path.commonprefix([os.path.realpath(file_path), os.path.realpath(image_dir)]) == os.path.realpath(
            image_dir):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недопустимый путь к файлу.")

    try:
        os.remove(file_path)
        return {"message": f"Файл {filename} успешно удален."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Не удалось удалить файл: {e}")


if __name__ == '__main__':
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
