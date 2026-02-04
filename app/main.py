from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import shutil
import hashlib
import os

from app.database import models, db
from app.schemas import InvoiceResponse, InvoiceCreate, LineItem
from app.ocr.paddle import PaddleOCRAdapter
from app.preprocessing.cleaner import TextCleaner
from app.extractors.vendor import VendorExtractor
from app.extractors.invoice_number import InvoiceNumberExtractor
from app.extractors.dates import DateExtractor
from app.extractors.currency import CurrencyExtractor
from app.extractors.totals import TotalsExtractor
from app.extractors.line_items import LineItemExtractor
from app.validation.validator import Validator
from app.confidence.score import ConfidenceScorer

# Initialize Core Components
app = FastAPI(title="Smart Scan API")
ocr_engine = PaddleOCRAdapter()
cleaner = TextCleaner()
validator = Validator()
scorer = ConfidenceScorer()

# Extractors
vendor_ex = VendorExtractor()
inv_num_ex = InvoiceNumberExtractor()
date_ex = DateExtractor()
currency_ex = CurrencyExtractor()
totals_ex = TotalsExtractor()
line_item_ex = LineItemExtractor()

# Database
models.Base.metadata.create_all(bind=db.engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB

@app.post("/scan", response_model=InvoiceResponse)
async def scan_invoice(file: UploadFile = File(...), db_session: Session = Depends(db.get_db)):
    # 1. File Validation
    if file.content_type not in ["application/pdf", "image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, PNG, JPEG allowed.")
    
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")
        
    content = await file.read()
    
    # Text Hash for deduplication
    text_hash = hashlib.sha256(content).hexdigest()
    
    # Check if exists
    existing = db_session.query(models.Invoice).filter(models.Invoice.text_hash == text_hash).first()
    if existing:
        return existing

    # 2. OCR
    try:
        # OCR returns list of pages, each page list of lines with boxes
        raw_results = ocr_engine.process_file(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR Failed: {str(e)}")

    # Flatten results for global field extraction (Vendor, Date, etc)
    # But keep structure for Line Items if needed
    all_raw_lines = raw_results # List of dicts
    
    # 3. Preprocessing
    # Merge lines mainly for field extraction (reading order)
    merged_lines = cleaner.merge_lines(all_raw_lines)
    
    # 4. Extraction
    extracted_data = {}
    extracted_data["vendor_name"] = vendor_ex.extract(merged_lines)
    extracted_data["invoice_number"] = inv_num_ex.extract(merged_lines)
    extracted_data["invoice_date"] = date_ex.extract(merged_lines)
    extracted_data["currency"] = currency_ex.extract(merged_lines)
    
    totals = totals_ex.extract(merged_lines)
    extracted_data.update(totals)
    
    # Line Items (Best Effort / Guardrailed)
    # Pass raw lines with boxes to line item extractor
    extracted_data["line_items"] = line_item_ex.extract(all_raw_lines) 

    # 5. Validation
    validation_res = validator.validate(extracted_data)
    
    # 6. Confidence Scoring
    confidence = scorer.calculate(extracted_data, validation_res)
    extracted_data["confidence_score"] = confidence

    # 7. Persistence
    db_invoice = models.Invoice(
        filename=file.filename,
        text_hash=text_hash,
        vendor_name=extracted_data["vendor_name"],
        invoice_number=extracted_data["invoice_number"],
        invoice_date=extracted_data["invoice_date"],
        currency=extracted_data["currency"],
        subtotal=extracted_data["subtotal"],
        tax=extracted_data["tax"],
        total=extracted_data["total"],
        line_items=extracted_data["line_items"], # SQLAlchemy JSON type handles list of dicts
        confidence_score=confidence,
        validation_status="VALID" if validation_res["is_valid"] else "INVALID"
    )
    
    db_session.add(db_invoice)
    db_session.commit()
    db_session.refresh(db_invoice)
    
    return db_invoice
