from flask import Blueprint, abort, jsonify, request
from pydantic import BaseModel
from spectree import Response

from app import crud
from app.database import get_session
from app.extensions import api
from app.schemas import (
    Health,
    ItemCreate,
    ItemRead,
    ManufacturerCreate,
    ManufacturerRead,
    SearchQuery,
)

# All routes live on this blueprint, registered in app/__init__.py's create_app().
# @api.validate(...) does request validation (from the Pydantic schemas) AND feeds
# the OpenAPI docs at /apidoc/swagger. Validated input arrives on request.context;
# invalid bodies/queries get an automatic 422 before the handler runs.
bp = Blueprint("api", __name__)


def _dump(model: type[BaseModel], obj: object) -> dict:
    """Serialize an ORM object through a Pydantic read-model to a JSON-safe dict."""
    return model.model_validate(obj).model_dump(mode="json")


@bp.get("/healthz")
@api.validate(resp=Response(HTTP_200=Health), tags=["meta"])
def healthz():
    return {"status": "ok"}


@bp.get("/items")
@api.validate(query=SearchQuery, resp=Response(HTTP_200=list[ItemRead]), tags=["items"])
def list_items():
    items = crud.list_items(get_session(), search=request.context.query.search)
    return jsonify([_dump(ItemRead, item) for item in items])


@bp.get("/items/<int:item_id>")
@api.validate(resp=Response(HTTP_200=ItemRead, HTTP_404=None), tags=["items"])
def get_item(item_id: int):
    item = crud.get_item(get_session(), item_id)
    if item is None:
        abort(404, description=f"Item {item_id} not found")
    return _dump(ItemRead, item)


@bp.post("/items")
@api.validate(json=ItemCreate, resp=Response(HTTP_201=ItemRead, HTTP_400=None), tags=["items"])
def create_item():
    payload: ItemCreate = request.context.json
    session = get_session()
    if crud.get_manufacturer(session, payload.manufacturer_id) is None:
        abort(400, description=f"Manufacturer {payload.manufacturer_id} not found")
    item = crud.create_item(session, payload)
    return _dump(ItemRead, item), 201


@bp.get("/manufacturers")
@api.validate(query=SearchQuery, resp=Response(HTTP_200=list[ManufacturerRead]), tags=["manufacturers"])
def list_manufacturers():
    manufacturers = crud.list_manufacturers(get_session(), search=request.context.query.search)
    return jsonify([_dump(ManufacturerRead, m) for m in manufacturers])


@bp.get("/manufacturers/<int:manufacturer_id>")
@api.validate(resp=Response(HTTP_200=ManufacturerRead, HTTP_404=None), tags=["manufacturers"])
def get_manufacturer(manufacturer_id: int):
    manufacturer = crud.get_manufacturer(get_session(), manufacturer_id)
    if manufacturer is None:
        abort(404, description=f"Manufacturer {manufacturer_id} not found")
    return _dump(ManufacturerRead, manufacturer)


@bp.post("/manufacturers")
@api.validate(json=ManufacturerCreate, resp=Response(HTTP_201=ManufacturerRead), tags=["manufacturers"])
def create_manufacturer():
    payload: ManufacturerCreate = request.context.json
    manufacturer = crud.create_manufacturer(get_session(), payload)
    return _dump(ManufacturerRead, manufacturer), 201
