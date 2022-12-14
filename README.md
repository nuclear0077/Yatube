## Yatube

## About
Yatube это социальная сеть для публикации личных дневников.
Это будет сайт, на котором можно создать свою страницу. Если на нее зайти, то можно посмотреть все записи автора.
Пользователи смогут заходить на чужие страницы, подписываться на авторов и комментировать их записи.
Автор может выбрать имя и уникальный адрес для своей страницы. 
Записи можно отправить в сообщество и посмотреть записи разных авторов.


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

