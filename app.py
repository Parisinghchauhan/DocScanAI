import os
import tempfile
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import io
import json

# Import custom modules
from database import DatabaseClient
from ocr_processor import OCRProcessor
from gst_classifier import GSTClassifier
from report_generator import ReportGenerator

# Create Flask app
app = Flask(__name__, 
            static_url_path='', 
            static_folder='static',
            template_folder='templates')
CORS(app)

# Global instances
db = DatabaseClient()
ocr_processor = OCRProcessor()
gst_classifier = GSTClassifier()
report_generator = ReportGenerator()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    try:
        invoices = db.get_invoices()
        return jsonify(invoices)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/invoice/<invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    try:
        invoice = db.get_invoice(invoice_id)
        items = db.get_items_by_invoice(invoice_id)
        
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404
            
        return jsonify({
            "invoice": invoice,
            "items": items
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/gst-slabs', methods=['GET'])
def get_gst_slabs():
    try:
        gst_slabs = db.get_gst_slabs()
        return jsonify(gst_slabs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process-invoice', methods=['POST'])
def process_invoice():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            file.save(tmp.name)
            temp_file_path = tmp.name
        
        # Extract text using OCR
        extracted_text = ocr_processor.process_file(temp_file_path)
        
        if not extracted_text:
            return jsonify({"error": "No text could be extracted from the invoice"}), 400
        
        # Extract structured data
        items_data = ocr_processor.extract_items(extracted_text)
        
        if not items_data:
            return jsonify({"error": "Could not identify item details in the invoice"}), 400
        
        # Classify items into GST slabs
        classified_items = gst_classifier.classify_items(items_data)
        
        # Save to database
        invoice_id = db.insert_invoice(
            file_name=file.filename,
            file_type=file.content_type,
            raw_text=extracted_text
        )
        
        if not invoice_id:
            return jsonify({"error": "Failed to save invoice to database"}), 500
            
        # Save classified items
        db.insert_items(invoice_id, classified_items)
        
        # Calculate GST breakdown
        gst_breakdown = {}
        for item in classified_items:
            gst_rate = item.get("gst_rate", 0)
            if gst_rate not in gst_breakdown:
                gst_breakdown[gst_rate] = {
                    "taxable_amount": 0,
                    "tax_amount": 0
                }
            
            taxable_amount = item.get("total", 0)
            tax_amount = taxable_amount * (gst_rate / 100)
            
            gst_breakdown[gst_rate]["taxable_amount"] += taxable_amount
            gst_breakdown[gst_rate]["tax_amount"] += tax_amount
            
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return jsonify({
            "success": True,
            "invoice_id": invoice_id,
            "items": classified_items,
            "gst_breakdown": gst_breakdown
        })
        
    except Exception as e:
        # Clean up in case of error
        if 'temp_file_path' in locals():
            os.unlink(temp_file_path)
            
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-item', methods=['POST'])
def update_item():
    try:
        item_data = request.json
        
        if not item_data or "id" not in item_data:
            return jsonify({"error": "Invalid item data"}), 400
            
        success = db.update_item(item_data)
        
        if not success:
            return jsonify({"error": "Failed to update item"}), 500
            
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/pdf/<invoice_id>', methods=['GET'])
def generate_pdf_report(invoice_id):
    try:
        invoice = db.get_invoice(invoice_id)
        
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404
            
        items = db.get_items_by_invoice(invoice_id)
        
        if not items:
            return jsonify({"error": "No items found for this invoice"}), 404
            
        # Calculate GST breakdown
        gst_breakdown = {}
        for item in items:
            gst_rate = item.get("gst_rate", 0)
            if gst_rate not in gst_breakdown:
                gst_breakdown[gst_rate] = {
                    "taxable_amount": 0,
                    "tax_amount": 0
                }
            
            taxable_amount = item.get("total", 0)
            tax_amount = taxable_amount * (gst_rate / 100)
            
            gst_breakdown[gst_rate]["taxable_amount"] += taxable_amount
            gst_breakdown[gst_rate]["tax_amount"] += tax_amount
            
        # Generate PDF report
        pdf_report = report_generator.generate_pdf_report(invoice_id, items, gst_breakdown)
        
        # Return PDF as file attachment
        return send_file(
            io.BytesIO(pdf_report),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"invoice_{invoice_id}_report.pdf"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/json/<invoice_id>', methods=['GET'])
def generate_json_report(invoice_id):
    try:
        invoice = db.get_invoice(invoice_id)
        
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404
            
        items = db.get_items_by_invoice(invoice_id)
        
        if not items:
            return jsonify({"error": "No items found for this invoice"}), 404
            
        # Calculate GST breakdown
        gst_breakdown = {}
        for item in items:
            gst_rate = item.get("gst_rate", 0)
            if gst_rate not in gst_breakdown:
                gst_breakdown[gst_rate] = {
                    "taxable_amount": 0,
                    "tax_amount": 0
                }
            
            taxable_amount = item.get("total", 0)
            tax_amount = taxable_amount * (gst_rate / 100)
            
            gst_breakdown[gst_rate]["taxable_amount"] += taxable_amount
            gst_breakdown[gst_rate]["tax_amount"] += tax_amount
            
        # Generate JSON report
        json_report = report_generator.generate_json_report(invoice_id, items, gst_breakdown)
        
        # Return JSON report
        return send_file(
            io.BytesIO(json_report.encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name=f"invoice_{invoice_id}_report.json"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/gstr1', methods=['POST'])
def generate_gstr1_report():
    try:
        data = request.json
        
        if not data or "start_date" not in data or "end_date" not in data:
            return jsonify({"error": "Start date and end date are required"}), 400
            
        start_date = data["start_date"]
        end_date = data["end_date"]
        
        # Fetch all invoices
        invoices = db.get_invoices()
        
        # Filter invoices by date range
        filtered_invoices = [
            inv for inv in invoices 
            if start_date <= inv["created_at"] <= end_date
        ]
        
        if not filtered_invoices:
            return jsonify({"error": "No invoices found in the selected date range"}), 404
            
        # Get items for filtered invoices
        filtered_items = []
        for invoice in filtered_invoices:
            items = db.get_items_by_invoice(invoice["id"])
            filtered_items.extend(items)
            
        # Generate GSTR-1 compatible report
        gstr1_report = report_generator.generate_gstr1_report(filtered_invoices, filtered_items)
        
        # Return CSV report
        return send_file(
            io.BytesIO(gstr1_report.encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"GSTR1_report_{start_date}_to_{end_date}.csv"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/gst-statistics', methods=['GET'])
def get_gst_statistics():
    try:
        # Fetch all invoices
        invoices = db.get_invoices()
        
        if not invoices:
            return jsonify({"error": "No invoices found"}), 404
            
        # Get all items across all invoices
        all_items = []
        for invoice in invoices:
            items = db.get_items_by_invoice(invoice["id"])
            all_items.extend(items)
            
        if not all_items:
            return jsonify({"error": "No items found across all invoices"}), 404
            
        # Calculate total tax by slab
        tax_by_slab = {}
        for item in all_items:
            slab = item.get("gst_rate", 0)
            if slab not in tax_by_slab:
                tax_by_slab[slab] = {
                    "taxable_amount": 0,
                    "tax_amount": 0
                }
            
            taxable_amount = item.get("total", 0)
            tax_amount = taxable_amount * (slab / 100)
            
            tax_by_slab[slab]["taxable_amount"] += taxable_amount
            tax_by_slab[slab]["tax_amount"] += tax_amount
            
        # Calculate total tax collected
        total_tax = sum(slab_data["tax_amount"] for slab_data in tax_by_slab.values())
        total_taxable = sum(slab_data["taxable_amount"] for slab_data in tax_by_slab.values())
            
        return jsonify({
            "tax_by_slab": tax_by_slab,
            "total_tax": total_tax,
            "total_taxable": total_taxable
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)