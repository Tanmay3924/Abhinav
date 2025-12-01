from app import create_app, celery

app = create_app()
app.app_context().push()

# REMOVE THIS LINE:
# celery.conf.update(app.config)

import app.tasks