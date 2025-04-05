import re
import os
import csv
import json
import pandas as pd
from fuzzywuzzy import fuzz

# Check if AI processor is available
try:
    from ai_processor import AIProcessor
    ai_available = True
except ImportError:
    ai_available = False

class GSTClassifier:
    def __init__(self):
        # Load HSN codes and GST rates
        self.hsn_data = self._load_hsn_data()
        
        # Initialize AI processor if available
        if ai_available:
            try:
                self.ai_processor = AIProcessor()
                self.use_ai = True
                print("AI processing enabled for enhanced GST classification")
            except Exception as e:
                print(f"AI GST classification not available: {e}")
                self.use_ai = False
        else:
            self.use_ai = False
            
        # Keywords to help identify item categories
        self.category_keywords = {
            "food": ["biscuit", "cookie", "cake", "bread", "rice", "wheat", "flour", "sugar", "milk", "curd", "cheese",
                      "butter", "ghee", "oil", "tea", "coffee", "spice", "masala", "sauce", "ketchup", "jam", "juice",
                      "water", "soft drink", "snack", "chocolate", "candy", "sweet", "namkeen", "chips"],
            "electronics": ["tv", "television", "laptop", "computer", "phone", "mobile", "tablet", "refrigerator", "fridge",
                           "washing machine", "dishwasher", "microwave", "oven", "ac", "air conditioner", "fan", "heater",
                           "mixer", "grinder", "iron", "camera", "speaker", "headphone", "earphone", "charger", "battery"],
            "clothing": ["shirt", "t-shirt", "trouser", "pant", "jeans", "dress", "skirt", "saree", "sari", "kurta",
                        "pajama", "underwear", "sock", "shoe", "sandal", "chappal", "hat", "cap", "belt", "tie"],
            "cosmetics": ["soap", "shampoo", "conditioner", "face wash", "moisturizer", "cream", "lotion", "oil",
                         "sunscreen", "perfume", "deodorant", "talcum", "powder", "makeup", "lipstick", "nail polish",
                         "hair color", "hair dye"],
            "furniture": ["chair", "table", "desk", "sofa", "bed", "mattress", "pillow", "cushion", "cabinet", "shelf",
                          "bookshelf", "wardrobe", "almirah", "mirror", "clock"],
            "stationery": ["pen", "pencil", "marker", "highlighter", "notebook", "copy", "paper", "book", "diary",
                          "calendar", "file", "folder", "stapler", "puncher", "tape", "glue", "scissor"]
        }
        
        # Mapping from categories to GST rates
        self.category_to_gst = {
            "food": 5,  # Most food items are in 5% slab, but some are higher
            "electronics": 18,  # Most electronics are in 18% slab, but some luxury items are 28%
            "clothing": 5,  # Clothing below Rs. 1000 is 5%, above is 12%
            "cosmetics": 18,  # Most cosmetics are 18%
            "furniture": 18,  # Most furniture is 18%
            "stationery": 12  # Most stationery is 12%
        }
        
        # Some specific items with known GST rates
        self.specific_items = {
            "mobile phone": {"gst_rate": 18, "hsn_code": "8517"},
            "television": {"gst_rate": 28, "hsn_code": "8528"},
            "air conditioner": {"gst_rate": 28, "hsn_code": "8415"},
            "refrigerator": {"gst_rate": 28, "hsn_code": "8418"},
            "washing machine": {"gst_rate": 28, "hsn_code": "8450"},
            "parle-g": {"gst_rate": 18, "hsn_code": "1905"},
            "britannia": {"gst_rate": 18, "hsn_code": "1905"}
        }
    
    def _load_hsn_data(self):
        """
        Load HSN code data from CSV
        
        Returns:
            pandas.DataFrame: DataFrame containing HSN codes and GST rates
        """
        # Try to load from data directory first
        data_file = os.path.join("data", "hsn_codes.csv")
        
        if os.path.exists(data_file):
            return pd.read_csv(data_file)
        
        # If file doesn't exist, create a basic dataset
        data = {
            "hsn_code": [
                "1905", "2106", "3004", "3304", "3401", "3402", "3923", 
                "4819", "8415", "8508", "8516", "8517", "8528"
            ],
            "description": [
                "Bread, pastry, cakes, biscuits", "Food preparations", "Medicaments",
                "Beauty or make-up preparations", "Soap, organic surface-active products",
                "Washing and cleaning preparations", "Plastic articles for packaging",
                "Cartons, boxes, cases, bags of paper", "Air conditioning machines",
                "Vacuum cleaners", "Electric heating equipment", "Telephones, smartphones",
                "Monitors and projectors, TV receivers"
            ],
            "gst_rate": [
                18, 18, 12, 28, 18, 18, 18, 18, 28, 28, 28, 18, 28
            ]
        }
        
        df = pd.DataFrame(data)
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Save to CSV for future use
        df.to_csv(data_file, index=False)
        
        return df
    
    def classify_items(self, items):
        """
        Classify items into GST slabs
        
        Args:
            items (list): List of dictionaries containing item details
            
        Returns:
            list: List of dictionaries with GST details added
        """
        # If AI is available, try to use it for classification
        if hasattr(self, 'use_ai') and self.use_ai:
            try:
                # Extract item descriptions for AI classification
                item_descriptions = [item["item"] for item in items]
                
                # Get AI suggestions for HSN codes and GST rates
                hsn_suggestions = self.ai_processor.suggest_hsn_codes(item_descriptions)
                
                if hsn_suggestions:
                    # Apply AI suggestions
                    classified_items = []
                    for item in items:
                        item_name = item["item"]
                        if item_name in hsn_suggestions:
                            suggestion = hsn_suggestions[item_name]
                            item["hsn_code"] = suggestion.get("hsn_code", "")
                            item["gst_rate"] = suggestion.get("gst_rate", 18)
                        else:
                            # Fall back to traditional classification if item not found
                            self._traditional_classify_item(item)
                        
                        classified_items.append(item)
                    
                    print(f"AI successfully classified {len(classified_items)} items")
                    return classified_items
                
            except Exception as e:
                print(f"AI-based classification failed: {e}")
                # Fall back to traditional classification
        
        # Traditional classification approach
        classified_items = []
        for item in items:
            self._traditional_classify_item(item)
            classified_items.append(item)
            
        return classified_items
        
    def _traditional_classify_item(self, item):
        """Helper method for traditional classification logic"""
        item_name = item["item"].lower()
        
        # Check if item is in specific items list
        for specific_item, details in self.specific_items.items():
            if specific_item in item_name:
                item["gst_rate"] = details["gst_rate"]
                item["hsn_code"] = details["hsn_code"]
                return
                
        # If not found in specific items, try to match with HSN data
        hsn_code, gst_rate = self._match_with_hsn(item_name)
        
        if hsn_code:
            item["hsn_code"] = hsn_code
            item["gst_rate"] = gst_rate
        else:
            # If not found in HSN data, use category-based classification
            category = self._identify_category(item_name)
            
            if category:
                item["gst_rate"] = self.category_to_gst.get(category, 18)  # Default to 18% if category not found
            else:
                # Default GST rate if nothing matches
                item["gst_rate"] = 18
    
    def _match_with_hsn(self, item_name):
        """
        Try to match item name with HSN descriptions
        
        Args:
            item_name (str): Name of the item
            
        Returns:
            tuple: (hsn_code, gst_rate) or (None, None) if not found
        """
        best_match = None
        best_score = 0
        
        for _, row in self.hsn_data.iterrows():
            description = row["description"].lower()
            
            # Check if any word in the description is in the item name
            for word in description.split():
                if word in item_name and len(word) > 3:  # Only consider words longer than 3 characters
                    score = fuzz.token_sort_ratio(description, item_name)
                    
                    if score > best_score:
                        best_score = score
                        best_match = row
        
        # Only consider a match if the score is above a threshold
        if best_score > 60:
            return best_match["hsn_code"], best_match["gst_rate"]
        
        return None, None
    
    def _identify_category(self, item_name):
        """
        Identify the category of an item based on keywords
        
        Args:
            item_name (str): Name of the item
            
        Returns:
            str: Category or None if not identified
        """
        best_category = None
        best_match_count = 0
        
        for category, keywords in self.category_keywords.items():
            match_count = 0
            
            for keyword in keywords:
                if keyword in item_name:
                    match_count += 1
            
            if match_count > best_match_count:
                best_match_count = match_count
                best_category = category
        
        # Only consider a category match if at least one keyword matched
        if best_match_count > 0:
            return best_category
        
        return None
