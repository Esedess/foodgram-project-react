prune:
	sudo docker system prune -af

rmn:
	sudo docker container rm nginx
	sudo docker image rm nginx:1.23.1-alpine

rmd:
	sudo docker container rm django
	sudo docker image rm kapkadibab/foodgram:latest

rmp:
	sudo docker container rm postgresql
	sudo docker image rm postgres:14.4-alpine

rmf:
	sudo docker container rm frontend
	sudo docker image rm infra_frontend:latest

rmv:
	sudo docker volume rm infra_db_value infra_frontend_value infra_media_value infra_static_value

rb:
	sudo docker container rm django
	sudo docker image rm kapkadibab/foodgram:latest
	sudo docker-compose -f infra/docker-compose.yml up

up:
	sudo docker-compose -f infra/docker-compose.yml up

build:
	sudo docker-compose -f infra/docker-compose.yml up --build

rebuild:
	sudo docker-compose -f infra/docker-compose.yml up -d --build

db:
	sudo docker-compose -f infra/docker-compose.yml exec django python3 manage.py makemigrations
	sudo docker-compose -f infra/docker-compose.yml exec django python3 manage.py migrate
	sudo docker-compose -f infra/docker-compose.yml exec django python3 manage.py import_all

makemigrations:
	sudo docker-compose -f infra/docker-compose.yml exec django python3 manage.py makemigrations

migrate:
	sudo docker-compose -f infra/docker-compose.yml exec django python3 manage.py migrate

createsuperuser:
	sudo docker-compose -f infra/docker-compose.yml exec django python3 manage.py createsuperuser

collectstatic:
	sudo docker-compose -f infra/docker-compose.yml exec django python3 manage.py collectstatic --no-input

# import_csv:
# 	sudo docker compose -f infra/docker-compose.yml exec django python3 manage.py import_csv

# dumpdb:
# 	sudo docker compose -f infra/docker-compose.yml exec django python manage.py dumpdata > fixtures.json

down:
	sudo docker-compose -f infra/docker-compose.yml  down -v