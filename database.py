import os
import json
import sqlite3
import uuid
from datetime import datetime

class DatabaseClient:
    def __init__(self):
        """Initialize the SQLite database client and create necessary tables."""
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Connect to SQLite database with thread safety
        self.db_path = "data/taxlyzer.db"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # This enables dictionary-like access to rows
        
        # Ensure tables exist
        self._create_tables_if_not_exist()
        
        # Populate GST slabs table if empty
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM gst_slabs")
        count = cursor.fetchone()[0]
        if count == 0:
            self._populate_gst_slabs()
    
    def _create_tables_if_not_exist(self):
        """
        Create the required tables if they don't exist:
        - invoices: Store invoice metadata
        - items: Store extracted items
        - gst_slabs: Store HSN codes and GST rates
        """
        cursor = self.conn.cursor()
        
        # Create invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id TEXT PRIMARY KEY,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                raw_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("Invoices table is ready.")
        
        # Create items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                invoice_id TEXT NOT NULL,
                item TEXT NOT NULL,
                qty NUMERIC NOT NULL,
                unit_price NUMERIC NOT NULL,
                total NUMERIC NOT NULL,
                hsn_code TEXT,
                gst_rate NUMERIC DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id)
            )
        ''')
        print("Items table is ready.")
        
        # Create gst_slabs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gst_slabs (
                id TEXT PRIMARY KEY,
                hsn_code TEXT NOT NULL,
                description TEXT,
                gst_rate NUMERIC NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("GST slabs table is ready.")
        
        # Commit changes
        self.conn.commit()
    
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
        
        cursor = self.conn.cursor()
        for hsn_data in common_hsn_codes:
            cursor.execute(
                "INSERT INTO gst_slabs (id, hsn_code, description, gst_rate) VALUES (?, ?, ?, ?)",
                (str(uuid.uuid4()), hsn_data["hsn_code"], hsn_data["description"], hsn_data["gst_rate"])
            )
        
        self.conn.commit()
        print("Populated GST slabs table with common HSN codes.")
    
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
            invoice_id = str(uuid.uuid4())
            
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO invoices (id, file_name, file_type, raw_text) VALUES (?, ?, ?, ?)",
                (invoice_id, file_name, file_type, raw_text)
            )
            
            self.conn.commit()
            return invoice_id
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
            cursor = self.conn.cursor()
            
            for item in items:
                item_id = str(uuid.uuid4())
                
                cursor.execute(
                    "INSERT INTO items (id, invoice_id, item, qty, unit_price, total, hsn_code, gst_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        item_id,
                        invoice_id,
                        item["item"],
                        item["qty"],
                        item["unit_price"],
                        item["total"],
                        item.get("hsn_code", ""),
                        item.get("gst_rate", 0)
                    )
                )
            
            self.conn.commit()
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
            
            # Prepare SET clause for SQL update
            set_clause = ", ".join([f"{key} = ?" for key in item.keys()])
            values = list(item.values()) + [item_id]
            
            cursor = self.conn.cursor()
            cursor.execute(
                f"UPDATE items SET {set_clause} WHERE id = ?",
                values
            )
            
            self.conn.commit()
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
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM invoices ORDER BY created_at DESC")
            
            # Convert rows to dictionaries
            invoices = [dict(row) for row in cursor.fetchall()]
            return invoices
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
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
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
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM items WHERE invoice_id = ?", (invoice_id,))
            
            # Convert rows to dictionaries
            items = [dict(row) for row in cursor.fetchall()]
            return items
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
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM gst_slabs")
            
            # Convert rows to dictionaries
            slabs = [dict(row) for row in cursor.fetchall()]
            return slabs
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
            
    def __del__(self):
        """Close the database connection when the object is destroyed."""
        if hasattr(self, 'conn'):
            self.conn.close()
