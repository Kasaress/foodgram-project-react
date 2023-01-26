![example workflow](https://github.com/kasaress/foodgram-project-react/actions/workflows/foodgram_workflow.yaml/badge.svg)

## Описание проекта

Приложение для публикации, поиска и выбора кулинарных рецептов. Каждый может авторизоваться, выложить свои рецепты, подписаться на других пользователей, добавлять
рецепты в избранное или в список покупок, скачать список покупок в pdf.

## Где посмотреть развернутый проект

Проект развернут по адресу:

## Инструкция по запуску проекта

Для запуска проекта необходимо по порядку выполнить следующие команды:
git clone https://github.com/RussianPostman/foodgram-project-react.git
cd infra
docker-compose up -d --build
docker-compose exec backend python manage.py makemigrations app
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python3 manage.py importcsv (данные для загрузки уже лежат в проекте)

## Эндпойнты

- корневой урл
- админка
- а все остальные урлы лежат в доке

## Документация проекта

Документация проекта доступна по адресу: <корневой url>/api/docs/
