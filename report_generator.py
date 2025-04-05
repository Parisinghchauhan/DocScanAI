import io
import json
import csv
import pandas as pd
from fpdf import FPDF
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        pass
    
    def generate_pdf_report(self, invoice_id, items, gst_breakdown):
        """
        Generate a PDF report for an invoice
        
        Args:
            invoice_id (str): ID of the invoice
            items (list): List of item dictionaries
            gst_breakdown (dict): GST breakdown by slab
            
        Returns:
            bytes: PDF report as bytes
        """
        # Create PDF object
        pdf = FPDF()
        pdf.add_page()
        
        # Set font
        pdf.set_font("Arial", "B", 16)
        
        # Title
        pdf.cell(0, 10, "GST Invoice Report", 0, 1, "C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Invoice ID: {invoice_id}", 0, 1, "C")
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "C")
        
        # Add items table
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(80, 10, "Item", 1)
        pdf.cell(20, 10, "Qty", 1)
        pdf.cell(30, 10, "Unit Price", 1)
        pdf.cell(30, 10, "Total", 1)
        pdf.cell(30, 10, "GST Rate", 1)
        pdf.ln()
        
        # Add items
        pdf.set_font("Arial", "", 10)
        total_amount = 0
        total_tax = 0
        
        for item in items:
            # Ensure item name doesn't exceed cell width
            item_name = item["item"]
            if len(item_name) > 30:
                item_name = item_name[:27] + "..."
            
            pdf.cell(80, 10, item_name, 1)
            pdf.cell(20, 10, str(item["qty"]), 1)
            pdf.cell(30, 10, f"Rs. {item['unit_price']:.2f}", 1)
            pdf.cell(30, 10, f"Rs. {item['total']:.2f}", 1)
            pdf.cell(30, 10, f"{item['gst_rate']}%", 1)
            pdf.ln()
            
            total_amount += item["total"]
            total_tax += item["total"] * (item["gst_rate"] / 100)
        
        # Add totals
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Subtotal: Rs. {total_amount:.2f}", 0, 1)
        pdf.cell(0, 10, f"Total GST: Rs. {total_tax:.2f}", 0, 1)
        pdf.cell(0, 10, f"Grand Total: Rs. {(total_amount + total_tax):.2f}", 0, 1)
        
        # Add GST breakdown
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "GST Breakdown", 0, 1)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(40, 10, "GST Rate", 1)
        pdf.cell(50, 10, "Taxable Amount", 1)
        pdf.cell(50, 10, "CGST", 1)
        pdf.cell(50, 10, "SGST", 1)
        pdf.ln()
        
        pdf.set_font("Arial", "", 10)
        for rate, details in gst_breakdown.items():
            pdf.cell(40, 10, f"{rate}%", 1)
            pdf.cell(50, 10, f"Rs. {details['taxable_amount']:.2f}", 1)
            pdf.cell(50, 10, f"Rs. {details['cgst']:.2f}", 1)
            pdf.cell(50, 10, f"Rs. {details['sgst']:.2f}", 1)
            pdf.ln()
        
        # Output the PDF to a bytes buffer
        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)
        
        return pdf_buffer.getvalue()
    
    def generate_json_report(self, invoice_id, items, gst_breakdown):
        """
        Generate a JSON report for an invoice
        
        Args:
            invoice_id (str): ID of the invoice
            items (list): List of item dictionaries
            gst_breakdown (dict): GST breakdown by slab
            
        Returns:
            str: JSON report as string
        """
        # Calculate totals
        total_amount = sum(item["total"] for item in items)
        total_tax = sum(item["total"] * (item["gst_rate"] / 100) for item in items)
        
        # Create report structure
        report = {
            "invoice_id": invoice_id,
            "generated_at": datetime.now().isoformat(),
            "items": items,
            "summary": {
                "subtotal": total_amount,
                "total_gst": total_tax,
                "grand_total": total_amount + total_tax
            },
            "gst_breakdown": gst_breakdown
        }
        
        # Convert to JSON
        return json.dumps(report, indent=4)
    
    def generate_gstr1_report(self, invoices, items):
        """
        Generate a GSTR-1 compatible CSV report
        
        Args:
            invoices (list): List of invoice dictionaries
            items (list): List of item dictionaries for all invoices
            
        Returns:
            str: CSV report as string
        """
        # Create a DataFrame for GSTR-1 B2B sales
        gstr1_data = []
        
        # Group items by invoice
        items_by_invoice = {}
        for item in items:
            invoice_id = item.get("invoice_id")
            if invoice_id not in items_by_invoice:
                items_by_invoice[invoice_id] = []
            items_by_invoice[invoice_id].append(item)
        
        # Process each invoice
        for invoice in invoices:
            invoice_id = invoice["id"]
            invoice_items = items_by_invoice.get(invoice_id, [])
            
            if not invoice_items:
                continue
            
            # Group items by GST rate
            items_by_rate = {}
            for item in invoice_items:
                rate = item.get("gst_rate", 0)
                if rate not in items_by_rate:
                    items_by_rate[rate] = []
                items_by_rate[rate].append(item)
            
            # Create GSTR-1 entries
            for rate, rate_items in items_by_rate.items():
                taxable_amount = sum(item["total"] for item in rate_items)
                gst_amount = taxable_amount * (rate / 100)
                
                gstr1_data.append({
                    "GSTIN": "PLACEHOLDER_GSTIN",  # This would be the GSTIN of the business
                    "Receiver GSTIN": "PLACEHOLDER_RECEIVER_GSTIN",  # This would be the customer's GSTIN
                    "Invoice Number": invoice_id,
                    "Invoice Date": pd.to_datetime(invoice["created_at"]).strftime("%d-%m-%Y"),
                    "Invoice Value": taxable_amount + gst_amount,
                    "Place of Supply": "PLACEHOLDER_STATE",  # This would be the state code
                    "Reverse Charge": "N",
                    "Invoice Type": "Regular",
                    "Rate": rate,
                    "Taxable Value": taxable_amount,
                    "Integrated Tax": 0,  # For interstate, this would be the full GST amount
                    "Central Tax": gst_amount / 2,  # CGST is half of total GST
                    "State/UT Tax": gst_amount / 2,  # SGST is half of total GST
                    "Cess": 0
                })
        
        if not gstr1_data:
            return "No data available for GSTR-1 report"
        
        # Convert to DataFrame and then to CSV
        df = pd.DataFrame(gstr1_data)
        
        # Output to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        
        return csv_buffer.getvalue()
