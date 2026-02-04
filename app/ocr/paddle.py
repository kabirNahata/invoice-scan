from paddleocr import PaddleOCR
from pdf2image import convert_from_path, convert_from_bytes
import numpy as np
import io
from PIL import Image

class PaddleOCRAdapter:
    def __init__(self, lang='en'):
        # use_angle_cls=True enables orientation classification
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang)

    def process_file(self, file_bytes: bytes, filename: str):
        """
        Process a file (PDF or Image) and return extracted text with metadata.
        Returns a list of pages, where each page is a list of lines.
        Each line: {'text': str, 'box': [[x1,y1], [x2,y2], [x3,y3], [x4,y4]], 'confidence': float}
        """
        images = []
        if filename.lower().endswith('.pdf'):
            try:
                # User provided Poppler path
                POPPLER_PATH = r"C:\Program Files\Release-25.12.0-0\poppler-25.12.0\Library\bin"
                
                # Convert PDF bytes to images
                images = convert_from_bytes(file_bytes, poppler_path=POPPLER_PATH)
            except Exception as e:
                print(f"Error converting PDF: {e}")
                # Fallback or re-raise depending on requirements. 
                # For now re-raise to be handled by caller
                raise ValueError(f"Failed to convert PDF: {str(e)}")
        else:
            # Assume image
            try:
                image = Image.open(io.BytesIO(file_bytes)).convert('RGB')
                images = [image]
            except Exception as e:
                raise ValueError(f"Failed to open image: {str(e)}")

        results = []
        for i, img in enumerate(images):
            # PaddleOCR expects numpy array
            img_np = np.array(img)
            
            # Run OCR
            # result structure: [ [ [ [x1,y1], ... ], (text, confidence) ], ... ]
            ocr_result = self.ocr.ocr(img_np, cls=True)
            
            page_lines = []
            if ocr_result and ocr_result[0]:
                for line in ocr_result[0]:
                    box = line[0]
                    text, confidence = line[1]
                    page_lines.append({
                        "text": text,
                        "box": box,
                        "confidence": confidence,
                        "page": i + 1
                    })
            results.extend(page_lines)
            
        return results
