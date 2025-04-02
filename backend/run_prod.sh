export FLASK_ENV=prod
echo $FLASK_ENV
gunicorn -w 4 -b 0.0.0.0:8082 'app:create_app()'
