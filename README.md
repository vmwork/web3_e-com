# Digital Products E-commerce Platform (MVP) 🚀

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=Python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=FastAPI)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=PostgreSQL)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-✓-blue?logo=Docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

Современная платформа для продажи цифровых продуктов (MVP). Поддерживает два способа авторизации: **Web3 (криптокошелёк)** и **Email + пароль**. Полноценная система управления продуктами, заказами, отзывами и скачиваниями.

---

## 📋 Содержание

- [Особенности](#-особенности)
- [Технологический стек](#-технологический-стек)
- [Архитектура проекта](#-архитектура-проекта)
- [Быстрый старт](#-быстрый-старт)
- [Спецификация API](#-спецификация-api)
- [Тестовые данные](#-тестовые-данные)
- [Документация](#-документация)
- [Разработчик](#-разработчик)

---

## ✨ Особенности

### 🔐 Аутентификация
- **Web3** — вход через криптокошелёк (MetaMask/WalletConnect) с проверкой подписи
- **Email** — регистрация и вход по email + пароль (bcrypt хеширование)
- **JWT токены** — безопасная авторизация с истечением срока действия
- **OAuth2** — стандартная форма авторизации в Swagger UI

### 🛍️ Основной функционал
- **Продукты** — CRUD для цифровых товаров (только админ)
- **Категории** — иерархическая структура товаров
- **Заказы** — создание, отслеживание статуса, история
- **Отзывы** — оценка продуктов с модерацией
- **Скачивания** — безопасная выдача файлов по одноразовым токенам
- **Профили** — настройка пользовательских данных
- **Админ-панель** — управление всеми сущностями

### 🗄️ База данных
- **UUID v7** — временнáя упорядоченность для высокой производительности
- **Миграции** — автоматическое применение через Alembic
- **Seed-данные** — автоматическое наполнение тестовыми данными

---

## 🛠️ Технологический стек

| Компонент | Технология |
|-----------|------------|
| **Язык** | Python 3.12 |
| **Фреймворк** | FastAPI 0.115.6 |
| **ORM** | SQLAlchemy 2.0.36 |
| **База данных** | PostgreSQL 15 |
| **Миграции** | Alembic 1.14.1 |
| **Аутентификация** | JWT (python-jose) + bcrypt (passlib) |
| **Web3** | eth-account, eth-keys |
| **Валидация** | Pydantic 2.10.4 |
| **Контейнеризация** | Docker + Docker Compose |
| **Сервер** | Uvicorn 0.34.0 |

---

## 🏗️ Архитектура проекта

```text
web3_e-com/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── auth.py              # Web3 + Email аутентификация
│   │           ├── users.py             # Управление пользователями
│   │           ├── profiles.py          # Профили пользователей
│   │           ├── user_configs.py      # Настройки интерфейса
│   │           ├── categories.py        # Категории продуктов
│   │           ├── products.py          # CRUD продуктов (админ)
│   │           ├── orders.py            # Заказы и статусы
│   │           ├── reviews.py           # Отзывы с модерацией
│   │           └── downloads.py         # Скачивание файлов по токенам
│   ├── core/
│   │   ├── config.py                    # Настройки приложения
│   │   ├── security.py                  # JWT, хеширование, Web3 подписи
│   │   └── dependencies.py              # Зависимости (get_current_user)
│   ├── models/                          # SQLAlchemy модели
│   │   ├── user.py
│   │   ├── user_config.py
│   │   ├── profile.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   ├── review.py
│   │   └── download_token.py
│   ├── schemas/                         # Pydantic схемы (DTO)
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── utils/
│   │   └── uuid_utils.py                # Генератор UUID v7
│   ├── seed.py                          # Наполнение БД тестовыми данными
│   ├── main.py                          # Точка входа FastAPI
│   └── deploy.sh                        # Скрипт деплоя в Docker
├── alembic/                             # Миграции БД
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
└── README.md

⚡ Быстрый старт
1️⃣ Клонирование репозитория
bash
git clone 
cd web3_e-com
2️⃣ Настройка окружения
Создайте файл .env на основе примера:

env
# === Настройки контейнеров ===
POSTGRES_USER=crypto_user
POSTGRES_PASSWORD=crypto_secure_pass
POSTGRES_DB=crypto_db_api
POSTGRES_SERVER=crypto_postgres
POSTGRES_PORT=5432

# === Строка подключения к БД внутри Docker ===
DATABASE_URL=postgresql://crypto_user:crypto_secure_pass@crypto_postgres:5432/crypto_db_api

# === Параметры JWT ===
SECRET_KEY=supersecretkeychangeit_crypto_auth_992183
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# === Web3 Админ ===
ADMIN_WALLET_ADDRESS=0x90F8bf6A479f320ced073E5743F257356671B414
3️⃣ Запуск через Docker
bash
docker-compose up --build
📦 При первом запуске автоматически:

Создаются таблицы в PostgreSQL

Применяются миграции Alembic

Загружаются тестовые данные (админ, категории, продукты)

4️⃣ Локальный запуск (без Docker)
bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Запустить приложение
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
Приложение будет доступно по адресу: http://localhost:8000

🔐 Тестовые данные
После запуска в базе автоматически создаются:

Тип	Email / Кошелёк	Пароль	Роль
Админ (Web3)	0x90F8bf6A479f320ced073E5743F257356671B414	-	admin
Админ (Email)	admin@example.com	admin123	admin
Пользователь	user@example.com	user123	user
⚠️ В продакшене обязательно смените тестовые пароли и SECRET_KEY!

📋 Спецификация API
🔑 Аутентификация
Метод	Эндпоинт	Описание	Доступ
POST	/api/v1/auth/connect	Вход через Web3 (криптокошелёк)	Публичный
POST	/api/v1/auth/register	Регистрация по email + пароль	Публичный
POST	/api/v1/auth/login	Вход по email + пароль	Публичный
POST	/api/v1/auth/token	OAuth2 эндпоинт для Swagger	Публичный
POST	/api/v1/auth/logout	Выход из системы	Авторизованный
GET	/api/v1/auth/me	Информация о текущем пользователе	Авторизованный
POST	/api/v1/auth/connect/wallet	Привязка кошелька к email-аккаунту	Авторизованный
DELETE	/api/v1/auth/connect/wallet	Отвязка кошелька от аккаунта	Авторизованный
👤 Пользователи
Метод	Эндпоинт	Описание	Доступ
GET	/api/v1/users/me	Профиль текущего пользователя	Авторизованный
PUT	/api/v1/users/me	Обновление профиля	Авторизованный
PUT	/api/v1/users/me/password	Смена пароля	Авторизованный
📂 Профили и настройки
Метод	Эндпоинт	Описание	Доступ
GET	/api/v1/profiles/me	Получить профиль	Авторизованный
PUT	/api/v1/profiles/me	Обновить профиль	Авторизованный
GET	/api/v1/configs/me	Получить настройки	Авторизованный
PUT	/api/v1/configs/me	Обновить настройки	Авторизованный
📦 Категории
Метод	Эндпоинт	Описание	Доступ
GET	/api/v1/categories/	Список категорий	Публичный
GET	/api/v1/categories/{id}	Категория по ID	Публичный
POST	/api/v1/categories/	Создать категорию	Только админ
PUT	/api/v1/categories/{id}	Обновить категорию	Только админ
DELETE	/api/v1/categories/{id}	Удалить категорию	Только админ
🛍️ Продукты
Метод	Эндпоинт	Описание	Доступ
GET	/api/v1/products/	Список продуктов (с фильтрацией)	Публичный
GET	/api/v1/products/{id}	Детали продукта	Публичный
POST	/api/v1/products/	Создать продукт	Только админ
PUT	/api/v1/products/{id}	Обновить продукт	Только админ
DELETE	/api/v1/products/{id}	Удалить продукт	Только админ
GET	/api/v1/products/admin/all	Все продукты (админ)	Только админ
📋 Заказы
Метод	Эндпоинт	Описание	Доступ
GET	/api/v1/orders/	История заказов	Авторизованный
GET	/api/v1/orders/{id}	Детали заказа	Авторизованный
POST	/api/v1/orders/	Создать заказ	Авторизованный
PUT	/api/v1/orders/{id}	Обновить статус заказа	Авторизованный
GET	/api/v1/orders/admin/all	Все заказы	Только админ
⭐ Отзывы
Метод	Эндпоинт	Описание	Доступ
GET	/api/v1/reviews/products/{id}	Отзывы на продукт	Публичный
POST	/api/v1/reviews/	Создать отзыв	Авторизованный
PUT	/api/v1/reviews/{id}	Обновить отзыв	Автор
DELETE	/api/v1/reviews/{id}	Удалить отзыв	Автор/Админ
GET	/api/v1/reviews/admin/pending	Отзывы на модерации	Только админ
PUT	/api/v1/reviews/admin/{id}/approve	Одобрить отзыв	Только админ
⬇️ Скачивания
Метод	Эндпоинт	Описание	Доступ
POST	/api/v1/downloads/tokens	Создать токен для скачивания	Авторизованный
GET	/api/v1/downloads/files/{token}	Скачать файл по токену	Публичный (с токеном)
GET	/api/v1/downloads/history	История скачиваний	Авторизованный
🛠️ Системные
Метод	Эндпоинт	Описание	Доступ
GET	/	Информация о сервисе	Публичный
GET	/health	Healthcheck	Публичный
📑 Интерактивная документация
После запуска доступны:

Swagger UI: http://localhost:8000/api/docs

ReDoc UI: http://localhost:8000/api/redoc

OpenAPI JSON: http://localhost:8000/api/openapi.json

🐳 Docker-команды
bash
# Сборка и запуск
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d

# Просмотр логов
docker-compose logs -f backend

# Остановка контейнеров
docker-compose down

# Остановка с удалением томов (полная очистка)
docker-compose down -v

# Перезапуск после изменений
docker-compose restart backend

# Вход в контейнер бэкенда
docker exec -it crypto_backend_app /bin/bash
🔧 Переменные окружения (.env)
Переменная	Описание	Пример
POSTGRES_USER	Пользователь PostgreSQL	crypto_user
POSTGRES_PASSWORD	Пароль PostgreSQL	crypto_secure_pass
POSTGRES_DB	Имя базы данных	crypto_db_api
POSTGRES_SERVER	Хост PostgreSQL (в Docker)	crypto_postgres
POSTGRES_PORT	Порт PostgreSQL	5432
DATABASE_URL	Полная строка подключения	postgresql://...
SECRET_KEY	Секретный ключ JWT	supersecretkey...
ACCESS_TOKEN_EXPIRE_MINUTES	Время жизни токена	10080 (7 дней)
ADMIN_WALLET_ADDRESS	Кошелёк админа (Web3)	0x90F8bf...
📄 Лицензия
MIT License — свободно используйте в коммерческих и личных проектах.

👨‍💻 Разработчик
### 🔗 Разработчик: Vladyslav | Senior Fullstack Developer
👉 [Profile on freelancehunt : vmarwork](https://freelancehunt.com)