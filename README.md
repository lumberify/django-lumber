# django-lumber
 
Lumber is a log aggregating facility. It is made of two components, an agent that listens to logs and a web application which stores log messages and provide a simple user interface to look and search for logs.

## Install

### Server

This repository contains the server side. It is a Django application and can be deployed as such.

```
$ git clone https://github.com/poitch/django-lumber.git
$ cd django-lumber
$ virtualenv venv -p python3.8
$ source venv/bin/activate
$ pip install -r requirements/prod.txt
```

The Lumber server relies on `dotenv` for its environment variables. You will need to create a `.env` under the application's directory. 

The bare minimun required is the definition of `DJANGO_SECRET_KEY`.

```
$ python -c 'from django.core.management.utils import get_random_secret_key; print(f"DJANGO_SECRET_KEY=\"{get_random_secret_key()}\"")' > .env
```

Optionally you might need to set a `DATABASE_URL` to configure where to store log files.

```
$ python manage.py migrate
```

We need to also compile the UI, make sure to have the latest node installed.

```
$ cd lumber/frontend
$ NODE_ENV=production npx webpack --config webpack.config.js
$ cd ../..
$ python manage.py collectstatic
```

At this point you can just run the application using gunicorn
```
$ gunicorn prj.wsgi --name lumber --workers 3 --log-level=info --access-logfile - --bind unix:lumber.sock
```

This will create a unix socket where gunicorn listents to.

#### Setting up users and applications

There is no registration UI or loggin UI at the moment, so you can create user using the command line and use the Django admin UI to login and create application.

```
$ python manage.py createsuperuser
```

Then create an `app` under the admin section.

The UUID of the application is then used to determine the DSN used for the agent.

If the UUID is `a56b9bfe-61d9-4baf-abc5-f35799986438` then the DSN for this application is going to be `http://<hostname>/lumber/sink/a56b9bfe-61d9-4baf-abc5-f35799986438`

### Agent

At the moment, there is only an agent that supports python socket logging, it will expect logging records to be `pickled`.

The agent listens to port 9020 by default but can be configured to any port. It will also take a required `dsn` parameter which is the application DSN defined in the previous step.

On each machines running the application you want to collect logs for, simply checkout the repository and run the agent.

```
$ git clone https://github.com/poitch/django-lumber.git
$ cd django-lumber
$ virtualenv venv -p python3.8
$ pip install -r requirements/prod.txt
$ ./agent -d <dsn>
```

You can optionally specify a `-f <filename>` to also send the local logs to a file, or even use `-v` to have logs sent the standard err.
