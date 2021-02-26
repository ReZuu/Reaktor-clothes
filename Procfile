web: flask db upgrade; gunicorn warehouse:app
worker: rq worker --with-scheduler -u $REDIS_URL warehouse-tasks