Телеграм-бот, который отслеживает статус проверки моих финальных заданий + отправляет логи.

Стек технологий:
Python, Bot API 


```
Бот запушен на Heroku.
```

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
https://github.com/pkrfc/homework_bot
```

```
cd api_final_yatube
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source env/bin/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

