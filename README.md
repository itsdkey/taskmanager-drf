# taskmanager-drf
A simple task manager using Django/DRF + Postgresql

* [Intuition](#intuition)
* [What I used](#what-i-used)
* [What patterns I followed](#what-patterns-i-followed)
* [Local development](#env-vars-setup)
    * [Env vars setup](#env-vars-setup)
    * [Docker compose](#run-the-project-using-docker-compose)
* [Doing stuff related to the project](#doing-stuff-related-to-the-project)
    * [Always execute commands inside a container](#always-execute-commands-inside-a-container)
    * [Migrations](#migrating-and-setting-up-database)
    * [Creating a superuser](#creating-a-superuser)
    * [Testing](#testing)
* [Debugging](#debugging)
* [Project conventions](#project-conventions)

## Intuition
Just a fun project to code a simple task manager app just to show how I code in Django.
To complate this project I used:
- [Django](https://www.djangoproject.com/)
- [Django rest framework](https://www.django-rest-framework.org/)
- [Postgresql](https://www.postgresql.org.pl/)
- A [TDD](https://pl.wikipedia.org/wiki/Test-driven_development) approach


## What I used
To show a little power what a Django project could have and also to follow
best practices I used the following concepts:
- env vars to hide secrets for our DB,
- [Django's ORM](https://docs.djangoproject.com/en/5.0/topics/db/queries/) to use our Database
- [DRF's serializers ](https://www.django-rest-framework.org/api-guide/serializers/) to serialize incoming data
- [DRF's viewsets](https://www.django-rest-framework.org/api-guide/viewsets/) to return our data in JSON format
- [DRF's custom actions](https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing) to update our task's state
- [DRF's APITestCase](https://www.django-rest-framework.org/api-guide/testing/#api-test-cases) to write tests
- [FactoryBoy](https://factoryboy.readthedocs.io/en/stable/index.html) to use factories for our models
- [django-filter](https://django-filter.readthedocs.io/en/stable/) to have filters on our endpoints
- [django-environ](https://django-environ.readthedocs.io/en/latest/) to configure our Dj app with env vars
- [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/) to provide OpenAPI/Swagger docs
- [GitHub actions](https://github.com/features/actions) for CI/CD support

## What patterns I followed
To keep following the best practices and to have my code more structured I decided to follow the patterns below:
- MVT - it is provided and suggested by the Django doc's itself.
- Serializers - put serialization into a separate class so our views are only responsible for returning parsed data


## Local development
### Env vars setup
To make this project work you first need to set up the required env vars:
```shell
POSTGRES_DB=<your postgresql database name>
POSTGRES_PASSWORD=<your postgresql users password>
POSTGRES_USER=<your postgresql username>
POSTGRES_HOST=db (because we are using docker containers)
POSTGRES_PORT=5432 (the default port for postgresql)
DEBUG=<1 if you want DEBUG on else 0)
DJANGO_SECRET=<your django secret>
ALLOWED_HOSTS=127.0.0.1 (because we are working locally)
INTERNAL_IPS=127.0.0.1 (the same as above)
OPENAPI_ENABLED=<1 if you want to use OPENAPI docs else 0>
```


### Run the project using docker compose
Build and the application with the following:
```shell
docker compose up app
```
You can run it in the background if you use the `-d` flag:
```shell
docker compose up -d app
```

This will run 2 containers: app and db. Review the interactive API
documentation at http://127.0.0.1:8000/openapi/swagger/


## Doing stuff related to the project
### Always execute commands inside a container
If you want to develop with docker compose you will need sometimes to execute commands
inside the app's container because the whole environment is there. This is separate from your
computer's environment. Entering the container is also necessary because all the env vars are loaded
from the .env file, and they will help you run your project smoothly.

All the commands below this paragraph will require you to enter the container first. To do that
please run one of the following commands:
```shell
docker compose run --rm app bash
```
or:
```shell
docker exec -it taskmanager-app bash
```

The first one creates a separate container if you have the project already running. The second one will
enter the running container itself.

### Migrating and setting up database
If you want to modify database, start with changing the code in <django_app>/models.
Be sure that your app is in the setting's INSTALLED_APPS list.
Then generate a migration file with the following command:
```shell
python manage.py makemigrations <app_name>
```

Apply the migration with:
```shell
python manage.py migrate <app_name>
```

### Creating a superuser
This will create an Admin user for you. It will ask for the basic information it needs to create an account.
Use the following command
```shell
python manage.py createsuperuser
```

From now on you will have access to the admin's panel at http://127.0.0.1:8000/admin/

### Testing
Remember to be inside the container. Use the following command to execute all tests using the
Django's testrunner:
```shell
python manage.py test
```
Or you can run specific Apps/TestCases/tests by narrowing the command above:
```shell
python manage.py test <app_name>
python manage.py test <app_name>.tests.<class_name>
python manage.py test <app_name>.tests.<class_name>.<test_name>
```

## Debugging
You can debug your project using a debugger. When working with docker containers it's easier to use
a debugger called [WDB](https://github.com/Kozea/wdb). It allows to debug your workflow at runtime
using a web browser. You can debug tests or flows using the installed wdb debugger.
Don't worry, the docker-compose.yml file sets the necessary environment variables:
```shell
PYTHONBREAKPOINT: wdb.set_trace
WDB_SOCKET_SERVER: wdb
WDB_NO_BROWSER_AUTO_OPEN: 1
```

### How to use it
First, place a breakpoint:
```python
breakpoint()
```
The start the WDB container in the background:
```shell
docker compose up -d wdb
```

After that run your piece of code and check the statement inside the interactive console at: http://127.0.0.1:1984/


## Project conventions
The project follows some specific conventions thanks to pre-commit:
- isort
- black
- flake8
- no-commit-to-branch (main branch)
- bandit
- docformatter
- python-safety-dependencies-check
- gitlint

To install the GitHub pre-commit hooks. This can be done in your virtual
environment by:
```shell
pre-commit install
```