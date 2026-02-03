from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Generator

from app.database import get_db
from app.repositories.invoice_repository import InvoiceRepository
from app.services.ocr import PaddleOCRService
from app.services.text_cleaner import TextCleaner
from app.services.ai_extractor import AIExtractor
from app.services.validator import Validator
from app.services.pipeline import InvoicePipeline

# Singleton instances (initialized once)
# Note: In a real heavy app, we might want to handle lifecycle better, but this is fine.
_ocr_service = PaddleOCRService()
_text_cleaner = TextCleaner()
_ai_extractor = AIExtractor()
_validator = Validator()

def get_ocr_service() -> PaddleOCRService:
    return _ocr_service

def get_text_cleaner() -> TextCleaner:
    return _text_cleaner

def get_ai_extractor() -> AIExtractor:
    return _ai_extractor

def get_validator() -> Validator:
    return _validator

def get_repository(db: Session = Depends(get_db)) -> InvoiceRepository:
    return InvoiceRepository(db)

def get_invoice_pipeline(
    ocr: PaddleOCRService = Depends(get_ocr_service),
    cleaner: TextCleaner = Depends(get_text_cleaner),
    ai: AIExtractor = Depends(get_ai_extractor),
    validator: Validator = Depends(get_validator),
    repo: InvoiceRepository = Depends(get_repository)
) -> InvoicePipeline:
    return InvoicePipeline(ocr, cleaner, ai, validator, repo)
