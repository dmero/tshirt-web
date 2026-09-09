FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home shop && chown -R shop:shop /app
USER shop
EXPOSE 8000
CMD ["sh", "-c", "python manage.py collectstatic --noinput && exec gunicorn tshirt_shop.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --access-logfile -"]
