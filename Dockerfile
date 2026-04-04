FROM python:3.11-slim

WORKDIR /code

# Переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание папки для загрузок и пользователя
RUN mkdir -p /code/app/uploads
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /code
USER appuser

# Запуск
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
