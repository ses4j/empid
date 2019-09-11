release: python manage.py migrate --noinput
web: waitress-serve --port=$PORT empid.wsgi:application