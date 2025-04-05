import streamlit as st
import pandas as pd
from datetime import datetime

def display_invoice_summary(invoice_id, invoices, items):
    """
    Display a summary of an invoice
    
    Args:
        invoice_id (str): ID of the invoice
        invoices (list): List of all invoices
        items (list): List of items for the invoice
    """
    # Find the invoice in the list
    invoice = next((inv for inv in invoices if inv["id"] == invoice_id), None)
    
    if not invoice:
        st.error("Invoice not found")
        return
    
    # Calculate totals
    total_amount = sum(item["total"] for item in items)
    total_tax = sum(item["total"] * (item["gst_rate"] / 100) for item in items)
    grand_total = total_amount + total_tax
    
    # Display summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Invoice ID", invoice_id)
        st.metric("File Name", invoice["file_name"])
        st.metric("Date", pd.to_datetime(invoice["created_at"]).strftime("%Y-%m-%d"))
    
    with col2:
        st.metric("Subtotal", f"₹{total_amount:.2f}")
        st.metric("Total GST", f"₹{total_tax:.2f}")
        st.metric("Grand Total", f"₹{grand_total:.2f}")

def display_items_table(items):
    """
    Display a table of invoice items
    
    Args:
        items (list): List of items to display
    """
    # Convert to DataFrame for display
    df = pd.DataFrame(items)
    
    # Select and rename columns for display
    if "id" in df.columns and "invoice_id" in df.columns:
        display_df = df[["item", "qty", "unit_price", "total", "hsn_code", "gst_rate"]]
    else:
        display_df = df
    
    # Format the DataFrame
    if "unit_price" in display_df.columns:
        display_df["unit_price"] = display_df["unit_price"].apply(lambda x: f"₹{x:.2f}")
    
    if "total" in display_df.columns:
        display_df["total"] = display_df["total"].apply(lambda x: f"₹{x:.2f}")
    
    if "gst_rate" in display_df.columns:
        display_df["gst_rate"] = display_df["gst_rate"].apply(lambda x: f"{x}%")
    
    # Rename columns for display
    column_map = {
        "item": "Item",
        "qty": "Quantity",
        "unit_price": "Unit Price",
        "total": "Total",
        "hsn_code": "HSN Code",
        "gst_rate": "GST Rate"
    }
    
    display_df = display_df.rename(columns=column_map)
    
    # Display the table
    st.dataframe(display_df)

def display_gst_breakdown(items):
    """
    Display a breakdown of GST by slab
    
    Args:
        items (list): List of items to calculate GST for
        
    Returns:
        dict: GST breakdown by slab
    """
    # Group items by GST rate
    gst_slabs = {}
    
    for item in items:
        rate = item.get("gst_rate", 0)
        
        if rate not in gst_slabs:
            gst_slabs[rate] = {
                "taxable_amount": 0,
                "cgst": 0,
                "sgst": 0,
                "igst": 0
            }
        
        # Add item total to taxable amount
        gst_slabs[rate]["taxable_amount"] += item["total"]
        
        # Calculate GST
        gst_amount = item["total"] * (rate / 100)
        
        # Split into CGST and SGST (assuming intra-state supply)
        gst_slabs[rate]["cgst"] += gst_amount / 2
        gst_slabs[rate]["sgst"] += gst_amount / 2
    
    # Create a table for display
    breakdown_data = []
    for rate, values in gst_slabs.items():
        breakdown_data.append({
            "GST Slab": f"{rate}%",
            "Taxable Amount": f"₹{values['taxable_amount']:.2f}",
            "CGST": f"₹{values['cgst']:.2f}",
            "SGST": f"₹{values['sgst']:.2f}",
            "Total GST": f"₹{(values['cgst'] + values['sgst']):.2f}"
        })
    
    # Display the table
    breakdown_df = pd.DataFrame(breakdown_data)
    st.dataframe(breakdown_df)
    
    # Return the raw data for use in reports
    return gst_slabs
