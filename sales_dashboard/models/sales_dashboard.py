from odoo import models, api
from datetime import datetime, timedelta

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def get_dashboard_data(self):
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = today.replace(day=1)

        # Calculate the same period in the previous month (first day to today's day)
        previous_month_start = (month_start - timedelta(days=1)).replace(day=1)
        previous_month_end = previous_month_start + timedelta(days=today.day - 1)

        # Fetch current month's orders up to today across all companies
        current_month_orders = self.with_context(active_test=False).sudo().search([
            ('date_order', '>=', month_start),
            ('date_order', '<=', today),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ])

        # Fetch the previous month's orders up to the same day
        previous_month_orders = self.with_context(active_test=False).sudo().search([
            ('date_order', '>=', previous_month_start),
            ('date_order', '<=', previous_month_end),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ])

        # Calculate total sales for both periods
        current_month_total_sales = sum(order.amount_currency for order in current_month_orders)
        previous_month_total_sales = sum(order.amount_currency for order in previous_month_orders)

        # Calculate total sales change percentage
        total_sales_change = round(((current_month_total_sales - previous_month_total_sales) / previous_month_total_sales) * 100, 2) if previous_month_total_sales else 100.0 if current_month_total_sales else 0.0

        # Calculate order-related statistics
        order_amount_sum = sum(order.amount_currency for order in current_month_orders)
        order_avg = order_amount_sum / len(current_month_orders) if len(current_month_orders) > 0 else 0
        order_count = len(current_month_orders)

        # Calculate discount average from order lines
        total_discount = sum(line.discount for order in current_month_orders for line in order.lines)
        discount_avg = total_discount / order_count if order_count > 0 else 0

        # Calculate previous period statistics
        previous_order_sum = sum(order.amount_currency for order in previous_month_orders)
        previous_order_avg = previous_order_sum / len(previous_month_orders) if len(previous_month_orders) > 0 else 0
        previous_order_count = len(previous_month_orders)
        previous_discount_total = sum(line.discount for order in previous_month_orders for line in order.lines)
        previous_discount_avg = previous_discount_total / previous_order_count if previous_order_count > 0 else 0

        # Calculate changes
        def calculate_change(current, previous):
            if previous == 0:
                return 100.0 if current > 0 else -100.0
            return round(((current - previous) / previous) * 100, 2)

        order_avg_change = calculate_change(order_avg, previous_order_avg)
        order_count_change = order_count - previous_order_count  # Difference in count instead of percentage
        discount_avg_change = calculate_change(discount_avg, previous_discount_avg)

        # Prepare daily sales data for each company
        companies = self.env['res.company'].search([])
        daily_sales = []
        current_sales_by_company = {company.id: 0 for company in companies}
        previous_sales_by_company = {company.id: 0 for company in companies}

        for order in current_month_orders:
            current_sales_by_company[order.company_id.id] += order.amount_currency

        for order in previous_month_orders:
            previous_sales_by_company[order.company_id.id] += order.amount_currency

        # Create daily sales data for each company
        for company in companies:
            current_sales = current_sales_by_company[company.id]
            previous_sales = previous_sales_by_company[company.id]

            # Skip companies with zero sales in both periods
            if current_sales == 0 and previous_sales == 0:
                continue

            # Calculate percentage change
            percentage_change = calculate_change(current_sales, previous_sales)

            # Include company in `daily_sales` data
            daily_sales.append({
                'company': company.name,
                'current_sales': current_sales,
                'percentage_change': percentage_change,
            })

        # Generate linear graph data for the entire month
        average_daily_sales = current_month_total_sales / today.day if today.day > 0 else 0
        linear_graph_data = [{'day': day, 'predicted_amount': average_daily_sales * day} for day in range(1, 32)]

        # Calculate product inventory for current and previous period
        current_products = self.env['product.product'].with_context(
            active_test=False).search([('type', '=', 'product'), ('qty_available', '>', 0)])
        prev_products = self.env['product.product'].with_context(
            to_date=previous_month_end, active_test=False).search(
            [('type', '=', 'product'), ('qty_available', '>', 0)])

        # Create product data with unique IDs
        current_product_data = [{
            'id': product.id,  # Use product ID as unique key
            'product': product.name,
            'quantity': product.qty_available,
            'cost': round(product.standard_price, 2)
        } for product in current_products]

        previous_product_data = [{
            'id': product.id,  # Use product ID as unique key
            'product': product.name,
            'quantity': product.qty_available,
            'cost': round(product.standard_price, 2)
        } for product in prev_products]

        # Calculate today's sales and comparison with the same day in the previous month
        today_start = today.replace(hour=0, minute=0, second=0)
        today_end = today.replace(hour=23, minute=59, second=59)

        today_orders = self.with_context(active_test=False).sudo().search([
            ('date_order', '>=', today_start),
            ('date_order', '<=', today_end),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ])

        previous_same_day = previous_month_start + timedelta(days=today.day - 1) if previous_month_end.day >= today.day else None
        previous_same_day_end = previous_same_day.replace(hour=23, minute=59, second=59) if previous_same_day else None

        previous_same_day_orders = self.with_context(active_test=False).sudo().search([
            ('date_order', '>=', previous_same_day),
            ('date_order', '<=', previous_same_day_end),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ]) if previous_same_day else []

        today_sales = sum(order.amount_currency for order in today_orders)
        previous_same_day_sales = sum(order.amount_currency for order in previous_same_day_orders)
        today_sales_change = round(((today_sales - previous_same_day_sales) / previous_same_day_sales) * 100, 2) if previous_same_day_sales else (100.0 if today_sales else 0.0)

        # Calculate and sort seller ranking
        seller_ranking = []

        for seller in current_month_orders.mapped('seller_id'):
            current_seller_sales = sum(order.amount_currency for order in current_month_orders.filtered(lambda o: o.seller_id == seller))
            previous_seller_sales = sum(order.amount_currency for order in previous_month_orders.filtered(lambda o: o.seller_id == seller))
            seller_change = calculate_change(current_seller_sales, previous_seller_sales)
            seller_ranking.append({
                'id': seller.id,
                'name': seller.name,
                'amount_sold': round(current_seller_sales, 2),
                'percentage_change': seller_change,
            })

        # Sort the seller ranking data by 'amount_sold' in descending order
        seller_ranking = sorted(seller_ranking, key=lambda x: x['amount_sold'], reverse=True)

        # Return updated dashboard data
        return {
            'total_sales': current_month_total_sales,
            'total_sales_change': round(total_sales_change, 2),
            'daily_sales': daily_sales,
            'linear_graph_data': linear_graph_data,
            'order_avg': round(order_avg, 2),
            'order_count': order_count,
            'discount_avg': round(discount_avg, 2),
            'order_avg_change': order_avg_change,
            'order_count_change': order_count_change,
            'discount_avg_change': discount_avg_change,
            'currentTotalQuantity': sum(p['quantity'] for p in current_product_data),
            'currentTotalCost': round(sum(p['quantity'] * p['cost'] for p in current_product_data), 2),
            'previousTotalQuantity': sum(p['quantity'] for p in previous_product_data),
            'previousTotalCost': round(sum(p['quantity'] * p['cost'] for p in previous_product_data), 2),
            'today_sales': today_sales,
            'today_sales_change': today_sales_change,
            'seller_ranking': seller_ranking  # Return sorted seller ranking
        }
