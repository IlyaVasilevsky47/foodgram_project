# Foodgram-project

[![CI](https://github.com/IlyaVasilevsky47/foodgram_project/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/IlyaVasilevsky47/foodgram_project/actions/workflows/main.yml)

Foodgram — это онлайн-платформа и API для хранения и обмена кулинарными рецептами.

## Основные возможности:
1. Регистрация и авторизация пользователей.
2. Пользователи могут создавать, редактировать и добавлять в избранное рецепты, а также подписываться на других пользователей.
3. У каждого пользователя есть список покупок. Когда этот список заполнен, пользователи могут сохранить свои рецепты в текстовом формате.

## Запуск проекта:
1. Клонируем проект
```bash
git clone git@github.com:IlyaVasilevsky47/foodgram_project.git
```
2. Переходим в папку и создаем файл.
```bash
cd infra
touch .env
```
3. Заходим в файл.
```bash
nano .env
```
4. Заполняем файл.
```conf
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=p&l%385148kslhtyn^##a1)ilz@4zqj=rq&agdol^##zgl9(vs
```
5. Запускаем контейнеры.
```bash
docker-compose up -d
```
6. Создаем базу данных.
```bash
docker-compose exec web python manage.py migrate
```
7. Создаем суперпользователя.
```bash
docker-compose exec web python manage.py createsuperuser
```
8. Заполняем тестовыми данными базу данных.
```bash
docker-compose exec web python manage.py load_data
```
9. Собираем всю статику.
```bash
docker-compose exec web python manage.py collectstatic --no-input
```

## Документация:
После запуска сервера, заходим в ReDoc по ссылке:
```url
http://localhost/api/docs/
```

## Автор:
- Василевский И.А.
- [GitHub](https://github.com/IlyaVasilevsky47)
- [Почта](vasilevskijila047@gmail.com)
- [Вконтакте](https://vk.com/ilya.vasilevskiy47)

## Технический стек
- Python 3.7.9
- Django 2.2.16
- Django REST framework 3.12.4
- Djoser 2.1.0
