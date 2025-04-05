import os
import json
from supabase import create_client
from datetime import datetime

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "")
        self.key = os.getenv("SUPABASE_KEY", "")
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and API key must be provided as environment variables.")
        
        self.client = create_client(self.url, self.key)
        
        # Ensure tables exist
        self._create_tables_if_not_exist()
    
    def _create_tables_if_not_exist(self):
        """
        Create the required tables if they don't exist:
        - invoices: Store invoice metadata
        - items: Store extracted items
        - gst_slabs: Store HSN codes and GST rates
        """
        # In Supabase, we're using the REST API which doesn't support direct SQL execution
        # Instead, let's create tables through the Supabase UI or management console
        # For this project, we'll assume tables are already created in Supabase
        
        # Check if tables exist
        try:
            # Try to access invoices table
            self.client.table("invoices").select("id").limit(1).execute()
            print("Invoices table exists.")
        except Exception as e:
            print(f"Error accessing invoices table: {e}")
            print("Please create the invoices table in Supabase with the following structure:")
            print("""
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                raw_text TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            """)
        
        try:
            # Try to access items table
            self.client.table("items").select("id").limit(1).execute()
            print("Items table exists.")
        except Exception as e:
            print(f"Error accessing items table: {e}")
            print("Please create the items table in Supabase with the following structure:")
            print("""
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                invoice_id UUID REFERENCES invoices(id),
                item TEXT NOT NULL,
                qty NUMERIC NOT NULL,
                unit_price NUMERIC NOT NULL,
                total NUMERIC NOT NULL,
                hsn_code TEXT,
                gst_rate NUMERIC DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            """)
        
        try:
            # Try to access gst_slabs table
            self.client.table("gst_slabs").select("id").limit(1).execute()
            print("GST slabs table exists.")
        except Exception as e:
            print(f"Error accessing gst_slabs table: {e}")
            print("Please create the gst_slabs table in Supabase with the following structure:")
            print("""
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                hsn_code TEXT NOT NULL,
                description TEXT,
                gst_rate NUMERIC NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            """)
            
            # For now, we'll skip populating GST slabs since the table might not exist
            # We'll handle this in the UI by providing fallback classification
    
    def _populate_gst_slabs(self):
        """Populate the gst_slabs table with common HSN codes."""
        common_hsn_codes = [
            {"hsn_code": "1905", "description": "Bread, pastry, cakes, biscuits", "gst_rate": 18},
            {"hsn_code": "2106", "description": "Food preparations", "gst_rate": 18},
            {"hsn_code": "3004", "description": "Medicaments", "gst_rate": 12},
            {"hsn_code": "3304", "description": "Beauty or make-up preparations", "gst_rate": 28},
            {"hsn_code": "3401", "description": "Soap, organic surface-active products", "gst_rate": 18},
            {"hsn_code": "3402", "description": "Washing and cleaning preparations", "gst_rate": 18},
            {"hsn_code": "3923", "description": "Plastic articles for packaging", "gst_rate": 18},
            {"hsn_code": "4819", "description": "Cartons, boxes, cases, bags of paper", "gst_rate": 18},
            {"hsn_code": "8415", "description": "Air conditioning machines", "gst_rate": 28},
            {"hsn_code": "8508", "description": "Vacuum cleaners", "gst_rate": 28},
            {"hsn_code": "8516", "description": "Electric heating equipment", "gst_rate": 28},
            {"hsn_code": "8517", "description": "Telephones, smartphones", "gst_rate": 18},
            {"hsn_code": "8528", "description": "Monitors and projectors, TV receivers", "gst_rate": 28},
            # Add more common HSN codes as needed
        ]
        
        for hsn_data in common_hsn_codes:
            self.client.table("gst_slabs").insert(hsn_data).execute()
    
    def insert_invoice(self, file_name, file_type, raw_text):
        """
        Insert a new invoice into the database
        
        Args:
            file_name (str): Name of the uploaded file
            file_type (str): MIME type of the file
            raw_text (str): Extracted raw text from OCR
            
        Returns:
            str: ID of the inserted invoice, or None if failed
        """
        try:
            result = self.client.table("invoices").insert({
                "file_name": file_name,
                "file_type": file_type,
                "raw_text": raw_text
            }).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]["id"]
            return None
        except Exception as e:
            print(f"Error inserting invoice: {e}")
            return None
    
    def insert_items(self, invoice_id, items):
        """
        Insert extracted items for an invoice
        
        Args:
            invoice_id (str): ID of the invoice
            items (list): List of dictionaries containing item details
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for item in items:
                item_data = {
                    "invoice_id": invoice_id,
                    "item": item["item"],
                    "qty": item["qty"],
                    "unit_price": item["unit_price"],
                    "total": item["total"],
                    "hsn_code": item.get("hsn_code", ""),
                    "gst_rate": item.get("gst_rate", 0)
                }
                
                self.client.table("items").insert(item_data).execute()
            
            return True
        except Exception as e:
            print(f"Error inserting items: {e}")
            return False
    
    def update_item(self, item):
        """
        Update an existing item
        
        Args:
            item (dict): Dictionary containing updated item details
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if "id" not in item:
                return False
            
            item_id = item.pop("id")
            
            self.client.table("items").update(item).eq("id", item_id).execute()
            
            return True
        except Exception as e:
            print(f"Error updating item: {e}")
            return False
    
    def get_invoices(self):
        """
        Get all invoices from the database
        
        Returns:
            list: List of invoice dictionaries
        """
        try:
            result = self.client.table("invoices").select("*").order("created_at", desc=True).execute()
            
            if result.data:
                return result.data
            return []
        except Exception as e:
            print(f"Error getting invoices: {e}")
            return []
    
    def get_invoice(self, invoice_id):
        """
        Get a specific invoice by ID
        
        Args:
            invoice_id (str): ID of the invoice
            
        Returns:
            dict: Invoice details
        """
        try:
            result = self.client.table("invoices").select("*").eq("id", invoice_id).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            print(f"Error getting invoice: {e}")
            return None
    
    def get_items_by_invoice(self, invoice_id):
        """
        Get all items for a specific invoice
        
        Args:
            invoice_id (str): ID of the invoice
            
        Returns:
            list: List of item dictionaries
        """
        try:
            result = self.client.table("items").select("*").eq("invoice_id", invoice_id).execute()
            
            if result.data:
                return result.data
            return []
        except Exception as e:
            print(f"Error getting items: {e}")
            return []
    
    def get_gst_slabs(self):
        """
        Get all GST slabs from the database
        
        Returns:
            list: List of GST slab dictionaries
        """
        try:
            result = self.client.table("gst_slabs").select("*").execute()
            
            if result.data:
                return result.data
            return []
        except Exception as e:
            print(f"Error getting GST slabs: {e}")
            return []
    
    def get_hsn_code_for_item(self, item_name):
        """
        Get the most appropriate HSN code for an item based on the description
        
        Args:
            item_name (str): Name of the item
            
        Returns:
            tuple: (hsn_code, gst_rate) or (None, 0) if not found
        """
        try:
            # This is a simplified approach; in a real system, use more sophisticated matching
            gst_slabs = self.get_gst_slabs()
            
            # Convert item name to lowercase for case-insensitive matching
            item_name_lower = item_name.lower()
            
            for slab in gst_slabs:
                description = slab.get("description", "").lower()
                
                # Check if any word in the description is in the item name
                if any(word in item_name_lower for word in description.split()):
                    return slab["hsn_code"], slab["gst_rate"]
            
            # Default return
            return None, 0
        except Exception as e:
            print(f"Error finding HSN code: {e}")
            return None, 0
