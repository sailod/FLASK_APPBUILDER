from app.utils import celery_init_app
from app import app

celery = celery_init_app(app)

app.app_context().push()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8787)
