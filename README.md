# text_extractor_service

Сервис для извлечения текста со страницы.
Сначала пытается скачать её через `httpx`, а при ошибке
переходит на `undetected_chromedriver` с подменой заголовков
и `User-Agent` при помощи `fake-headers` и `fake-useragent`.

## Запуск

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Пример запроса

```bash
curl -X POST http://localhost:8000/extract \
     -H 'Content-Type: application/json' \
     -d '{"url": "https://example.com"}'
```
