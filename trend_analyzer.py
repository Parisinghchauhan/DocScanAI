import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class TrendAnalyzer:
    def __init__(self, db_client):
        """
        Initialize the trend analyzer with a database client
        
        Args:
            db_client: Database client instance
        """
        self.db = db_client
        
    def analyze_historical_trends(self, start_date=None, end_date=None, group_by="month"):
        """
        Analyze historical GST data to identify trends
        
        Args:
            start_date (str, optional): Start date for analysis in ISO format (YYYY-MM-DD)
            end_date (str, optional): End date for analysis in ISO format (YYYY-MM-DD)
            group_by (str, optional): Time period to group data by - "day", "week", "month", or "quarter"
            
        Returns:
            dict: Dictionary containing trend analysis results
        """
        # Get all invoices
        invoices = self.db.get_invoices()
        
        # If no invoices found, return empty results
        if not invoices:
            return {
                "time_series": [],
                "summary": {
                    "total_tax": 0,
                    "total_taxable": 0,
                    "invoice_count": 0,
                    "item_count": 0
                },
                "top_hsn_codes": [],
                "slab_distribution": {}
            }
        
        # Convert to DataFrame for easier analysis
        df_invoices = pd.DataFrame(invoices)
        
        # Convert created_at to datetime
        df_invoices['created_at'] = pd.to_datetime(df_invoices['created_at'])
        
        # Apply date filters if provided
        if start_date:
            start_date = pd.to_datetime(start_date)
            df_invoices = df_invoices[df_invoices['created_at'] >= start_date]
        
        if end_date:
            end_date = pd.to_datetime(end_date)
            df_invoices = df_invoices[df_invoices['created_at'] <= end_date]
        
        # If no invoices after filtering, return empty results
        if df_invoices.empty:
            return {
                "time_series": [],
                "summary": {
                    "total_tax": 0,
                    "total_taxable": 0,
                    "invoice_count": 0,
                    "item_count": 0
                },
                "top_hsn_codes": [],
                "slab_distribution": {}
            }
        
        # Get all items for these invoices
        all_items = []
        for invoice_id in df_invoices['id']:
            items = self.db.get_items_by_invoice(invoice_id)
            for item in items:
                item['invoice_id'] = invoice_id
                all_items.append(item)
        
        # If no items found, return basic invoice stats
        if not all_items:
            return {
                "time_series": self._generate_time_series(df_invoices, None, group_by),
                "summary": {
                    "total_tax": 0,
                    "total_taxable": 0,
                    "invoice_count": len(df_invoices),
                    "item_count": 0
                },
                "top_hsn_codes": [],
                "slab_distribution": {}
            }
        
        # Convert items to DataFrame
        df_items = pd.DataFrame(all_items)
        
        # Merge with invoice data to get timestamps
        df_items = df_items.merge(
            df_invoices[['id', 'created_at']], 
            left_on='invoice_id', 
            right_on='id', 
            suffixes=('_item', '')
        )
        
        # Calculate tax amount for each item
        df_items['tax_amount'] = df_items['total'] * (df_items['gst_rate'] / 100)
        
        # Generate time series data
        time_series = self._generate_time_series(df_invoices, df_items, group_by)
        
        # Get top HSN codes by frequency
        top_hsn = self._get_top_hsn_codes(df_items)
        
        # Get GST slab distribution
        slab_distribution = self._get_slab_distribution(df_items)
        
        # Calculate summary statistics
        summary = {
            "total_tax": float(df_items['tax_amount'].sum()),
            "total_taxable": float(df_items['total'].sum()),
            "invoice_count": len(df_invoices),
            "item_count": len(df_items),
            "avg_tax_per_invoice": float(df_items.groupby('invoice_id')['tax_amount'].sum().mean()) if len(df_items) > 0 else 0,
            "avg_items_per_invoice": float(df_items.groupby('invoice_id').size().mean()) if len(df_items) > 0 else 0
        }
        
        # Generate final trend analysis
        trend_analysis = {
            "time_series": time_series,
            "summary": summary,
            "top_hsn_codes": top_hsn,
            "slab_distribution": slab_distribution
        }
        
        return trend_analysis
    
    def _generate_time_series(self, df_invoices, df_items, group_by):
        """Generate time series data grouped by specified time period"""
        # Define grouping frequency
        freq_map = {
            "day": "D",
            "week": "W",
            "month": "M",
            "quarter": "Q"
        }
        freq = freq_map.get(group_by, "M")  # Default to month
        
        # Generate time bins
        if not df_invoices.empty:
            min_date = df_invoices['created_at'].min()
            max_date = df_invoices['created_at'].max()
            
            # Ensure we have at least a day range
            if min_date == max_date:
                max_date = min_date + timedelta(days=1)
                
            date_range = pd.date_range(start=min_date, end=max_date, freq=freq)
            
            # Count invoices per time period
            invoice_counts = df_invoices.groupby(pd.Grouper(key='created_at', freq=freq)).size()
            
            # Initialize time series
            time_series = []
            
            # If we have item data, calculate tax metrics too
            if df_items is not None and not df_items.empty:
                tax_data = df_items.groupby(pd.Grouper(key='created_at', freq=freq)).agg({
                    'total': 'sum',
                    'tax_amount': 'sum'
                })
                
                # Combine invoice counts with tax data
                for date in date_range:
                    date_str = date.strftime('%Y-%m-%d')
                    period_label = self._format_period_label(date, group_by)
                    
                    entry = {
                        "date": date_str,
                        "period": period_label,
                        "invoice_count": int(invoice_counts.get(date, 0)),
                        "total_taxable_value": float(tax_data.get('total', pd.Series()).get(date, 0)),
                        "total_tax": float(tax_data.get('tax_amount', pd.Series()).get(date, 0))
                    }
                    time_series.append(entry)
            else:
                # Just include invoice counts
                for date in date_range:
                    date_str = date.strftime('%Y-%m-%d')
                    period_label = self._format_period_label(date, group_by)
                    
                    entry = {
                        "date": date_str,
                        "period": period_label,
                        "invoice_count": int(invoice_counts.get(date, 0)),
                        "total_taxable_value": 0,
                        "total_tax": 0
                    }
                    time_series.append(entry)
                    
            return time_series
        else:
            return []
    
    def _format_period_label(self, date, group_by):
        """Format the period label based on grouping"""
        if group_by == "day":
            return date.strftime('%b %d, %Y')
        elif group_by == "week":
            return f"Week of {date.strftime('%b %d, %Y')}"
        elif group_by == "month":
            return date.strftime('%b %Y')
        elif group_by == "quarter":
            quarter = (date.month - 1) // 3 + 1
            return f"Q{quarter} {date.year}"
        else:
            return date.strftime('%b %Y')
    
    def _get_top_hsn_codes(self, df_items, limit=10):
        """Get the most frequently used HSN codes"""
        if 'hsn_code' not in df_items.columns or df_items.empty:
            return []
            
        # Get counts by HSN code
        hsn_counts = df_items['hsn_code'].value_counts().reset_index()
        hsn_counts.columns = ['hsn_code', 'count']
        
        # Get total tax and amount by HSN code
        hsn_tax = df_items.groupby('hsn_code').agg({
            'total': 'sum',
            'tax_amount': 'sum',
            'gst_rate': 'first',
            'description': 'first'  # Get the item description for display
        }).reset_index()
        
        # Merge counts with tax data
        hsn_data = hsn_counts.merge(hsn_tax, on='hsn_code')
        
        # Sort by count descending and take top N
        top_hsn = hsn_data.sort_values('count', ascending=False).head(limit)
        
        # Convert to list of dictionaries
        result = []
        for _, row in top_hsn.iterrows():
            if pd.notna(row['hsn_code']) and row['hsn_code'] != '':
                # Handle missing description field gracefully
                description = row.get('description', '')
                if pd.isna(description):
                    description = f"Item with HSN {row['hsn_code']}"
                
                result.append({
                    'hsn_code': row['hsn_code'],
                    'description': description,
                    'count': int(row['count']),
                    'total_amount': float(row['total']),
                    'total_tax': float(row['tax_amount']),
                    'gst_rate': float(row['gst_rate'])
                })
        
        return result
    
    def _get_slab_distribution(self, df_items):
        """Get distribution of tax slabs across items"""
        if 'gst_rate' not in df_items.columns or df_items.empty:
            return []
            
        # Group by GST rate
        slab_data = df_items.groupby('gst_rate').agg({
            'id_item': 'count',
            'total': 'sum',
            'tax_amount': 'sum'
        }).reset_index()
        
        # Convert to list format for frontend charts
        result = []
        for _, row in slab_data.iterrows():
            slab = float(row['gst_rate'])
            result.append({
                'slab': slab,
                'count': int(row['id_item']),
                'total_amount': float(row['total']),
                'total_tax': float(row['tax_amount'])
            })
        
        # Sort by tax slab
        result = sorted(result, key=lambda x: x['slab'])
        
        return result