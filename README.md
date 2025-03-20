# Сайт кафе на Django

Этот проект представляет собой сайт кафе с использованием Django.

## Требования

Перед запуском проекта убедиться, что установлен:

- `Python`

На компьютере должна быть база данных mysql:

Заменить значения в `.env` файле на реальные значения:

```
DB_NAME=название базы
DB_USER=пользователь mysql, root по дефолту
DB_PASSWORD=пароль от сервера mysql, который нужно вводить при подключении к серверу mysql
DB_HOST=хост сервера mysql, localhost по дефолту
DB_PORT=порт сервера mysql, 3306 по дефолту
```

## Установка зависимостей для Django:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Выполнить миграции базы данных:

```bash
python manage.py migrate
```
Загрузить данные в базу данных:
```bash
python manage.py loaddata db.json
```

### Запуск Django сервера:

```bash
python manage.py runserver
```

Вход в админку [Админ панель](http://127.0.0.1:8000/admin/)
логин: admin
пароль: 123