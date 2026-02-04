from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.sql import func
from .db import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Extracted Data
    vendor_name = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    invoice_date = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    
    # Financials
    subtotal = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    total = Column(Float, nullable=True)
    
    # Complex Types
    line_items = Column(JSON, nullable=True)
    
    # Validation & Meta
    confidence_score = Column(Float, default=0.0)
    text_hash = Column(String, unique=True, index=True) # For duplicate detection
    validation_status = Column(String, default="PENDING") # VALID, INVALID, PENDING
