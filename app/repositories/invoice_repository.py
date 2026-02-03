from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.repositories.base import BaseRepository
from app.models import DBInvoice, DBInvoiceItem
from app.core.exceptions import DatabaseError, DuplicateInvoiceError

class InvoiceRepository(BaseRepository[DBInvoice]):
    """Repository for Invoice data access."""
    
    def __init__(self, db: Session):
        self.db = db

    def add(self, invoice: DBInvoice) -> DBInvoice:
        try:
            self.db.add(invoice)
            self.db.commit()
            self.db.refresh(invoice)
            return invoice
        except IntegrityError as e:
            self.db.rollback()
            if "unique constraint" in str(e.orig).lower() or "unique constraint" in str(e).lower():
                 raise DuplicateInvoiceError(f"Invoice with content hash {invoice.content_hash} already exists.")
            raise DatabaseError("Database integrity error", e)
        except Exception as e:
            self.db.rollback()
            raise DatabaseError("Failed to add invoice to database", e)

    def add_with_items(self, invoice: DBInvoice, items: List[DBInvoiceItem]) -> DBInvoice:
        """Adds an invoice and its line items transactionally."""
        try:
            self.db.add(invoice)
            self.db.flush() # Generate ID for invoice
            
            for item in items:
                item.invoice_id = invoice.id
                self.db.add(item)
                
            self.db.commit()
            self.db.refresh(invoice)
            return invoice
        except IntegrityError as e:
            self.db.rollback()
            if "unique constraint" in str(e.orig).lower() or "unique constraint" in str(e).lower():
                 raise DuplicateInvoiceError(f"Invoice with content hash {invoice.content_hash} already exists.")
            raise DatabaseError("Database integrity error", e)
        except Exception as e:
            self.db.rollback()
            raise DatabaseError("Failed to save invoice transaction", e)

    def get(self, id: int) -> Optional[DBInvoice]:
        return self.db.query(DBInvoice).filter(DBInvoice.id == id).first()

    def get_by_hash(self, content_hash: str) -> Optional[DBInvoice]:
        return self.db.query(DBInvoice).filter(DBInvoice.content_hash == content_hash).first()

    def list(self) -> List[DBInvoice]:
        return self.db.query(DBInvoice).all()
