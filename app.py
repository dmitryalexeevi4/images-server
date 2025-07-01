import logging
import os
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

app.mount("/templates/css", StaticFiles(directory="templates/css"), name="templates/css")
app.mount("/templates/page_pics", StaticFiles(directory="templates/page_pics"), name="templates/page_pics")
app.mount("/templates/js", StaticFiles(directory="templates/js"), name="templates/js")

templates = Jinja2Templates(directory="templates")

# Константы для валидации
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/gif"]

image_dir = Path("images")
image_dir.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/upload", response_class=HTMLResponse)
async def upload_img(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


# @app.post("/upload/")
# async def upload_img(request: Request, file: UploadFile = File(...)):
#     print(f'Файл получен {file.filename}')
#     my_file = Path(file.filename)
#     if is_allowed_file(my_file):
#         print('Верное расширение')
#     else:
#         logging.error('Выбрали файл с не верным расширением')
#         print('НЕ верное расширение')
#
#     content = await file.read(MAX_FILE_SIZE + 1)
#     size = len(content)
#     if size < MAX_FILE_SIZE:
#         print(f"Длина изображения подходит {size}")
#
#     new_file_name = get_unique_name(my_file)
#     print(f"{new_file_name}")
#
#     image_dir = Path("images")
#     image_dir.mkdir(exist_ok=True)
#     save_path = image_dir / new_file_name
#
#     save_path.write_bytes(content)
#     print(f"Файл {str(save_path)} записан")
#
#     return {'message': f'Файл {file.filename} получен\n Сохраним в {save_path}'}

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

    save_path = image_dir/new_filename
    return {'message': f'Файл {file.filename} получен\n Сохраним в {save_path}'}

# Пробрасываем /static/images/ -> ./images/
app.mount("/static/images", StaticFiles(directory="images"), name="images")


@app.get("/images/", response_class=HTMLResponse)
async def get_images(request: Request):
    images_folder = "images"
    image_files = [
        f"/static/images/{file}"
        for file in os.listdir(images_folder)
        if file.lower().endswith((".jpg", ".png", ".gif"))
    ]
    return templates.TemplateResponse("gallery.html", {"request": request, "images": image_files})


if __name__ == '__main__':
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
