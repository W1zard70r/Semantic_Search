FROM python:3.12-slim

# 1. Устанавливаем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 2. Указываем рабочую директорию
WORKDIR /app

# 3. Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# 4. Устанавливаем зависимости (пропускаем установку самого проекта)
# Мы скачиваем модель в образ, чтобы она не качалась каждый раз при запуске
RUN uv sync --frozen --no-install-project

# 5. Копируем остальной код
COPY . .

# 6. Открываем порт для FastAPI
EXPOSE 8000

# 7. Запускаем сервер
# --host 0.0.0.0 обязателен для работы внутри Docker
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]