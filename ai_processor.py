import os
import json
from openai import OpenAI

class AIProcessor:
    def __init__(self):
        """Initialize the AI Processor with OpenAI client."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
    
    def enhance_ocr_text(self, raw_text):
        """
        Enhance OCR text using AI to fix common OCR errors
        
        Args:
            raw_text (str): Raw OCR text
            
        Returns:
            str: Enhanced text with common OCR errors fixed
        """
        try:
            prompt = f"""
            The following text was extracted using OCR from an invoice. 
            Please fix any obvious OCR errors, normalize formatting, and return the corrected text:
            
            {raw_text}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            enhanced_text = response.choices[0].message.content
            return enhanced_text
        except Exception as e:
            print(f"Error enhancing OCR text: {e}")
            return raw_text  # Fallback to original text on error
    
    def extract_structured_data(self, raw_text):
        """
        Extract structured item data from OCR text using AI
        
        Args:
            raw_text (str): OCR text (preferably enhanced)
            
        Returns:
            list: List of dictionaries containing item details
        """
        try:
            prompt = f"""
            Extract the line items from this invoice text. 
            For each item, provide:
            - item: The name/description of the item
            - qty: The quantity purchased
            - unit_price: The price per unit
            - total: The total price for this item (qty * unit_price)
            
            Return the data as a list of JSON objects. If you can't extract all fields for an item, 
            make reasonable estimates based on the available information.
            
            Invoice text:
            {raw_text}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            try:
                result = json.loads(response.choices[0].message.content)
                # Handle case where the AI might wrap the items in a parent object
                if "items" in result:
                    return result["items"]
                elif isinstance(result, list):
                    return result
                else:
                    # Try to find any array in the response
                    for key, value in result.items():
                        if isinstance(value, list) and len(value) > 0:
                            return value
                    return []
            except json.JSONDecodeError:
                # If not valid JSON, try to extract via regex as fallback
                print("AI response was not valid JSON")
                return []
                
        except Exception as e:
            print(f"Error extracting structured data: {e}")
            return []
    
    def analyze_invoice_metadata(self, raw_text):
        """
        Extract invoice metadata like invoice number, date, vendor, etc.
        
        Args:
            raw_text (str): OCR text from invoice
            
        Returns:
            dict: Dictionary with extracted metadata
        """
        try:
            prompt = f"""
            Extract the following metadata from this invoice text:
            - invoice_number: The invoice number/ID
            - invoice_date: The date of the invoice
            - vendor_name: The name of the vendor/supplier
            - total_amount: The total invoice amount
            - tax_amount: The total tax amount
            - currency: The currency used
            
            Return the data as a JSON object. If you can't find a particular field, set its value to null.
            
            Invoice text:
            {raw_text}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            metadata = json.loads(response.choices[0].message.content)
            return metadata
            
        except Exception as e:
            print(f"Error extracting invoice metadata: {e}")
            return {}
    
    def suggest_hsn_codes(self, item_descriptions):
        """
        Suggest appropriate HSN codes for item descriptions
        
        Args:
            item_descriptions (list): List of item descriptions
            
        Returns:
            dict: Dictionary mapping item descriptions to HSN codes and GST rates
        """
        try:
            prompt = f"""
            For each of the following product descriptions, suggest the most appropriate HSN code and GST rate.
            Return the results as a JSON object where the keys are the item descriptions and the values are 
            objects containing the hsn_code and gst_rate.
            
            Item descriptions:
            {json.dumps(item_descriptions)}
            
            Consider common HSN codes used in India:
            - 1905: Bread, pastry, cakes, biscuits (18%)
            - 2106: Food preparations (18%)
            - 3004: Medicaments (12%)
            - 3304: Beauty or make-up preparations (28%)
            - 3401: Soap, organic surface-active products (18%)
            - 3402: Washing and cleaning preparations (18%)
            - 3923: Plastic articles for packaging (18%)
            - 4819: Cartons, boxes, cases, bags of paper (18%)
            - 8415: Air conditioning machines (28%)
            - 8508: Vacuum cleaners (28%)
            - 8516: Electric heating equipment (28%)
            - 8517: Telephones, smartphones (18%)
            - 8528: Monitors and projectors, TV receivers (28%)
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            hsn_suggestions = json.loads(response.choices[0].message.content)
            return hsn_suggestions
            
        except Exception as e:
            print(f"Error suggesting HSN codes: {e}")
            return {}

    def get_chatbot_response(self, user_message, chat_history=None):
        """
        Get response from the chatbot using AI
        
        Args:
            user_message (str): User's message
            chat_history (list, optional): List of previous messages for context
            
        Returns:
            str: Chatbot's response
        """
        try:
            # Prepare system message with information about GST in India
            system_message = """
            You are a helpful GST assistant for TaxLyzer, an Indian invoice analysis application.
            Provide concise, accurate information about GST in India, invoice processing, and tax compliance.
            If you don't know something, say so. Base your answers on Indian tax regulations.
            Keep responses under 150 words. Use simple language that anyone can understand.
            """
            
            # Create message history including system message
            messages = [{"role": "system", "content": system_message}]
            
            # Add chat history if available
            if chat_history:
                for msg in chat_history[-10:]:  # Limit to last 10 messages for context
                    if msg.get('type') == 'user':
                        messages.append({"role": "user", "content": msg.get('content', '')})
                    elif msg.get('type') == 'bot':
                        messages.append({"role": "assistant", "content": msg.get('content', '')})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Get response from AI model
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=300  # Limit token length for cost efficiency
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error getting chatbot response: {e}")
            return "I'm having trouble connecting to my knowledge base right now. Please try again later."