from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import datetime

# --- Pydantic Models for API & Validation ---

class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None

class InvoiceSchema(BaseModel):
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    currency: Optional[str] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    line_items: List[LineItem] = Field(default_factory=list)
    
    # Internal fields not from AI
    confidence_score: float = 0.0
    filename: Optional[str] = None
    content_hash: Optional[str] = None

    class Config:
        from_attributes = True

# --- SQLAlchemy Models for SQLite ---

Base = declarative_base()

class DBInvoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    invoice_date = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    subtotal = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    total = Column(Float, nullable=True)
    
    filename = Column(String, nullable=False)
    content_hash = Column(String, unique=True, index=True) # For duplicate detection
    confidence_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    items = relationship("DBInvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class DBInvoiceItem(Base):
    __tablename__ = 'invoice_items'

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    description = Column(String, nullable=False)
    quantity = Column(Float, nullable=True)
    unit_price = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)

    invoice = relationship("DBInvoice", back_populates="items")
