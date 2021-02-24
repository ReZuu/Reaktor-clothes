web: flask db upgrade; gunicorn warehouse:app
worker: rq worker -u $REDIS_URL warehouse-tasks