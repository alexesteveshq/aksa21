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
        ]).filtered(lambda o: not o.is_refunded and not o.refunded_orders_count)

        # Fetch the previous month's orders up to the same day
        previous_month_orders = self.with_context(active_test=False).sudo().search([
            ('date_order', '>=', previous_month_start_utc),
            ('date_order', '<=', previous_month_end_utc),
            ('is_refunded', '=', False),
            ('refunded_orders_count', '=', 0),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ]).filtered(lambda o: not o.is_refunded and not o.refunded_orders_count)

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
        order_prod_avg = (len(current_month_orders.mapped('lines').filtered(
            lambda ln: ln.amount_currency > 0)) / order_count)

        # Calculate discount average from order lines
        discount_avg = (sum(current_month_orders.mapped('lines').filtered(lambda ln: ln.discount > 0).mapped(
            'discount')) / len(current_month_orders.mapped('lines').filtered(lambda ln: ln.discount > 0)))

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
            current_margin = ((current_sales - current_cost)/current_sales) * 100

            # Include company in `daily_sales` data
            daily_sales.append({
                'company': company.name,
                'current_sales': format_amount(self.env, current_sales, self.env.company.currency_id),
                'current_cost': format_amount(self.env, current_cost, self.env.company.currency_id),
                'margin': round(current_margin, 2),
                'percentage_change': percentage_change,
            })

        # Generate linear graph data for the entire month, split by company
        linear_graph_data = []

        for company in companies:
            # Get current month sales for the company
            company_orders = current_month_orders.filtered(lambda o: o.company_id == company)
            total_company_sales = sum(order.amount_currency for order in company_orders)
            if total_company_sales > 0:
                avg_daily_sales = total_company_sales / today.day if today.day > 0 else 0

                # Add data points for the company's predicted sales
                company_graph_data = {
                    'company': company.name,
                    'data': [{'day': day, 'predicted_amount': avg_daily_sales * day} for day in range(1, 32)]
                }
                linear_graph_data.append(company_graph_data)

        # Add a "Legacy" record as the sum of all predicted sales
        legacy_data = []
        for day in range(1, 32):
            # Sum the predicted amounts for all companies for the current day
            total_predicted_amount = sum(
                company_data['data'][day - 1]['predicted_amount'] for company_data in linear_graph_data
            )
            legacy_data.append({'day': day, 'predicted_amount': total_predicted_amount})

        # Append the "Legacy" record to the linear graph data
        linear_graph_data.append({
            'company': 'Legacy',
            'data': legacy_data
        })

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
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('is_refunded', '=', False),
            ('refunded_orders_count', '=', 0),
        ]).filtered(lambda o: not o.is_refunded and not o.refunded_orders_count)

        previous_same_day = previous_month_start + timedelta(
            days=today.day - 1) if previous_month_end.day >= today.day else None
        previous_same_day_end = previous_same_day.replace(hour=23, minute=59, second=59) if previous_same_day else None

        previous_same_day_orders = self.with_context(active_test=False).sudo().search([
            ('date_order', '>=', previous_same_day),
            ('date_order', '<=', previous_same_day_end),
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('is_refunded', '=', False),
            ('refunded_orders_count', '=', 0),
        ]).filtered(lambda o: not o.is_refunded and not o.refunded_orders_count) if previous_same_day else []

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

            # Fetch today's POS orders for this company
            company_today_orders = today_orders.filtered(lambda o: o.company_id == company)

            company_order_details = [{
                'ticket_reference': order.pos_reference,
                'amount_currency': format_amount(self.env, order.amount_currency, self.env.company.currency_id),
                'seller': order.seller_id.name if order.seller_id else _('Unknown'),
                'datetime': order.date_order.astimezone(pytz.timezone(self.env.user.tz or 'UTC')).strftime('%H:%M:%S')
            } for order in company_today_orders]

            # Skip companies with zero sales in both periods
            if current_sales == 0 and previous_sales == 0:
                continue

            # Calculate percentage change
            percentage_change = calculate_change(current_sales, previous_sales)

            # Add company and detailed orders to today's sales data
            today_sales_data.append({
                'company': company.name,
                'current_cost': format_amount(self.env, current_cost, self.env.company.currency_id),
                'current_sales': format_amount(self.env, current_sales, self.env.company.currency_id),
                'percentage_change': percentage_change,
                'order_details': company_order_details  # Include POS order details
            })

        # Updated seller ranking logic
        seller_ranking = []

        for seller in current_month_orders.mapped('seller_id'):
            # Filter orders by seller
            seller_orders = current_month_orders.filtered(lambda o: o.seller_id == seller)
            previous_seller_orders = previous_month_orders.filtered(lambda o: o.seller_id == seller)

            # Total and average sales
            current_seller_sales = sum(order.amount_currency for order in seller_orders)
            previous_seller_sales = sum(order.amount_currency for order in previous_seller_orders)
            seller_change = calculate_change(current_seller_sales, previous_seller_sales)

            # Calculate discount averages
            current_total_discount = sum(
                line.discount for order in seller_orders for line in order.lines.filtered(lambda ln: ln.price_unit > 0))
            current_line_count = len(seller_orders.mapped('lines').filtered(lambda ln: ln.price_unit > 0))
            current_seller_discount_avg = current_total_discount / current_line_count if current_line_count > 0 else 0

            previous_total_discount = sum(line.discount for order in previous_seller_orders for line in
                                          order.lines.filtered(lambda ln: ln.price_unit > 0))
            previous_line_count = len(previous_seller_orders.mapped('lines').filtered(lambda ln: ln.price_unit > 0))
            previous_seller_discount_avg = previous_total_discount / previous_line_count if previous_line_count > 0 else 0

            discount_avg_change = 0 if not previous_seller_discount_avg else \
                round(current_seller_discount_avg - previous_seller_discount_avg, 2)

            # Calculate averages
            total_products_sold = sum(
                line.qty for order in seller_orders for line in order.lines.filtered(lambda ln: ln.price_unit > 0))
            total_orders = len(seller_orders)
            avg_products_sold = total_products_sold
            avg_order_count = total_orders
            avg_products_per_order = total_products_sold / total_orders if total_orders > 0 else 0  # Average products per order

            # Append seller data
            seller_ranking.append({
                'id': seller.id,
                'name': seller.name,
                'amount_sold': current_seller_sales,
                'percentage_change': seller_change,
                'discount_avg': round(current_seller_discount_avg, 2),
                'discount_change': discount_avg_change,
                'avg_products_sold': avg_products_sold,
                'avg_order_count': avg_order_count,
                'avg_products_per_order': round(avg_products_per_order, 2),
            })

        # Sort seller ranking by total sales
        seller_ranking = sorted(seller_ranking, key=lambda x: x['amount_sold'], reverse=True)

        # Format monetary values
        for record in seller_ranking:
            record['amount_sold'] = format_amount(self.env, record['amount_sold'], self.env.company.currency_id)

        # Initialize dictionaries to track sales and totals by category
        category_sales = {}  # Total sales amount (amount_currency) per category
        category_totals = {}  # Total quantity sold per category

        # Calculate total sales amount and total quantity per category
        for line in current_month_orders.mapped('lines').filtered(lambda ln: ln.amount_currency > 0):
            category = line.product_id.category_id.name or _('Uncategorized')
            category_sales[category] = category_sales.get(category, 0) + line.amount_currency  # Sum by amount_currency
            category_totals[category] = category_totals.get(category, 0) + line.qty  # Sum by quantity

        # Calculate the total sales amount across all categories
        total_sales_amount = sum(category_sales.values())

        # Prepare the data with percentages based on revenue (amount_currency)
        best_selling_products_data = []
        for category, sales_amount in category_sales.items():
            percentage = (sales_amount / total_sales_amount) * 100 if total_sales_amount > 0 else 0
            quantity = category_totals[category]  # Total quantity for the category
            formatted_sales = f"{sales_amount:,.2f}"  # Format sales amount

            best_selling_products_data.append({
                'category': f"{category} ({int(quantity)})",  # Add number of products sold next to the name
                'quantity': round(quantity, 2),  # Keep quantity rounded
                'percentage': round(percentage, 2),  # Percentage based on revenue
                'total_sales': formatted_sales  # Total sales formatted in US style
            })

        # Sort by percentage of revenue and limit to the top 10 categories
        best_selling_products_data = sorted(best_selling_products_data,
                                            key=lambda x: x['percentage'], reverse=True)[:10]

        # Generate daily sales data per company for the graph
        daily_sales_graph_data = []

        # Ensure all datetime comparisons are in UTC
        utc_timezone = pytz.UTC

        # Initialize a dictionary to accumulate sales for the "Legacy" line
        legacy_daily_sales = {day: 0 for day in range(1, today.day + 1)}

        for company in companies:
            # Filter orders for the current company and current month
            company_orders = current_month_orders.filtered(lambda o: o.company_id == company)

            # Prepare daily sales data
            company_daily_sales = []
            total_company_sales = 0  # Track total sales for the company

            for day in range(1, today.day + 1):  # Loop from the first day of the month to today
                # Calculate day start and day end in UTC
                day_start = (month_start + timedelta(days=day - 1)).replace(tzinfo=utc_timezone)
                day_end = (day_start + timedelta(days=1) - timedelta(seconds=1)).replace(tzinfo=utc_timezone)

                # Convert o.date_order to UTC for comparison
                day_orders = company_orders.filtered(
                    lambda o: day_start <= o.date_order.replace(tzinfo=utc_timezone) <= day_end
                )
                total_sales = sum(order.amount_currency for order in day_orders)

                # Add the day's sales to the company's total sales
                total_company_sales += total_sales

                # Add sales to the "Legacy" line for this day
                legacy_daily_sales[day] += total_sales

                # Append daily sales data
                company_daily_sales.append({'day': day, 'sales': total_sales})

            # Only add companies with total sales > 0 to the graph
            if total_company_sales > 0:
                daily_sales_graph_data.append({
                    'company': company.name,
                    'data': company_daily_sales,
                })

        # Add the "Legacy" line to the graph
        legacy_data = [{'day': day, 'sales': legacy_daily_sales[day]} for day in range(1, today.day + 1)]
        daily_sales_graph_data.append({
            'company': 'Legacy',
            'data': legacy_data,
        })

        # Generate monthly sales data with detailed tickets
        monthly_sales_data = []
        start_date = (today - timedelta(days=today.day)).replace(day=1)  # First day of the previous month
        end_date = today.replace(day=1)  # Current month (1st day)

        # Loop from the past month to the current month
        while start_date <= end_date:
            # Calculate the start and end of the current month
            month_start = start_date
            next_month_start = (month_start + timedelta(days=31)).replace(day=1)  # First day of the next month
            month_end = next_month_start - timedelta(seconds=1)  # Last second of the current month

            # Convert to UTC
            month_start_utc = month_start.astimezone(pytz.UTC)
            month_end_utc = month_end.astimezone(pytz.UTC)

            # Fetch orders for the current month
            monthly_orders = self.with_context(active_test=False).sudo().search([
                ('date_order', '>=', month_start_utc),
                ('date_order', '<=', month_end_utc),
                ('state', 'in', ['paid', 'done', 'invoiced']),
            ])

            # Calculate totals
            total_sales = sum(order.amount_currency for order in monthly_orders)
            total_cost = sum(order.order_cost for order in monthly_orders)
            total_orders = len(monthly_orders)

            # Fetch detailed ticket data
            ticket_details = [{
                'ticket_reference': order.pos_reference,
                'seller': order.seller_id.name if order.seller_id else _('Unknown'),
                'datetime': order.date_order.astimezone(
                    pytz.timezone(self.env.user.tz or 'UTC')).strftime('%Y-%m-%d %H:%M:%S'),
                'amount': format_amount(self.env, order.amount_currency, self.env.company.currency_id),
            } for order in monthly_orders]

            # Append the month's data
            monthly_sales_data.append({
                'year': month_start.year,
                'month': month_start.strftime('%B'),  # Month name (e.g., 'November')
                'total_sales': format_amount(self.env, total_sales, self.env.company.currency_id),
                'total_cost': format_amount(self.env, total_cost, self.env.company.currency_id),
                'total_orders': total_orders,
                'tickets': ticket_details,  # Add ticket details
            })

            # Move to the next month
            start_date = next_month_start

        return {
            'total_sales': format_amount(self.env, current_month_total_sales, self.env.company.currency_id),
            'total_sales_change': round(total_sales_change, 2),
            'best_selling_products': best_selling_products_data,
            'daily_sales': daily_sales,
            'linear_graph_data': linear_graph_data,
            'order_avg': format_amount(self.env, order_avg, self.env.company.currency_id),
            'order_count': order_count,
            'monthly_sales_data': monthly_sales_data,
            'discount_avg': round(discount_avg, 2),
            'order_prod_avg': round(order_prod_avg, 2),
            'order_avg_change': order_avg_change,
            'daily_sales_graph_data': daily_sales_graph_data,
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
