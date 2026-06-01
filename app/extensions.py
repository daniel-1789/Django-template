from spectree import SpecTree

# Single SpecTree instance, imported by routes (for @api.validate) and by the
# app factory (for api.register). It reads the existing Pydantic schemas to
# build the OpenAPI spec and serve interactive docs.
#   Swagger UI: /apidoc/swagger    ReDoc: /apidoc/redoc    Scalar: /apidoc/scalar
#   Raw spec:   /apidoc/openapi.json
api = SpecTree(
    "flask",
    title="Flask API Template",
    version="0.1.0",
    description="Starter backend: Flask + SQLAlchemy + Alembic + Pydantic.",
)
