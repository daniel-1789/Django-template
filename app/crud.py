from sqlalchemy import ColumnElement, select
from sqlalchemy.orm import InstrumentedAttribute, Session, selectinload

from app.models import Item, Manufacturer
from app.schemas import ItemCreate, ManufacturerCreate


def _name_contains(column: InstrumentedAttribute, search: str | None) -> ColumnElement | None:
    """Case-insensitive 'column contains search' filter, or None if search is blank.

    ilike() is case-insensitive on both SQLite and MySQL. We escape the LIKE
    wildcards (% and _) so a literal one typed in the search isn't treated as a
    pattern — searching "10%" matches the text "10%", not "10<anything>".
    """
    term = (search or "").strip()
    if not term:
        return None
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return column.ilike(f"%{escaped}%", escape="\\")


def list_items(session: Session, search: str | None = None) -> list[Item]:
    # selectinload eager-loads each item's manufacturer in one extra query, so
    # the relationship is populated before we serialize. (Lazy access still works
    # in sync code while the session is open, but eager-loading avoids N+1.)
    stmt = select(Item).options(selectinload(Item.manufacturer)).order_by(Item.id)
    name_filter = _name_contains(Item.name, search)
    if name_filter is not None:
        stmt = stmt.where(name_filter)
    return list(session.scalars(stmt).all())


def get_item(session: Session, item_id: int) -> Item | None:
    stmt = select(Item).options(selectinload(Item.manufacturer)).where(Item.id == item_id)
    return session.scalars(stmt).one_or_none()


def create_item(session: Session, data: ItemCreate) -> Item:
    item = Item(**data.model_dump())
    session.add(item)
    session.commit()
    # Re-fetch so the response includes the eager-loaded manufacturer.
    return get_item(session, item.id)


def get_manufacturer(session: Session, manufacturer_id: int) -> Manufacturer | None:
    return session.get(Manufacturer, manufacturer_id)


def create_manufacturer(session: Session, data: ManufacturerCreate) -> Manufacturer:
    manufacturer = Manufacturer(**data.model_dump())
    session.add(manufacturer)
    session.commit()
    session.refresh(manufacturer)
    return manufacturer


def list_manufacturers(session: Session, search: str | None = None) -> list[Manufacturer]:
    stmt = select(Manufacturer).order_by(Manufacturer.id)
    name_filter = _name_contains(Manufacturer.name, search)
    if name_filter is not None:
        stmt = stmt.where(name_filter)
    return list(session.scalars(stmt).all())
