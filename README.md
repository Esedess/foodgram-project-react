# foodgram-project-react


<h1 align="center">Привет! </h1>
<h3 align="center">Я студент факультета Бэкенд. Когорта №9+ Яндекс.Практикум</h3>
<h3 align="center">Сегодня наш проект - <a href="https://github.com/KapkaDibab/foodgram-project-react" target="_blank">сайт Foodgram, «Продуктовый помощник»</a></h3>
<h4 align="center">Адрес проекта - <a href="http://esedess.sytes.net" target="_blank">esedess.sytes.net</a></h4>
<h4 align="center">IP адрес проекта - <a href="http://158.160.4.31" target="_blank">158.160.4.31</a></h4>


<p align="left">На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.</p>

<h3 align="left">В настоящее время изучаю <a href="https://www.djangoproject.com/" target="_blank" rel="noreferrer">Django</a>, в проекте используются следующие фреймфорки: </h3>

- 🔭 django
- 🔭 djangorestframework
- 🔭 python-dotenv
- 🔭 djangorestframework-simplejwt
- 🔭 docker
- 🔭 docker-compose
- 🔭 GitHub Actions

<details>
  <summary><h3 align="left">Как запустить проект:</h3></summary>

### Установить Докер:
```
sudo apt update

sudo apt upgrade

sudo apt install docker
```

### Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/Esedess/foodgram-project-react.git

cd foodgram-project-react
```

### Запустить создание и запуск контейнеров:
```
sudo docker-compose -f infra/docker-compose.yml up

# или воспользоваться Make
make up
```

### Выполнить миграции:
```
sudo docker-compose -f infra/docker-compose.yml exec django python3 manage.py makemigrations
sudo docker-compose -f infra/docker-compose.yml exec django python3 manage.py migrate --run-syncdb

# или воспользоваться Make
make db
```

### Создать суперпользователя:
```
sudo docker-compose -f infra/docker-compose.yml exec django python3 manage.py createsuperuser

# или воспользоваться Make
make createsuperuser
```

### Создать статику:
```
sudo docker-compose -f infra/docker-compose.yml exec django python3 manage.py collectstatic --no-input

# или воспользоваться Make
make collectstatic
```

### Выключить и удалить контейнеры:
```
sudo docker-compose -f infra/docker-compose.yml  down -v

# или воспользоваться Make
make down
```
### --------------------------------------------------------------

### Если вы внесли изменения в код контейнеры нужно перезапустить:
```
sudo docker-compose -f infra/docker-compose.yml up -d --build

# или воспользоваться Make
make rebuild
```

### Наполнение БД тестовыми значениями:
```
sudo docker-compose -f infra/docker-compose.yml exec django python3 manage.py import_all

# или воспользоваться Make
make db_import
```
</details>

<h4 align="center">После запуска проект будет доступен по адресу- <a href="http://localhost/" target="_blank">localhost</a></h4>

### Django admin panel
### http://localhost/admin/
### 
### login/password - admin/admin
### email - admin@admin.ru

🌱 [Никита Трошкин](https://github.com/Esedess)
