from src.api.rest.app import create_app
from src.config.settings import settings
from src.observability.logging import setup_logging

# Server logs go to stdout as JSON lines: read them with `docker compose logs auth`.
setup_logging(settings.log_level, settings.log_json)

app = create_app()
