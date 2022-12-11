# Yatube project
### Описание
YATUBE - cоциальная сеть блогеров
### Технологии
- Python 3.7.15
- Django 2.2.19
### Запуск проекта в dev-режиме

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/DmitriiParshin/yatube.git
```

```
cd yatube
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source venv/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

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
```
### Автор
Dmitry Parshin
