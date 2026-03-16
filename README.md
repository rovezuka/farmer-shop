Вот содержимое для файла `README.md` — скопируйте всё что ниже между тройными обратными кавычками:

# 🌾 Фермерская лавка

Клиент-серверное веб-приложение для автоматизации продажи местных фермерских продуктов.

## 📋 Содержание

- [Технологии](#технологии)
- [Предварительные требования](#предварительные-требования)
- [Установка и запуск](#установка-и-запуск)
  - [1. Клонирование репозитория](#1-клонирование-репозитория)
  - [2. Запуск базы данных](#2-запуск-базы-данных)
  - [3. Запуск сервера (Backend)](#3-запуск-сервера-backend)
  - [4. Запуск клиента (Frontend)](#4-запуск-клиента-frontend)
- [Проверка работоспособности](#проверка-работоспособности)
- [Тестовые учётные записи](#тестовые-учётные-записи)
- [API-документация](#api-документация)
- [Структура проекта](#структура-проекта)
- [Полезные команды](#полезные-команды)
- [Возможные проблемы](#возможные-проблемы)
- [Участники](#участники)

---

## Технологии

| Компонент | Технология |
|---|---|
| Backend | Python 3.11+, FastAPI, SQLAlchemy (async), Alembic |
| Frontend | React 18, Vite, Axios, React Router |
| База данных | PostgreSQL 16 |
| Аутентификация | JWT (access + refresh токены) |
| Контейнеризация | Docker, Docker Compose |

---

## Предварительные требования

Перед началом убедитесь, что на вашем компьютере установлены:

- **Python** 3.11 или выше — [скачать](https://www.python.org/downloads/)
- **Node.js** 18 или выше — [скачать](https://nodejs.org/)
- **Docker** и **Docker Compose** — [скачать](https://www.docker.com/products/docker-desktop/)
- **Git** — [скачать](https://git-scm.com/downloads)

Проверка установки:

```bash
python --version    # Python 3.11+
node --version      # v18+
npm --version       # 9+
docker --version    # Docker 24+
git --version       # git 2+
```

---

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/<ваш-username>/farmer-shop.git
cd farmer-shop
```

### 2. Запуск базы данных

#### Вариант А: Через Docker (рекомендуется)

```bash
# Убедитесь что порт 5432 свободен
# Если локальный PostgreSQL запущен — остановите его:
# Linux:   sudo systemctl stop postgresql
# macOS:   brew services stop postgresql
# Windows: net stop postgresql-x64-16

# Запуск контейнера с PostgreSQL
docker-compose up -d

# Проверка что контейнер работает
docker ps

# Проверка подключения
docker exec -it farmer-db psql -U farmer_user -d farmer_db -c "SELECT 1;"
```

Должно вывести:

```
 ?column?
----------
        1
(1 row)
```

#### Вариант Б: Локальный PostgreSQL

Если у вас уже установлен PostgreSQL:

```bash
# Подключитесь как суперпользователь
psql -U postgres

# Выполните:
CREATE USER farmer_user WITH PASSWORD 'farmer_pass';
CREATE DATABASE farmer_db OWNER farmer_user;
GRANT ALL PRIVILEGES ON DATABASE farmer_db TO farmer_user;
\q
```

> **Важно:** если локальный PostgreSQL работает на порту 5432, а вы хотите использовать Docker — измените порт в `docker-compose.yml` на `5433:5432` и в `server/.env` укажите `DB_PORT=5433`.

### 3. Запуск сервера (Backend)

Откройте **первый терминал**:

```bash
# Перейдите в папку сервера
cd server

# Создайте виртуальное окружение
python -m venv venv

# Активируйте его:
# macOS / Linux:
source venv/bin/activate
# Windows (cmd):
venv\Scripts\activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Установите зависимости
pip install -r requirements.txt

# Создайте файл переменных окружения
cp .env.example .env
```

Проверьте что файл `server/.env` содержит правильные данные:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=farmer_db
DB_USER=farmer_user
DB_PASSWORD=farmer_pass
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=true
```

Продолжите настройку:

```bash
# Примените миграции базы данных
alembic upgrade head

# Загрузите тестовые данные
python -m app.db.seed
# Должно вывести: ✅ Тестовые данные успешно загружены!

# Запустите сервер
uvicorn app.main:app --reload --port 8000
```

Сервер запустится на http://localhost:8000

> ⚠️ **Не закрывайте этот терминал!** Сервер должен работать постоянно.

### 4. Запуск клиента (Frontend)

Откройте **второй терминал**:

```bash
# Перейдите в папку клиента
cd client

# Установите зависимости
npm install

# Запустите в режиме разработки
npm run dev
```

Клиент запустится на http://localhost:5173

> ⚠️ **Не закрывайте этот терминал!** Клиент должен работать постоянно.

---

## Проверка работоспособности

### Открытие в браузере

| URL | Что откроется |
|---|---|
| http://localhost:5173 | Фронтенд (React) |
| http://localhost:8000/docs | Swagger UI (документация API) |
| http://localhost:8000/redoc | ReDoc (альтернативная документация) |
| http://localhost:8000/health | Проверка здоровья сервера |

### Быстрая проверка API через терминал

```bash
# Проверка здоровья сервера
curl http://localhost:8000/health
# Ответ: {"status":"ok"}

# Получение списка товаров
curl http://localhost:8000/api/v1/products
# Ответ: {"items":[...],"total":6,"page":1,"per_page":12}

# Регистрация нового покупателя
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "newuser@test.com",
    "password": "test123456",
    "role": "customer",
    "first_name": "Иван",
    "phone": "+79001234567"
  }'
# Ответ: {"access_token":"eyJ...","refresh_token":"eyJ...","role":"customer",...}
```

---

## Тестовые учётные записи

После выполнения `python -m app.db.seed` доступны следующие аккаунты:

| Роль | Email | Пароль |
|---|---|---|
| Администратор | admin@ferma.ru | admin123 |
| Фермер 1 | ivanov@ferma.ru | farmer123 |
| Фермер 2 | petrova@ferma.ru | farmer123 |
| Покупатель | buyer@example.com | buyer123 |

### Вход через API

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email": "buyer@example.com", "password": "buyer123"}'
```

---

## API-документация

После запуска сервера документация доступна автоматически:

- **Swagger UI** (интерактивная): http://localhost:8000/docs
- **ReDoc** (читаемая): http://localhost:8000/redoc

### Основные эндпоинты

| Метод | URL | Описание | Авторизация |
|---|---|---|---|
| POST | /api/v1/auth/register | Регистрация | Нет |
| POST | /api/v1/auth/login | Вход | Нет |
| POST | /api/v1/auth/refresh | Обновление токена | Нет |
| GET | /api/v1/products | Каталог товаров | Нет |
| GET | /api/v1/products/{id} | Детали товара | Нет |
| POST | /api/v1/products | Добавить товар | Фермер |
| PUT | /api/v1/products/{id} | Обновить товар | Фермер |
| DELETE | /api/v1/products/{id} | Удалить товар | Фермер |
| POST | /api/v1/orders | Создать заказ | Покупатель |
| GET | /api/v1/orders/my | Мои заказы | Покупатель |
| GET | /api/v1/orders/farmer | Заказы фермера | Фермер |
| PATCH | /api/v1/orders/{id}/status | Изменить статус | Фермер |
| GET | /api/v1/analytics/sales | Аналитика продаж | Фермер |

---

## Структура проекта

```
farmer-shop/
├── server/                        # Backend (FastAPI)
│   ├── app/
│   │   ├── api/                   # Роутеры (эндпоинты)
│   │   │   ├── auth.py            # Регистрация, вход, JWT
│   │   │   ├── products.py        # CRUD товаров, каталог
│   │   │   ├── orders.py          # Заказы
│   │   │   └── analytics.py       # Аналитика для фермера
│   │   ├── core/                  # Конфигурация
│   │   │   ├── config.py          # Настройки из .env
│   │   │   ├── security.py        # JWT, хеширование паролей
│   │   │   └── dependencies.py    # Зависимости (get_current_user)
│   │   ├── models/                # SQLAlchemy модели (таблицы БД)
│   │   ├── schemas/               # Pydantic модели (валидация)
│   │   ├── services/              # Бизнес-логика
│   │   ├── db/                    # Подключение к БД, seed-данные
│   │   └── main.py                # Точка входа
│   ├── alembic/                   # Миграции БД
│   ├── requirements.txt           # Python-зависимости
│   ├── .env                       # Переменные окружения (НЕ в Git!)
│   └── .env.example               # Шаблон переменных
├── client/                        # Frontend (React)
│   ├── src/
│   │   ├── components/            # UI-компоненты
│   │   ├── pages/                 # Страницы
│   │   ├── services/              # Вызовы API (axios)
│   │   ├── context/               # React Context (авторизация)
│   │   ├── App.jsx                # Маршрутизация
│   │   └── main.jsx               # Точка входа
│   ├── index.html
│   └── package.json
├── database/                      # SQL-скрипты
├── docker-compose.yml             # Docker для PostgreSQL
└── README.md
```

---

## Полезные команды

### База данных

```bash
# Запуск PostgreSQL в Docker
docker-compose up -d

# Остановка
docker-compose down

# Остановка с удалением данных (полный сброс)
docker-compose down -v

# Подключение к БД через psql
docker exec -it farmer-db psql -U farmer_user -d farmer_db

# Просмотр таблиц
docker exec -it farmer-db psql -U farmer_user -d farmer_db -c "\dt"
```

### Сервер

```bash
cd server
source venv/bin/activate

# Запуск
uvicorn app.main:app --reload --port 8000

# Создание новой миграции (после изменения моделей)
alembic revision --autogenerate -m "описание изменений"

# Применение миграций
alembic upgrade head

# Откат последней миграции
alembic downgrade -1

# Перезагрузка тестовых данных
python -m app.db.seed

# Запуск тестов
pytest tests/ -v
```

### Клиент

```bash
cd client

# Запуск в режиме разработки
npm run dev

# Сборка для продакшена
npm run build

# Предпросмотр собранной версии
npm run preview
```

---

## Схема запуска (итого)

```
Терминал 1 (БД):       docker-compose up -d
Терминал 2 (Backend):  cd server && source venv/bin/activate && uvicorn app.main:app --reload --port 8000
Терминал 3 (Frontend): cd client && npm run dev

Браузер:
  → http://localhost:5173      (фронтенд)
  → http://localhost:8000/docs (API-документация)
```

---

## Участники

| Участник | Зона ответственности |
|---|---|
| Участник 1 | БД, модели, миграции, аутентификация |
| Участник 2 | Каталог товаров, заказы, корзина |
| Участник 3 | ЛК фермера, аналитика, админ-панель |
| Участник 4 | Клиентский интерфейс (React) |