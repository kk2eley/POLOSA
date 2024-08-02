# Используем официальный образ Python
FROM python:3.10-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /usr/src/app

# Копируем файлы requirements.txt и устанавливаем зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY . ./

# Запускаем бота
CMD ["python", "bot.py"]
