from abc import ABC, abstractmethod
import logging
from typing import Optional
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
import io

# Configure logging
logger = logging.getLogger(__name__)

class OCRError(Exception):
    """Custom exception for OCR failures."""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error

class OCRService(ABC):
    """Abstract Base Class for OCR Services."""
    
    @abstractmethod
    def extract_text(self, image_bytes: bytes) -> str:
        """
        Extracts text from the provided image bytes.
        
        Args:
            image_bytes: Raw bytes of the image file.
            
        Returns:
            str: The extracted text content.
            
        Raises:
            OCRError: If extraction fails.
        """
        pass

class PaddleOCRService(OCRService):
    """OCR implementation using PaddleOCR."""
    
    def __init__(self, use_angle_cls: bool = True, lang: str = 'en'):
        try:
            # Initialize PaddleOCR
            # use_angle_cls=True allows detecting rotated text (deprecated, use use_textline_orientation)
            self.ocr = PaddleOCR(use_angle_cls=use_angle_cls, lang=lang, enable_mkldnn=False)
            logger.info("PaddleOCR initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise OCRError("Failed to initialize OCR engine", e)

    def extract_text(self, image_bytes: bytes) -> str:
        if not image_bytes:
            raise OCRError("Empty image bytes provided")

        try:
            # Convert bytes to PIL Image then to numpy array for PaddleOCR
            image = Image.open(io.BytesIO(image_bytes))
            
            # Ensure image is in RGB mode (PaddleOCR expects 3 channels usually)
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            img_array = np.array(image)

            # Perform inference
            # result is a list of [ [ [points], [text, confidence] ], ... ]
            result = self.ocr.ocr(img_array)
            
            if not result or result[0] is None:
                logger.warning("OCR detected no text or returned empty result.")
                return ""

            # Extract just the text parts and concatenate them
            # PaddleOCR returns a list of lists (pages), we assume single image input here mostly
            # structure: result[0] is the first image results
            extracted_lines = []
            for line in result[0]:
                text = line[1][0]
                extracted_lines.append(text)
            
            full_text = "\n".join(extracted_lines)
            return full_text

        except Exception as e:
            logger.error(f"OCR Extraction failed: {e}")
            raise OCRError("Failed to extract text from image", e)
