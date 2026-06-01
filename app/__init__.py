from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from app.database import close_session
from app.extensions import api


def create_app() -> Flask:
    """Application factory: build, configure, and return the Flask app."""
    app = Flask(__name__)

    # Close the request-scoped DB session when each request ends.
    app.teardown_appcontext(close_session)

    from app.main import bp

    app.register_blueprint(bp)
    _register_error_handlers(app)

    # Generate the OpenAPI spec from the routes' @api.validate decorators and
    # mount the docs (Swagger UI at /apidoc/swagger). Must run after the routes
    # are registered. Spectree handles request validation and returns 422 itself.
    api.register(app)
    return app


def _register_error_handlers(app: Flask) -> None:
    """JSON error responses for abort()-based errors, shaped {"detail": ...}.

    (Request-body/query validation is handled by Spectree, which returns its own
    422 with the Pydantic error list — see app/main.py.)
    """

    @app.errorhandler(HTTPException)
    def _on_http_error(exc: HTTPException):
        return jsonify({"detail": exc.description}), exc.code


# Module-level instance so `flask --app app run` and `gunicorn app:app` both work.
app = create_app()
