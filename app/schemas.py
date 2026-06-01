from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Health(BaseModel):
    """Response for GET /healthz."""

    status: str = Field(examples=["ok"])


class SearchQuery(BaseModel):
    """Optional `?search=` query param shared by the list endpoints."""

    search: str | None = Field(None, description="Case-insensitive filter on name")


class ManufacturerCreate(BaseModel):
    """Payload for POST /manufacturers."""

    name: str = Field(..., max_length=255, examples=["Acme Corp"])
    state: str = Field(..., min_length=2, max_length=2, examples=["CA"])


class ManufacturerRead(BaseModel):
    """Manufacturer as returned by the API (also nested inside ItemRead)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    state: str


class ItemCreate(BaseModel):
    """Payload for POST /items."""

    name: str = Field(..., max_length=255, examples=["Widget"])
    description: str | None = Field(None, max_length=1024)
    price: float = Field(..., ge=0, examples=[9.99])
    manufacturer_id: int = Field(..., examples=[1])


class ItemRead(BaseModel):
    """Item as returned by the API, with its manufacturer nested in."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: float
    created_at: datetime
    manufacturer_id: int
    manufacturer: ManufacturerRead
