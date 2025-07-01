document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const browseButton = document.getElementById('browse-file-button');
    const uploadArea = document.getElementById('upload-area');
    const submitUploadButton = document.getElementById('submit-upload-button');
    const uploadLinkInput = document.querySelector('.upload-link-input');
    const copyButton = document.querySelector('.copy-button');

    const dragText = document.querySelector('.drag-text');
    const supportText = document.querySelector('.support-text');
    const uploadIcon = document.querySelector('.upload-icon svg'); // Для изменения цвета иконки
    const MAX_FILE_SIZE_MB = 5;
    const ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/gif'];

    // Вспомогательная функция для сброса состояния области загрузки
    function resetUploadArea() {
        uploadArea.classList.remove('upload-failed'); // Удаляем класс ошибки, если был
        uploadIcon.style.color = '#007bff'; // Возвращаем синий цвет иконки
        dragText.textContent = 'Select a file or drag and drop here.';
        supportText.innerHTML = `Only support .jpg, .png and .gif.<br>Maximum file size is ${MAX_FILE_SIZE_MB}MB`;
    }

    // 1. Активация скрытого input type="file" при клике на кнопку или область
    browseButton.addEventListener('click', () => {
        fileInput.click();
    });

    uploadArea.addEventListener('click', (event) => {
        if (event.target === uploadArea || uploadArea.contains(event.target)) {
            fileInput.click();
        }
    });

    // 2. Обработка выбора файла и валидация
    fileInput.addEventListener('change', () => {
        resetUploadArea(); // Сбрасываем состояние перед новой валидацией

        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            const fileName = file.name;
            const fileSizeMB = file.size / (1024 * 1024); // Размер в мегабайтах
            const fileType = file.type;

            let isValid = true;
            let errorMessage = '';

            // Валидация по типу файла
            if (!ALLOWED_FILE_TYPES.includes(fileType)) {
                isValid = false;
                errorMessage = 'Upload failed'; // Как на скриншоте
                supportText.innerHTML = `Only support .jpg, .png and .gif.<br>Maximum file size is ${MAX_FILE_SIZE_MB}MB`;
            }

            // Валидация по размеру файла (выполняется только если тип файла уже правильный или независимо)
            if (fileSizeMB > MAX_FILE_SIZE_SIZE_MB) {
                isValid = false;
                errorMessage = 'Upload failed'; // Как на скриншоте
                supportText.innerHTML = `File size exceeds ${MAX_FILE_SIZE_MB}MB.<br>Only support .jpg, .png and .gif.`; // Дополнительное сообщение
            }

            if (isValid) {
                dragText.textContent = `File selected: ${fileName}`;
                supportText.textContent = 'Ready to upload.';
                // Можно здесь автоматически отправить форму или изменить кнопку на "Upload"
                // Например, submitUploadButton.click();
            } else {
                uploadArea.classList.add('upload-failed'); // Добавляем класс для красной рамки/текста
                uploadIcon.style.color = 'red'; // Меняем цвет иконки на красный
                dragText.textContent = errorMessage;
                // supportText уже содержит сообщение об ошибке, установленное выше
                fileInput.value = ''; // Очищаем input, чтобы пользователь мог выбрать другой файл
            }
        } else {
            resetUploadArea(); // Если пользователь отменил выбор файла
        }
    });

    // 3. Функциональность кнопки "COPY"
    if (copyButton && uploadLinkInput) {
        copyButton.addEventListener('click', () => {
            uploadLinkInput.select();
            uploadLinkInput.setSelectionRange(0, 99999);
            document.execCommand("copy");

            const originalText = copyButton.textContent;
            copyButton.textContent = 'Copied!';
            setTimeout(() => {
                copyButton.textContent = originalText;
            }, 2000);
        });
    }

    // 4. Функциональность Drag and Drop и валидация
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        resetUploadArea(); // Сбрасываем состояние перед новой валидацией

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            const fileName = file.name;
            const fileSizeMB = file.size / (1024 * 1024);
            const fileType = file.type;

            let isValid = true;
            let errorMessage = '';

            if (!ALLOWED_FILE_TYPES.includes(fileType)) {
                isValid = false;
                errorMessage = 'Upload failed';
                supportText.innerHTML = `Only support .jpg, .png and .gif.<br>Maximum file size is ${MAX_FILE_SIZE_MB}MB`;
            }

            if (fileSizeMB > MAX_FILE_SIZE_MB) {
                isValid = false;
                errorMessage = 'Upload failed';
                supportText.innerHTML = `File size exceeds ${MAX_FILE_SIZE_MB}MB.<br>Only support .jpg, .png and .gif.`;
            }

            if (isValid) {
                fileInput.files = files; // Передаем перетащенные файлы в input type="file"
                // Теперь можно отобразить имя файла или автоматически отправить
                dragText.textContent = `File selected: ${fileName}`;
                supportText.textContent = 'Ready to upload.';
                // submitUploadButton.click(); // Отправляет форму
            } else {
                uploadArea.classList.add('upload-failed');
                uploadIcon.style.color = 'red';
                dragText.textContent = errorMessage;
                // supportText уже содержит сообщение об ошибке
                fileInput.value = ''; // Очищаем input
            }
        } else {
            resetUploadArea();
        }
    });
});