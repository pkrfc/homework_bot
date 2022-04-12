Телеграм-бот, который отслеживает статус проверки моих проектов.
Раз в 10 минут отправляет запрос к API, проверяет статус работы отправленной на ревью.
При обновлении статуса присылает сообщение в telegram. Пишет логи и сообщает о важных проблемах сообщением в Telegram.

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
cd homework_bot
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

