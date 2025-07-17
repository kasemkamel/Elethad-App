# مقترح من cloude Ai


# def get_monthly_sales_comparison(self, months_back=6) -> dict:
#     """
#     Generate monthly sales comparison for the last N months.
    
#     Args:
#         months_back (int): Number of months to compare (default: 6)
    
#     Returns:
#         dict: Monthly sales comparison data
#     """
#     with self.db.get_connection() as conn:
#         cursor = conn.cursor()
        
#         cursor.execute('''
#         SELECT 
#             strftime('%Y', t.date) as year,
#             strftime('%m', t.date) as month,
#             SUM(COALESCE(t.total_amount, t.quantity * t.unit_price, 0)) as monthly_sales,
#             COUNT(*) as transaction_count,
#             SUM(t.quantity) as quantity_sold
#         FROM Transactions t
#         WHERE t.transaction_type = 'outgoing'
#         AND t.date >= date('now', '-{} months')
#         AND t.total_amount IS NOT NULL
#         GROUP BY strftime('%Y-%m', t.date)
#         ORDER BY year DESC, month DESC
#         '''.format(months_back))
        
#         monthly_data = cursor.fetchall()
        
#         # Calculate month-over-month growth
#         comparison_data = []
#         previous_sales = None
        
#         for row in reversed(monthly_data):  # Reverse to get chronological order
#             year, month, sales, transactions, quantity = row
#             month_name = datetime(int(year), int(month), 1).strftime('%B %Y')
            
#             growth_rate = None
#             if previous_sales is not None and previous_sales > 0:
#                 growth_rate = ((sales - previous_sales) / previous_sales) * 100
            
#             comparison_data.append({
#                 'year': int(year),
#                 'month': int(month),
#                 'month_name': month_name,
#                 'sales': float(sales),
#                 'transactions': transactions,
#                 'quantity_sold': quantity,
#                 'growth_rate': growth_rate
#             })
            
#             previous_sales = sales
        
#         # Calculate summary statistics
#         total_sales = sum(item['sales'] for item in comparison_data)
#         avg_monthly_sales = total_sales / len(comparison_data) if comparison_data else 0
        
#         return {
#             'monthly_data': comparison_data,
#             'total_sales': total_sales,
#             'average_monthly_sales': avg_monthly_sales,
#             'months_analyzed': len(comparison_data),
#             'generated_at': datetime.now().isoformat()
#         }

