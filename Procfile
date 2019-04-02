web: gunicorn --bind 0.0.0.0:${PORT} Bemeta.wsgi --log-file -
worker: python manage.py runworker default -v2