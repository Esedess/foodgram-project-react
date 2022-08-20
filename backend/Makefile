up:
	python3 manage.py runserver

mm:
	python3 manage.py makemigrations

migrate:
	python3 manage.py migrate

createsuperuser:
	python3 manage.py createsuperuser

collectstatic:
	python3 manage.py collectstatic --no-input

# import_csv:
# 	python3 manage.py import_csv

# dumpdb:
# 	python manage.py dumpdata > fixtures.json

down:
	sudo docker-compose -f infra/docker-compose.yml  down -v