"""
OCR processor module.
Handles OCR processing for scanned PDF pages.
"""

import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import io
import numpy as np


class OCRProcessor:
    """Process scanned PDF pages using OCR."""
    
    def __init__(self, dpi: int = 300, lang: str = 'eng'):
        """Initialize the OCR processor.
        Args:
            dpi: DPI to use for rendering PDF pages to images
            lang: Language to use for OCR
        """
        self.dpi = dpi
        self.lang = lang
    
    def process_page(self, page: fitz.Page) -> str:
        """Process a PDF page using OCR.
        Args:
            page: A PyMuPDF page object
        Returns:
            Extracted text from the page
        """
        # Calculate matrix for desired DPI
        zoom = self.dpi / 72  # PDF uses 72 DPI by default
        matrix = fitz.Matrix(zoom, zoom)
        
        # Render page to a pixmap (image)
        pix = page.get_pixmap(matrix=matrix)
        
        # Convert pixmap to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Apply image preprocessing for better OCR results
        img = self._preprocess_image(img)
        
        # Perform OCR
        text = pytesseract.image_to_string(img, lang=self.lang)
        
        return text
    
    def _preprocess_image(self, img: Image.Image) -> Image.Image:
        """Preprocess an image to improve OCR results.
        Args:
            img: PIL Image object
        Returns:
            Preprocessed PIL Image object
        """
        # Convert to numpy array for easier manipulation
        img_array = np.array(img)
        
        # Convert to grayscale if image is color
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            gray = np.dot(img_array[..., :3], [0.2989, 0.5870, 0.1140])
            img_array = gray.astype(np.uint8)
        
        # Simple thresholding for better contrast
        threshold = 200  # Adjust as needed
        img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
        
        # Convert back to PIL Image
        processed_img = Image.fromarray(img_array)
        
        return processed_img