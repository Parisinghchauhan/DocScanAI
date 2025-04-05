import os
import tempfile
import threading
import datetime
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import io
import json
import uuid

# Import custom modules
from database import DatabaseClient
from ocr_processor import OCRProcessor
from gst_classifier import GSTClassifier
from report_generator import ReportGenerator
from trend_analyzer import TrendAnalyzer
from ai_processor import AIProcessor

# For batch processing
batch_jobs = {}

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
trend_analyzer = TrendAnalyzer(db)
ai_processor = AIProcessor()

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

@app.route('/api/batch/process', methods=['POST'])
def batch_process_invoices():
    if 'files' not in request.files:
        return jsonify({"error": "No files part"}), 400
        
    files = request.files.getlist('files')
    
    if not files or len(files) == 0 or files[0].filename == '':
        return jsonify({"error": "No files selected"}), 400
    
    # Create a batch job
    batch_id = str(uuid.uuid4())
    file_names = [file.filename for file in files]
    
    # Save files temporarily
    temp_files = []
    for file in files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            file.save(tmp.name)
            temp_files.append({
                'path': tmp.name,
                'name': file.filename,
                'content_type': file.content_type
            })
    
    # Create batch job entry
    batch_jobs[batch_id] = {
        'id': batch_id,
        'status': 'processing',
        'total_files': len(files),
        'processed_files': 0,
        'successful_files': 0,
        'failed_files': 0,
        'started_at': str(datetime.datetime.now()),
        'completed_at': None,
        'results': [],
        'files': file_names
    }
    
    # Start processing in background
    thread = threading.Thread(
        target=_process_batch, 
        args=(batch_id, temp_files)
    )
    thread.daemon = True  # Daemon threads are killed when the main program exits
    thread.start()
    
    return jsonify({
        "success": True,
        "batch_id": batch_id,
        "message": f"Processing {len(files)} files in the background",
        "total_files": len(files)
    })

def _process_batch(batch_id, temp_files):
    """Background task to process multiple invoice files"""
    batch_info = batch_jobs[batch_id]
    
    try:
        for file_info in temp_files:
            try:
                # Extract text using OCR
                extracted_text = ocr_processor.process_file(file_info['path'])
                
                if not extracted_text:
                    batch_info['failed_files'] += 1
                    batch_info['results'].append({
                        'file_name': file_info['name'],
                        'success': False,
                        'error': "No text could be extracted from the invoice"
                    })
                    continue
                
                # Extract structured data
                items_data = ocr_processor.extract_items(extracted_text)
                
                if not items_data:
                    batch_info['failed_files'] += 1
                    batch_info['results'].append({
                        'file_name': file_info['name'],
                        'success': False,
                        'error': "Could not identify item details in the invoice"
                    })
                    continue
                
                # Classify items into GST slabs
                classified_items = gst_classifier.classify_items(items_data)
                
                # Save to database
                invoice_id = db.insert_invoice(
                    file_name=file_info['name'],
                    file_type=file_info['content_type'],
                    raw_text=extracted_text
                )
                
                if not invoice_id:
                    batch_info['failed_files'] += 1
                    batch_info['results'].append({
                        'file_name': file_info['name'],
                        'success': False,
                        'error': "Failed to save invoice to database"
                    })
                    continue
                
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
                
                # Record success
                batch_info['successful_files'] += 1
                batch_info['results'].append({
                    'file_name': file_info['name'],
                    'success': True,
                    'invoice_id': invoice_id,
                    'items_count': len(classified_items)
                })
                
            except Exception as e:
                # Record failure
                batch_info['failed_files'] += 1
                batch_info['results'].append({
                    'file_name': file_info['name'],
                    'success': False,
                    'error': str(e)
                })
            
            finally:
                # Cleanup temp file
                try:
                    os.unlink(file_info['path'])
                except:
                    pass
                
                # Update progress
                batch_info['processed_files'] += 1
        
        # Mark batch as completed
        batch_info['status'] = 'completed'
        batch_info['completed_at'] = str(datetime.datetime.now())
        
    except Exception as e:
        # Mark batch as failed
        batch_info['status'] = 'failed'
        batch_info['error'] = str(e)
        batch_info['completed_at'] = str(datetime.datetime.now())
        
        # Clean up any remaining temp files
        for file_info in temp_files:
            try:
                if os.path.exists(file_info['path']):
                    os.unlink(file_info['path'])
            except:
                pass

@app.route('/api/batch/status/<batch_id>', methods=['GET'])
def get_batch_status(batch_id):
    if batch_id not in batch_jobs:
        return jsonify({"error": "Batch job not found"}), 404
    
    return jsonify(batch_jobs[batch_id])

@app.route('/api/batch/list', methods=['GET'])
def list_batch_jobs():
    # Return basic info about all batch jobs
    batch_summaries = []
    for job_id, job_info in batch_jobs.items():
        batch_summaries.append({
            'id': job_id,
            'status': job_info['status'],
            'total_files': job_info['total_files'],
            'processed_files': job_info['processed_files'],
            'successful_files': job_info['successful_files'],
            'failed_files': job_info['failed_files'],
            'started_at': job_info['started_at'],
            'completed_at': job_info['completed_at']
        })
    
    return jsonify(batch_summaries)

@app.route('/api/gst-statistics', methods=['GET'])
def get_gst_statistics():
    try:
        # Get time range filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Fetch all invoices
        invoices = db.get_invoices()
        
        if not invoices:
            # Return empty stats instead of 404 for better UI handling
            return jsonify({
                "tax_by_slab": {},
                "total_tax": 0,
                "total_taxable": 0,
                "invoice_count": 0
            })
            
        # Apply date filtering if provided
        if start_date and end_date:
            invoices = [
                inv for inv in invoices 
                if start_date <= inv["created_at"] <= end_date
            ]
            
        # Get all items across all invoices
        all_items = []
        for invoice in invoices:
            items = db.get_items_by_invoice(invoice["id"])
            all_items.extend(items)
            
        if not all_items:
            # Return empty stats instead of 404 for better UI handling
            return jsonify({
                "tax_by_slab": {},
                "total_tax": 0,
                "total_taxable": 0,
                "invoice_count": len(invoices)
            })
            
        # Calculate total tax by slab
        tax_by_slab = {}
        for item in all_items:
            slab = item.get("gst_rate", 0)
            if slab not in tax_by_slab:
                tax_by_slab[slab] = {
                    "taxable_amount": 0,
                    "tax_amount": 0,
                    "item_count": 0
                }
            
            taxable_amount = item.get("total", 0)
            tax_amount = taxable_amount * (slab / 100)
            
            tax_by_slab[slab]["taxable_amount"] += taxable_amount
            tax_by_slab[slab]["tax_amount"] += tax_amount
            tax_by_slab[slab]["item_count"] += 1
            
        # Calculate total tax collected
        total_tax = sum(slab_data["tax_amount"] for slab_data in tax_by_slab.values())
        total_taxable = sum(slab_data["taxable_amount"] for slab_data in tax_by_slab.values())
            
        return jsonify({
            "tax_by_slab": tax_by_slab,
            "total_tax": total_tax,
            "total_taxable": total_taxable,
            "invoice_count": len(invoices),
            "item_count": len(all_items)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trend-analysis', methods=['GET'])
def get_trend_analysis():
    try:
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        group_by = request.args.get('group_by', 'month')  # Default to monthly grouping
        
        # Validate group_by parameter
        valid_group_by = ['day', 'week', 'month', 'quarter']
        if group_by not in valid_group_by:
            return jsonify({"error": f"Invalid group_by parameter. Must be one of: {', '.join(valid_group_by)}"}), 400
        
        # Run trend analysis
        trend_data = trend_analyzer.analyze_historical_trends(
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )
        
        return jsonify(trend_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/slab-distribution', methods=['GET'])
def get_slab_distribution():
    try:
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Run trend analysis with focus on slab distribution
        trend_data = trend_analyzer.analyze_historical_trends(
            start_date=start_date,
            end_date=end_date
        )
        
        # Extract just the slab distribution part
        return jsonify(trend_data.get("slab_distribution", []))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/top-hsn-codes', methods=['GET'])
def get_top_hsn_codes():
    try:
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 10)
        
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
            
        # Run trend analysis
        trend_data = trend_analyzer.analyze_historical_trends(
            start_date=start_date,
            end_date=end_date
        )
        
        # Extract just the top HSN codes part
        return jsonify(trend_data.get("top_hsn_codes", [])[:limit])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Chatbot endpoint
@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.json
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
            
        user_message = data['message']
        
        # Get chat history context if available
        chat_history = data.get('history', [])
        
        # Use AI processor to get response
        response = ai_processor.get_chatbot_response(user_message, chat_history)
        
        return jsonify({
            'response': response
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)