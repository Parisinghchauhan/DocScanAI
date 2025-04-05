import os
import tempfile
import streamlit as st
import pandas as pd
from PIL import Image
import io

# Import custom modules
from database import DatabaseClient
from ocr_processor import OCRProcessor
from gst_classifier import GSTClassifier
from report_generator import ReportGenerator
from utils import display_invoice_summary, display_items_table, display_gst_breakdown

# Set page config
st.set_page_config(
    page_title="TaxLyzer - GST Invoice Processor",
    page_icon="📊",
    layout="wide"
)

# Initialize database client
@st.cache_resource
def init_database():
    return DatabaseClient()

# Initialize OCR processor
@st.cache_resource
def init_ocr():
    return OCRProcessor()

# Initialize GST classifier
@st.cache_resource
def init_classifier():
    return GSTClassifier()

# Initialize Report Generator
@st.cache_resource
def init_report_generator():
    return ReportGenerator()

# Main application
def main():
    try:
        db = init_database()
        ocr_processor = init_ocr()
        gst_classifier = init_classifier()
        report_generator = init_report_generator()
        
        # Application header
        st.title("TaxLyzer - Automated GST Invoice Processor")
        st.markdown("""
        Upload invoice images or PDFs to automatically extract data, 
        classify items into GST slabs, and generate tax reports.
        """)
        
        # Sidebar for navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Upload Invoice", "Invoice History", "GST Dashboard"])
        
        if page == "Upload Invoice":
            upload_invoice_page(db, ocr_processor, gst_classifier)
        elif page == "Invoice History":
            invoice_history_page(db, report_generator)
        elif page == "GST Dashboard":
            gst_dashboard_page(db, report_generator)
    except Exception as e:
        st.error(f"Error initializing application: {str(e)}")
        st.info("If there's a database error, the system will try to create the necessary tables automatically.")

def upload_invoice_page(db, ocr_processor, gst_classifier):
    st.header("Upload Invoice")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload invoice image or PDF", 
        type=["jpg", "jpeg", "png", "pdf"]
    )
    
    if uploaded_file is not None:
        # Display uploaded file
        if uploaded_file.type.startswith('image'):
            st.image(uploaded_file, caption="Uploaded Invoice", use_container_width=True)
        else:
            st.info("PDF uploaded successfully.")
        
        # Process button
        if st.button("Extract Data from Invoice"):
            with st.spinner("Processing invoice..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    temp_file_path = tmp.name
                
                try:
                    # Extract text using OCR
                    extracted_text = ocr_processor.process_file(temp_file_path)
                    
                    if not extracted_text:
                        st.error("No text could be extracted from the invoice. Please try with a clearer image.")
                        return
                    
                    # Extract structured data
                    items_data = ocr_processor.extract_items(extracted_text)
                    
                    if not items_data:
                        st.error("Could not identify item details in the invoice. Please try with a different invoice.")
                        return
                    
                    # Classify items into GST slabs
                    classified_items = gst_classifier.classify_items(items_data)
                    
                    # Save to database
                    invoice_id = db.insert_invoice(
                        file_name=uploaded_file.name,
                        file_type=uploaded_file.type,
                        raw_text=extracted_text
                    )
                    
                    if invoice_id:
                        db.insert_items(invoice_id, classified_items)
                        
                        # Display results
                        st.success("Invoice processed successfully!")
                        
                        # Display extracted items
                        st.subheader("Extracted Items")
                        items_df = pd.DataFrame(classified_items)
                        st.dataframe(items_df)
                        
                        # Allow manual corrections
                        st.subheader("Manual Corrections")
                        st.info("You can make corrections to extracted data by selecting an item below.")
                        
                        selected_item_idx = st.selectbox(
                            "Select an item to edit:",
                            range(len(classified_items)),
                            format_func=lambda i: classified_items[i]["item"]
                        )
                        
                        # Get current values for the selected item
                        current_item = classified_items[selected_item_idx]
                        
                        # Create form for editing
                        with st.form(key=f"edit_item_{selected_item_idx}"):
                            item_name = st.text_input("Item Name", value=current_item["item"])
                            qty = st.number_input("Quantity", value=current_item["qty"], min_value=0.0, format="%f")
                            unit_price = st.number_input("Unit Price", value=current_item["unit_price"], min_value=0.0, format="%f")
                            
                            # GST slab selection
                            gst_slabs = [0, 5, 12, 18, 28]
                            selected_slab = st.selectbox(
                                "GST Slab (%)", 
                                gst_slabs,
                                index=gst_slabs.index(current_item["gst_rate"]) if current_item["gst_rate"] in gst_slabs else 0
                            )
                            
                            # HSN code
                            hsn_code = st.text_input("HSN Code", value=current_item.get("hsn_code", ""))
                            
                            submit_btn = st.form_submit_button("Update Item")
                            
                            if submit_btn:
                                # Update the item in the database
                                updated_item = {
                                    "id": current_item.get("id"),
                                    "item": item_name,
                                    "qty": qty,
                                    "unit_price": unit_price,
                                    "total": qty * unit_price,
                                    "gst_rate": selected_slab,
                                    "hsn_code": hsn_code
                                }
                                
                                db.update_item(updated_item)
                                st.success(f"Item '{item_name}' updated successfully!")
                                st.rerun()
                        
                        # GST Summary
                        st.subheader("GST Summary")
                        gst_breakdown = display_gst_breakdown(classified_items)
                        
                        # Generate report button
                        if st.button("Generate GST Report"):
                            with st.spinner("Generating report..."):
                                # Create a report generator instance for this report
                                report_gen = init_report_generator()
                                pdf_report = report_gen.generate_pdf_report(invoice_id, classified_items, gst_breakdown)
                                json_report = report_gen.generate_json_report(invoice_id, classified_items, gst_breakdown)
                                
                                # Provide download buttons
                                st.download_button(
                                    label="Download PDF Report",
                                    data=pdf_report,
                                    file_name=f"invoice_{invoice_id}_report.pdf",
                                    mime="application/pdf"
                                )
                                
                                st.download_button(
                                    label="Download JSON Report",
                                    data=json_report,
                                    file_name=f"invoice_{invoice_id}_report.json",
                                    mime="application/json"
                                )
                    else:
                        st.error("Failed to save invoice to database.")
                
                except Exception as e:
                    st.error(f"Error processing invoice: {str(e)}")
                
                finally:
                    # Clean up the temporary file
                    os.unlink(temp_file_path)

def invoice_history_page(db, report_generator):
    st.header("Invoice History")
    
    # Fetch invoices from database
    invoices = db.get_invoices()
    
    if not invoices:
        st.info("No invoices found. Upload your first invoice to get started!")
        return
    
    # Display invoices in a table
    invoices_df = pd.DataFrame(invoices)
    st.dataframe(invoices_df[["id", "file_name", "created_at"]])
    
    # Allow user to select an invoice to view details
    selected_invoice_id = st.selectbox(
        "Select an invoice to view details:",
        invoices_df["id"].tolist(),
        format_func=lambda x: next((inv["file_name"] for inv in invoices if inv["id"] == x), "")
    )
    
    if selected_invoice_id:
        # Fetch items for the selected invoice
        items = db.get_items_by_invoice(selected_invoice_id)
        
        if items:
            # Display invoice summary
            st.subheader("Invoice Summary")
            display_invoice_summary(selected_invoice_id, invoices, items)
            
            # Display items
            st.subheader("Invoice Items")
            display_items_table(items)
            
            # GST breakdown
            st.subheader("GST Breakdown")
            gst_breakdown = display_gst_breakdown(items)
            
            # Generate reports
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Generate PDF Report"):
                    with st.spinner("Generating PDF report..."):
                        pdf_report = report_generator.generate_pdf_report(selected_invoice_id, items, gst_breakdown)
                        
                        st.download_button(
                            label="Download PDF Report",
                            data=pdf_report,
                            file_name=f"invoice_{selected_invoice_id}_report.pdf",
                            mime="application/pdf"
                        )
            
            with col2:
                if st.button("Generate JSON Report"):
                    with st.spinner("Generating JSON report..."):
                        json_report = report_generator.generate_json_report(selected_invoice_id, items, gst_breakdown)
                        
                        st.download_button(
                            label="Download JSON Report",
                            data=json_report,
                            file_name=f"invoice_{selected_invoice_id}_report.json",
                            mime="application/json"
                        )
        else:
            st.info("No items found for this invoice.")

def gst_dashboard_page(db, report_generator):
    st.header("GST Dashboard")
    
    # Fetch all invoices and items
    invoices = db.get_invoices()
    
    if not invoices:
        st.info("No invoices found. Upload your first invoice to get started!")
        return
    
    # Get all items across all invoices
    all_items = []
    for invoice in invoices:
        items = db.get_items_by_invoice(invoice["id"])
        all_items.extend(items)
    
    if not all_items:
        st.info("No items found across all invoices.")
        return
    
    # Display GST statistics
    st.subheader("GST Statistics")
    
    # Calculate total tax by slab
    tax_by_slab = {}
    for item in all_items:
        slab = item.get("gst_rate", 0)
        if slab not in tax_by_slab:
            tax_by_slab[slab] = 0
        
        # Calculate GST amount for this item
        item_total = item.get("total", 0)
        gst_amount = item_total * (slab / 100)
        tax_by_slab[slab] += gst_amount
    
    # Convert to DataFrame for visualization
    tax_df = pd.DataFrame({
        "GST Slab (%)": tax_by_slab.keys(),
        "Tax Amount (₹)": tax_by_slab.values()
    })
    
    # Bar chart for tax by slab
    st.bar_chart(tax_df.set_index("GST Slab (%)"))
    
    # Display total tax collected
    total_tax = sum(tax_by_slab.values())
    st.metric("Total GST Collected", f"₹{total_tax:.2f}")
    
    # GSTR-1 report generation
    st.subheader("Generate GSTR-1 Report")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date")
    with col2:
        end_date = st.date_input("End Date")
    
    if start_date and end_date:
        if st.button("Generate GSTR-1 Report"):
            with st.spinner("Generating GSTR-1 report..."):
                # Filter invoices by date range
                filtered_invoices = [
                    inv for inv in invoices 
                    if start_date <= pd.to_datetime(inv["created_at"]).date() <= end_date
                ]
                
                if not filtered_invoices:
                    st.warning("No invoices found in the selected date range.")
                    return
                
                # Get items for filtered invoices
                filtered_items = []
                for invoice in filtered_invoices:
                    items = db.get_items_by_invoice(invoice["id"])
                    filtered_items.extend(items)
                
                # Generate GSTR-1 compatible report
                gstr1_report = report_generator.generate_gstr1_report(filtered_invoices, filtered_items)
                
                st.download_button(
                    label="Download GSTR-1 Report",
                    data=gstr1_report,
                    file_name=f"GSTR1_report_{start_date}_to_{end_date}.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()
