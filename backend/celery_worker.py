from app import create_app, celery

app = create_app()

celery.conf.update(app.config)

import app.tasks
