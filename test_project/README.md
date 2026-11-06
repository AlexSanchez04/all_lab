# Менеджер заметок (Go + Python + PostgreSQL)

Учебный веб-проект: фронтенд на **Python (Flask)**, бэкенд-API на **Go**, хранилище — **PostgreSQL**.
Обрабатывает `GET` и `POST` запросы.

## Архитектура

```
Браузер ──GET/POST──> Python/Flask (:5000) ──HTTP──> Go REST API (:8080) ──SQL──> PostgreSQL (:5432)
```

| Слой        | Язык     | Что делает                                 |
|-------------|----------|--------------------------------------------|
| frontend/   | Python   | HTML-страницы, формы; `GET /`, `POST /notes` проксирует в Go |
| backend/    | Go       | `GET /api/notes`, `GET /api/notes/{id}`, `POST /api/notes`, CORS |
| db/         | SQL      | База `notesapp`, таблица `notes`           |

## Запуск

### 1. База данных

Локально (PostgreSQL уже запущен на :5432):

```powershell
$env:PGPASSWORD="postgres"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -w -h localhost -f db\init.sql
```

Либо через Docker (если установлен):

```bash
docker compose up -d
```

### 2. Go backend

```bash
cd backend
go mod tidy
go build -o notes-backend.exe
.\notes-backend.exe
# или: go run .
```

Порт по умолчанию `8080`, строка подключения БД из env `DATABASE_URL`
(`postgres://postgres:postgres@localhost:5432/notesapp`).

### 3. Python frontend

```bash
cd frontend
pip install -r requirements.txt
python app.py
```

Страница: http://localhost:5000

## API Go (примеры)

```bash
# список заметок (GET)
curl http://localhost:8080/api/notes

# создать заметку (POST)
curl -X POST http://localhost:8080/api/notes \
  -H "Content-Type: application/json" \
  -d '{"title":"Привет","content":"Текст"}'

# заметка по id (GET)
curl http://localhost:8080/api/notes/1
```

## Структура

```
backend/            Go REST API (main.go, store.go, model.go)
frontend/           Flask-приложение (app.py, templates/, static/)
db/init.sql         схема БД (создание и инициализация)
docker-compose.yaml PostgreSQL в контейнере (опционально)
```