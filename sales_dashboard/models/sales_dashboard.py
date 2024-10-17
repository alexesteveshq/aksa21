from odoo import models, api, _
from datetime import datetime, timedelta
from odoo.tools import format_amount
import pytz


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def get_dashboard_data(self):
        # Get the user's timezone or fallback to 'UTC'
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')

        # Use timezone-aware datetime objects for `today`
        today = datetime.now(tz=timezone)
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Calculate the same period in the previous month
        previous_month_start = (month_start - timedelta(days=1)).replace(day=1)
        previous_month_end = previous_month_start + timedelta(days=today.day - 1)

        # Convert `today` and other relevant datetimes to UTC for comparison
        today_utc = today.astimezone(pytz.UTC)
        month_start_utc = month_start.astimezone(pytz.UTC)
        previous_month_start_utc = previous_month_start.astimezone(pytz.UTC)
        previous_month_end_utc = previous_month_end.astimezone(pytz.UTC)

        # Fetch current month's orders up to the current time across all companies
        current_month_orders = self.with_context(active_test=False).sudo().search([
            ('date_order', '>=', month_start_utc),
            ('date_order', '<=', today_utc),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ])

        # Fetch the previous month's orders up to the same day
        previous_month_orders = self.with_context(active_test=False).sudo().search([
            ('date_order', '>=', previous_month_start_utc),
            ('date_order', '<=', previous_month_end_utc),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ])

        # Calculate total sales for both periods
        current_month_total_sales = sum(order.amount_currency for order in current_month_orders)
        previous_month_total_sales = sum(order.amount_currency for order in previous_month_orders)

        # Calculate total sales change percentage
        total_sales_change = round(
            ((current_month_total_sales - previous_month_total_sales) / previous_month_total_sales) * 100,
            2) if previous_month_total_sales else 100.0 if current_month_total_sales else 0.0

        # Calculate order-related statistics
        order_amount_sum = sum(order.amount_currency for order in current_month_orders)
        order_avg = order_amount_sum / len(current_month_orders) if len(current_month_orders) > 0 else 0
        order_count = len(current_month_orders)

        # Calculate discount average from order lines
        total_discount = sum(line.discount for order in current_month_orders for line in order.lines)
        discount_avg = total_discount / len(current_month_orders.mapped('lines')) if order_count > 0 else 0

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
        discount_avg_change = round(discount_avg - previous_discount_avg, 2)

        # Prepare daily sales data for each company
        companies = self.env['res.company'].search([])
        daily_sales = []
        current_sales_by_company = {company.id: 0 for company in companies}
        current_cost_by_company = {company.id: 0 for company in companies}
        previous_sales_by_company = {company.id: 0 for company in companies}

        for order in current_month_orders:
            current_cost_by_company[order.company_id.id] += order.order_cost
            current_sales_by_company[order.company_id.id] += order.amount_currency

        for order in previous_month_orders:
            previous_sales_by_company[order.company_id.id] += order.amount_currency

        # Create daily sales data for each company
        for company in companies:
            current_sales = current_sales_by_company[company.id]
            current_cost = current_cost_by_company[company.id]
            previous_sales = previous_sales_by_company[company.id]

            # Skip companies with zero sales in both periods
            if current_sales == 0 and previous_sales == 0:
                continue

            # Calculate percentage change
            percentage_change = calculate_change(current_sales, previous_sales)

            # Include company in `daily_sales` data
            daily_sales.append({
                'company': company.name,
                'current_sales': format_amount(self.env, current_sales, self.env.company.currency_id),
                'current_cost': format_amount(self.env, current_cost, self.env.company.currency_id),
                'percentage_change': percentage_change,
            })

        # Generate linear graph data for the entire month
        average_daily_sales = current_month_total_sales / today.day if today.day > 0 else 0
        linear_graph_data = [{'day': day, 'predicted_amount': average_daily_sales * day} for day in range(1, 32)]

        # Calculate product inventory for current and previous period
        current_products = self.env['product.product'].with_context(
            active_test=False).search([('type', '=', 'product'), ('qty_available', '>', 0)])

        # Convert to naive datetime for `to_date` in previous product search
        previous_month_end_naive = previous_month_end_utc.replace(tzinfo=None)

        prev_products = self.env['product.product'].with_context(
            to_date=previous_month_end_naive, active_test=False).search(
            [('type', '=', 'product'), ('qty_available', '>', 0)])

        # Create product data with unique IDs
        current_product_data = [{
            'id': product.id,
            'product': product.name,
            'quantity': product.qty_available,
            'cost': round(product.standard_price, 2)
        } for product in current_products]

        previous_product_data = [{
            'id': product.id,
            'product': product.name,
            'quantity': product.qty_available,
            'cost': round(product.standard_price, 2)
        } for product in prev_products]

        # Calculate today's sales and comparison with the same day in the previous month
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)

        today_orders = self.with_context(active_test=False).sudo().search([
            ('date_order', '>=', today_start.astimezone(pytz.UTC)),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ])

        previous_same_day = previous_month_start + timedelta(
            days=today.day - 1) if previous_month_end.day >= today.day else None
        previous_same_day_end = previous_same_day.replace(hour=23, minute=59, second=59) if previous_same_day else None

        previous_same_day_orders = self.with_context(active_test=False).sudo().search([
            ('date_order', '>=', previous_same_day),
            ('date_order', '<=', previous_same_day_end),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ]) if previous_same_day else []

        today_sales = sum(order.amount_currency for order in today_orders)
        previous_same_day_sales = sum(order.amount_currency for order in previous_same_day_orders)
        today_sales_change = round(((today_sales - previous_same_day_sales) / previous_same_day_sales) * 100,
                                   2) if previous_same_day_sales else (100.0 if today_sales else 0.0)

        # Calculate today's sales by company
        today_sales_by_company = {company.id: 0 for company in companies}
        today_cost_by_company = {company.id: 0 for company in companies}
        previous_sales_by_company_today = {company.id: 0 for company in companies}

        for order in today_orders:
            today_cost_by_company[order.company_id.id] += order.order_cost
            today_sales_by_company[order.company_id.id] += order.amount_currency

        for order in previous_same_day_orders:
            previous_sales_by_company_today[order.company_id.id] += order.amount_currency

        # Create today's sales data for each company
        today_sales_data = []
        for company in companies:
            current_cost = today_cost_by_company[company.id]
            current_sales = today_sales_by_company[company.id]
            previous_sales = previous_sales_by_company_today[company.id]

            # Skip companies with zero sales in both periods
            if current_sales_by_company[company.id] == 0 and previous_sales_by_company[company.id] == 0:
                continue

            # Calculate percentage change
            percentage_change = calculate_change(current_sales, previous_sales)

            # Include company in today's sales data
            today_sales_data.append({
                'company': company.name,
                'current_cost': format_amount(self.env, current_cost, self.env.company.currency_id),
                'current_sales': format_amount(self.env, current_sales, self.env.company.currency_id),
                'percentage_change': percentage_change,
            })

        # Calculate and sort seller ranking
        seller_ranking = []

        for seller in current_month_orders.mapped('seller_id'):
            current_seller_sales = sum(
                order.amount_currency for order in current_month_orders.filtered(lambda o: o.seller_id == seller))
            previous_seller_sales = sum(
                order.amount_currency for order in previous_month_orders.filtered(lambda o: o.seller_id == seller))
            seller_change = calculate_change(current_seller_sales, previous_seller_sales)

            # Calculate discount averages for the current and previous month for each seller
            current_total_discount = sum(line.discount for order in current_month_orders.filtered(lambda o: o.seller_id == seller) for line in order.lines)
            current_line_count = len(current_month_orders.filtered(lambda o: o.seller_id == seller).mapped('lines'))
            current_seller_discount_avg = current_total_discount / current_line_count if current_line_count > 0 else 0

            previous_total_discount = sum(line.discount for order in previous_month_orders.filtered(lambda o: o.seller_id == seller) for line in order.lines)
            previous_line_count = len(previous_month_orders.filtered(lambda o: o.seller_id == seller).mapped('lines'))
            previous_seller_discount_avg = previous_total_discount / previous_line_count if previous_line_count > 0 else 0

            discount_avg_change = 0 if not previous_seller_discount_avg else\
                round(current_seller_discount_avg - previous_seller_discount_avg, 2)

            seller_ranking.append({
                'id': seller.id,
                'name': seller.name,
                'amount_sold': format_amount(self.env, current_seller_sales, self.env.company.currency_id),
                'percentage_change': seller_change,
                'discount_avg': round(current_seller_discount_avg, 2),
                'discount_change': discount_avg_change,
            })

        # Sort the seller ranking data by 'amount_sold' in descending order
        seller_ranking = sorted(seller_ranking, key=lambda x: x['amount_sold'], reverse=True)

        category_sales = {}
        for line in current_month_orders.mapped('lines'):
            category = line.product_id.category_id.name or _('Uncategorized')
            category_sales[category] = category_sales.get(category, 0) + line.qty

        # Sort by quantity and limit to top 10 categories
        sorted_category_sales = sorted(category_sales.items(), key=lambda x: x[1], reverse=True)[:10]

        # Prepare the data for best-selling products by category based on quantities
        best_selling_products_data = [{'category': category, 'quantity': round(quantity, 2)} for category, quantity in
                                      sorted_category_sales]
        # Return updated dashboard data
        return {
            'total_sales': format_amount(self.env, current_month_total_sales, self.env.company.currency_id),
            'total_sales_change': round(total_sales_change, 2),
            'best_selling_products': best_selling_products_data,
            'daily_sales': daily_sales,
            'linear_graph_data': linear_graph_data,
            'order_avg': format_amount(self.env, order_avg, self.env.company.currency_id),
            'order_count': order_count,
            'discount_avg': round(discount_avg, 2),
            'order_avg_change': order_avg_change,
            'order_count_change': order_count_change,
            'discount_avg_change': discount_avg_change,
            'currentTotalQuantity': sum(p['quantity'] for p in current_product_data),
            'currentTotalCost': format_amount(
                self.env, sum(p['quantity'] * p['cost'] for p in current_product_data), self.env.company.currency_id),
            'previousTotalQuantity': sum(p['quantity'] for p in previous_product_data),
            'previousTotalCost': format_amount(
                self.env, sum(p['quantity'] * p['cost'] for p in previous_product_data), self.env.company.currency_id),
            'today_sales_data': today_sales_data,
            'today_sales': format_amount(self.env, today_sales, self.env.company.currency_id),
            'today_sales_change': today_sales_change,
            'seller_ranking': seller_ranking
        }
