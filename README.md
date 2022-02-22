# Django Starter Project

## About this project

The Django Starter Project is a template we use as a starting point for all django projects. There are a lot of amazing django starter projects out there (i.e. Djangox and cookiecutter-django are two well known ones) which can usually be applied to any django project and are built to be an optimal between "batteries included" + flexibility. These project are amazing, but in our case we were still finding that we needed to always do a lot of the same work over and over again for all projects, such as integrating with S3, adding mailgun, creating user profiles, login / register flows, adding support for files, records, etc.


## How to run the project and get started

You can get started by going through the typical Django initiation steps noted below:

- Make sure you are in a virtualenv (it is usually recommended to set up a new one specifically for this project)
- Install everything from requirements.txt using ```pip install -r requirements.txt``` (use `pip3` if running two version of python - this project is running on python3)
- Make sure you create a local database in ```core.settings.base.py```. We always use a format of ```[project name]-local```, so in this case it's ```django-starter-project-local```:
```
local_database = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'NAME': 'django-starter-project-local',
          'USER': 'YOUR LOCAL USER',
          'PASSWORD': 'YOUR LOCAL PASSWORD',
          'HOST': 'localhost',
          'PORT': '5432',
      }
}
```
- Run ```python3 manage.py makemigrations``` to create database migrations
- Run ```python3 manage.py migrate``` to create database tables / initial setup
- Run ```python3 manage.py createsuperuser``` to create an admin user
- Run ```python3 manage.py runserver``` for start the local server
- The project should be running now at http://127.0.0.1:8000/
- The admin panel should be running now at http://127.0.0.1:8000/admin

Please note that the project does rely on some third party services, such as Mailgun for things like password reset (in production) or S3 for file storage (in both dev and production).


## Deployment

The project is setup to deploy to Heroku

- There is a setup for dev and production, using an environment variable `environment` on Heroku to designate 'production' settings.
- The `main` branch is always the most up to date code.

