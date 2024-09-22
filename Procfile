web: daphne -b 0.0.0.0 -p $PORT core.asgi:application
worker: celery -A core worker -c 10 -B --loglevel=info
