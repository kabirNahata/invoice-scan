from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None

class InvoiceBase(BaseModel):
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    currency: Optional[str] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    line_items: List[LineItem] = []
    confidence_score: float = 0.0

class InvoiceCreate(InvoiceBase):
    filename: str
    text_hash: str

class InvoiceResponse(InvoiceBase):
    id: int
    filename: str
    upload_date: datetime
    validation_status: str

    class Config:
        from_attributes = True
