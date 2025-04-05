import os
import re
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import numpy as np
from ai_processor import AIProcessor

class OCRProcessor:
    def __init__(self):
        # Check if Tesseract is available
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            print(f"Tesseract not properly configured: {e}")
            # In a production system, we might raise an exception here
        
        # Initialize AI processor if available
        try:
            self.ai_processor = AIProcessor()
            self.use_ai = True
            print("AI processing enabled for enhanced OCR accuracy")
        except Exception as e:
            print(f"AI processing not available: {e}")
            self.use_ai = False
    
    def process_file(self, file_path):
        """
        Process an uploaded file (image or PDF) using OCR
        
        Args:
            file_path (str): Path to the uploaded file
            
        Returns:
            str: Extracted text from the file
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext in ['.pdf']:
                return self._process_pdf(file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
                return self._process_image(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            print(f"Error processing file: {e}")
            return ""
    
    def _process_image(self, image_path):
        """
        Process a single image using OCR
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Extracted text from the image
        """
        try:
            # Open image
            image = Image.open(image_path)
            
            # Convert to grayscale for better OCR results
            if image.mode != 'L':
                image = image.convert('L')
            
            # Apply some pre-processing for better OCR results
            # This is a simple approach; more sophisticated methods could be used
            # image = self._preprocess_image(image)
            
            # Perform OCR
            extracted_text = pytesseract.image_to_string(image, lang='eng')
            
            return extracted_text
        except Exception as e:
            print(f"Error processing image: {e}")
            return ""
    
    def _process_pdf(self, pdf_path):
        """
        Process a PDF file using OCR
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from the PDF
        """
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            # Process each image
            all_text = []
            for image in images:
                # Convert to grayscale
                if image.mode != 'L':
                    image = image.convert('L')
                
                # Apply pre-processing
                # image = self._preprocess_image(image)
                
                # Perform OCR
                text = pytesseract.image_to_string(image, lang='eng')
                all_text.append(text)
            
            # Combine text from all pages
            return "\n\n".join(all_text)
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return ""
    
    def _preprocess_image(self, image):
        """
        Apply pre-processing to improve OCR results
        
        Args:
            image (PIL.Image): Image to preprocess
            
        Returns:
            PIL.Image: Preprocessed image
        """
        # This is a placeholder for more sophisticated preprocessing
        # In a production system, we would use more advanced techniques
        return image
    
    def extract_items(self, text):
        """
        Extract structured item data from OCR text
        
        Args:
            text (str): Raw OCR text
            
        Returns:
            list: List of dictionaries containing item details
        """
        # First, enhance the OCR text with AI if available
        if self.use_ai:
            try:
                # Enhance the raw OCR text
                enhanced_text = self.ai_processor.enhance_ocr_text(text)
                print("OCR text enhanced with AI")
                
                # Try AI-based extraction first
                ai_items = self.ai_processor.extract_structured_data(enhanced_text)
                if ai_items and len(ai_items) > 0:
                    print(f"AI successfully extracted {len(ai_items)} items")
                    return ai_items
                
                # If AI extraction fails, fall back to traditional methods but use the enhanced text
                text = enhanced_text
            except Exception as e:
                print(f"AI-based extraction failed: {e}")
                # Continue with traditional methods
        
        items = []
        
        # Clean the text
        text = self._clean_text(text)
        
        # Split into lines
        lines = text.split('\n')
        
        # Different invoice formats will require different parsing strategies
        # This is a simple approach that looks for lines with quantity, price, and total
        for i, line in enumerate(lines):
            # Skip short lines
            if len(line.strip()) < 5:
                continue
            
            # Try to extract item details using regex
            item_data = self._extract_item_from_line(line)
            
            if item_data:
                items.append(item_data)
                continue
            
            # Try multi-line approach if single line fails
            if i < len(lines) - 1:
                combined_line = line + " " + lines[i + 1]
                item_data = self._extract_item_from_line(combined_line)
                
                if item_data:
                    items.append(item_data)
        
        # If no items found, try a different approach
        if not items:
            items = self._extract_items_table_format(text)
        
        return items
    
    def _clean_text(self, text):
        """
        Clean and normalize OCR text
        
        Args:
            text (str): Raw OCR text
            
        Returns:
            str: Cleaned text
        """
        # Replace common OCR errors
        text = text.replace('|', '1')
        text = text.replace('l', '1')
        text = text.replace('O', '0')
        text = text.replace('o', '0')
        
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        # Replace common currency symbols
        text = text.replace('₹', '')
        text = text.replace('$', '')
        text = text.replace('€', '')
        
        # Remove other special characters
        text = re.sub(r'[^\w\s\.\-\,]', '', text)
        
        return text
    
    def _extract_item_from_line(self, line):
        """
        Extract item details from a single line
        
        Args:
            line (str): Line of text
            
        Returns:
            dict: Item details or None if no match
        """
        # This regex pattern tries to match common invoice line item formats
        # It's simplified and would need to be adapted to specific invoice formats
        patterns = [
            # Pattern 1: Item name followed by quantity, unit price, and total
            r'([\w\s\-]+)\s+(\d+(?:\.\d+)?)\s+(?:x\s+)?(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)',
            
            # Pattern 2: Item name followed by quantity and total (no unit price)
            r'([\w\s\-]+)\s+(\d+(?:\.\d+)?)\s+(?:pcs|units|nos)?\s+(\d+(?:\.\d+)?)',
            
            # Pattern 3: Just item name and price
            r'([\w\s\-]+)\s+(\d+(?:\.\d+)?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                groups = match.groups()
                
                if len(groups) == 4:  # Pattern 1
                    item_name = groups[0].strip()
                    qty = float(groups[1])
                    unit_price = float(groups[2])
                    total = float(groups[3])
                    
                    # Verify that qty * unit_price is approximately equal to total
                    calculated_total = qty * unit_price
                    if abs(calculated_total - total) > 1:  # Allow for small rounding differences
                        # If totals don't match, this might not be a valid item line
                        continue
                    
                    return {
                        "item": item_name,
                        "qty": qty,
                        "unit_price": unit_price,
                        "total": total
                    }
                
                elif len(groups) == 3:  # Pattern 2
                    item_name = groups[0].strip()
                    qty = float(groups[1])
                    total = float(groups[2])
                    unit_price = total / qty if qty else 0
                    
                    return {
                        "item": item_name,
                        "qty": qty,
                        "unit_price": unit_price,
                        "total": total
                    }
                
                elif len(groups) == 2:  # Pattern 3
                    item_name = groups[0].strip()
                    total = float(groups[1])
                    
                    return {
                        "item": item_name,
                        "qty": 1,  # Assume quantity of 1
                        "unit_price": total,
                        "total": total
                    }
        
        return None
    
    def _extract_items_table_format(self, text):
        """
        Extract items assuming a table format in the invoice
        
        Args:
            text (str): OCR text
            
        Returns:
            list: List of item dictionaries
        """
        items = []
        
        # Split into lines
        lines = text.split('\n')
        
        # Look for lines that might represent table rows
        for line in lines:
            # Skip short lines
            if len(line.strip()) < 10:
                continue
            
            # Split line by multiple spaces
            parts = re.split(r'\s{2,}', line.strip())
            
            if len(parts) >= 3:
                # Try to identify which parts correspond to item, qty, price, total
                item_name = parts[0]
                
                # Look for numbers in the other parts
                numbers = []
                for part in parts[1:]:
                    try:
                        num = float(re.sub(r'[^\d\.]', '', part))
                        numbers.append(num)
                    except:
                        pass
                
                if len(numbers) >= 2:
                    # Assume last number is total
                    total = numbers[-1]
                    
                    # If we have 3 numbers, assume they are qty, unit_price, total
                    if len(numbers) >= 3:
                        qty = numbers[-3]
                        unit_price = numbers[-2]
                    else:
                        # If we have 2 numbers, assume they are qty and total
                        qty = numbers[-2]
                        unit_price = total / qty if qty else 0
                    
                    items.append({
                        "item": item_name,
                        "qty": qty,
                        "unit_price": unit_price,
                        "total": total
                    })
        
        return items
