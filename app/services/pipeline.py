from fastapi import UploadFile
from typing import BinaryIO
import logging

from app.services.ocr import PaddleOCRService
from app.services.text_cleaner import TextCleaner
from app.services.ai_extractor import AIExtractor
from app.services.validator import Validator
from app.repositories.invoice_repository import InvoiceRepository
from app.models import InvoiceSchema, DBInvoice, DBInvoiceItem
from app.core.exceptions import AppError, OCRError

logger = logging.getLogger(__name__)

class InvoicePipeline:
    """
    Orchestrates the invoice scanning, extraction, validation, and storage pipeline.
    """
    
    def __init__(self, 
                 ocr_service: PaddleOCRService,
                 text_cleaner: TextCleaner,
                 ai_extractor: AIExtractor,
                 validator: Validator,
                 repository: InvoiceRepository):
        self.ocr_service = ocr_service
        self.text_cleaner = text_cleaner
        self.ai_extractor = ai_extractor
        self.validator = validator
        self.repository = repository

    def process(self, file_content: bytes, filename: str) -> InvoiceSchema:
        """
        Process an invoice file bytes: OCR -> Clean -> AI -> Validate -> Save.
        """
        logger.info(f"Starting processing for file: {filename}")
        
        # 1. OCR
        raw_text = self.ocr_service.extract_text(file_content)
        if not raw_text:
             raise OCRError("No text detected in the document.")

        # 2. Clean Text
        cleaned_text = self.text_cleaner.clean_text(raw_text)
        
        # 3. Duplicate Check (Hash)
        content_hash = self.validator.compute_content_hash(cleaned_text)
        existing = self.repository.get_by_hash(content_hash)
        if existing:
            # We assume DuplicateInvoiceError is handled by the caller or we raise it here
            from app.core.exceptions import DuplicateInvoiceError
            raise DuplicateInvoiceError(f"Invoice already exists with ID: {existing.id}")

        # 4. AI Extraction
        # Note: AIExtractor currently instantiates its own model, which is fine for now but could be injected.
        extracted_data = self.ai_extractor.extract_invoice_data(cleaned_text)
        
        # 5. Schema Validation & Confidence
        invoice_schema = InvoiceSchema(**extracted_data)
        confidence = self.validator.calculate_confidence(invoice_schema)
        
        # Enrich Schema
        invoice_schema.confidence_score = confidence
        invoice_schema.filename = filename
        invoice_schema.content_hash = content_hash
        
        # 6. Persistence
        # Convert Pydantic to DB Models
        db_invoice = DBInvoice(
            vendor_name=invoice_schema.vendor_name,
            invoice_number=invoice_schema.invoice_number,
            invoice_date=invoice_schema.invoice_date,
            currency=invoice_schema.currency,
            subtotal=invoice_schema.subtotal,
            tax=invoice_schema.tax,
            total=invoice_schema.total,
            filename=invoice_schema.filename,
            content_hash=invoice_schema.content_hash,
            confidence_score=invoice_schema.confidence_score
        )
        
        db_items = [
            DBInvoiceItem(
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                amount=item.amount
            ) for item in invoice_schema.line_items
        ]
        
        saved_invoice = self.repository.add_with_items(db_invoice, db_items)
        logger.info(f"Successfully processed and saved invoice ID: {saved_invoice.id}")
        
        return invoice_schema
