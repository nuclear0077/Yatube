## Социальная сеть Yatube

## About
Новая социальная сеть для публикации личных дневников с возможностью авторизации, подписки на автора, публикация, удаления записей, а также с возможностью оценить публикацию. Благодаря этому проекту можно будет расширять свой кругозор и получать новую информацию.


## Technology
Python 3.7, Django 2.2.19, SQLite3


## Documentation

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/nuclear0077/yatube.git
```

```
cd yatube
```

Cоздать и активировать виртуальное окружение:

```
python3.7 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```


## Developer

- [Aleksandr M](https://github.com/nuclear0077)
- Telegram @nuclear0077

