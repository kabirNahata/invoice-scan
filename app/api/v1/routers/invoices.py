from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import csv
import io
import shutil
import os

from app.api import deps
from app.services.pipeline import InvoicePipeline
from app.models import InvoiceSchema, DBInvoice
from app.core.exceptions import AppError
from app.database import get_db
from app.repositories.invoice_repository import InvoiceRepository

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok", "message": "Smart Scan API is running (Production Mode)"}

@router.post("/scan", response_model=InvoiceSchema)
async def scan_invoice(
    file: UploadFile = File(...),
    pipeline: InvoicePipeline = Depends(deps.get_invoice_pipeline)
):
    """
    Scans an uploaded invoice file and returns structured data.
    """
    if file.content_type not in ["application/pdf", "image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, JPG, PNG allowed.")
    
    # We need to save the file or read it into memory. 
    # PaddleOCR expects bytes or path. The current Pipeline takes bytes.
    # Reading into memory is fine for MVP, but for large files we might stream.
    try:
        content = await file.read()
        result = pipeline.process(content, file.filename)
        return result
    except AppError as e:
        # Map AppErrors to HTTP status codes
        # This could be done globally, but explicit here for clarity or custom mapping
        status_code = 500
        if "Duplicate" in str(e) or "already exists" in str(e):
             status_code = 409
        elif "Input" in str(e):
             status_code = 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/export")
def export_invoices(
    repo: InvoiceRepository = Depends(deps.get_repository)
):
    """Export all invoices to CSV."""
    def iter_csv():
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write Header
        writer.writerow(["ID", "Vendor", "Date", "Invoice #", "Total", "Currency", "Filename", "Confidence"])
        output.seek(0)
        yield output.read()
        output.truncate(0)
        output.seek(0)
        
        invoices = repo.list()
        for invoice in invoices:
            writer.writerow([
                invoice.id,
                invoice.vendor_name,
                invoice.invoice_date,
                invoice.invoice_number,
                invoice.total,
                invoice.currency,
                invoice.filename,
                invoice.confidence_score
            ])
            output.seek(0)
            yield output.read()
            output.truncate(0)
            output.seek(0)
            
    response = StreamingResponse(iter_csv(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=invoices.csv"
    return response
