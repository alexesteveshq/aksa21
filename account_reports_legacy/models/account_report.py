from odoo import models, fields, api, _
from odoo.tools.misc import format_amount
import re

class AccountReport(models.Model):
    _inherit = 'account.report'

    is_legacy = fields.Boolean(string="Legacy Report", default=False)

    @staticmethod
    def extract_account_id(line_id):
        match = re.search(r"groupby:account_id~account\.account~(\d+)", line_id)
        return int(match.group(1)) if match else None

    @staticmethod
    def extract_report_line_id(line_id):
        match = re.search(r"~account\.report\.line~(\d+)", line_id)
        return int(match.group(1)) if match else None

    def _get_lines(self, options, all_column_groups_expression_totals=None):
        original_lines = super()._get_lines(options, all_column_groups_expression_totals)
        if not self.is_legacy:
            return original_lines

        new_lines = []
        for line in original_lines:
            new_lines.append(line)

            if "~account.report.line~" in line.get("id", ""):
                report_line_id = self.extract_report_line_id(line["id"])
                report_line = self.env['account.report.line'].browse(report_line_id)

                if report_line.code == 'INC_LEGACY':
                    sublines = self._create_account_lines(line, options, 'income', 'income_account')
                    new_lines.extend(sublines)

                elif report_line.code == 'LEX_LEGACY_EXP':
                    sublines = self._create_account_lines(line, options, 'expense', 'expense_account')
                    new_lines.extend(sublines)

                elif report_line.code == 'BANK_LEGACY':
                    sublines = self._create_bank_lines(line, options)
                    new_lines.extend(sublines)

                elif report_line.code == 'UTILITY_LEGACY':
                    sublines = self._create_utility_lines(line, options)
                    new_lines.extend(sublines)

        return new_lines

    def _create_account_lines(self, parent_line, options, account_type, prefix):
        results = self._get_accounts_summary(options, account_type)
        allow_unfold = True
        return self._build_account_lines(parent_line, options, results, prefix, allow_unfold=allow_unfold)

    def _create_bank_lines(self, parent_line, options):
        results = self._get_bank_accounts_lifetime()
        return self._build_account_lines(parent_line, options, results, prefix='bank_account', allow_unfold=True)

    def _create_utility_lines(self, parent_line, options):
        rows = self._get_company_currency_utilities(options)

        company_totals = {}
        for row in rows:
            company_id = row['company_id']
            company_name = row['company_name']
            currency = row['currency']
            key = (company_id, company_name)
            if key not in company_totals:
                company_totals[key] = {
                    'account_code': str(company_id),
                    'account_name': company_name,
                    'balance_mxn': 0.0,
                    'balance_usd': 0.0,
                }
            if currency == 'MXN':
                company_totals[key]['balance_mxn'] += (row['income'] or 0.0) - (row['expense'] or 0.0)
            elif currency == 'USD':
                company_totals[key]['balance_usd'] += (row['income'] or 0.0) - (row['expense'] or 0.0)

        return self._build_account_lines(parent_line, options, list(company_totals.values()), prefix='utility', allow_unfold=False)

    def _get_company_currency_utilities(self, options):
        date_from = options["date"]["date_from"]
        date_to = options["date"]["date_to"]

        sql = """
            SELECT
                c.id AS company_id,
                c.name AS company_name,
                COALESCE(curr.name, 'MXN') AS currency,
                SUM(CASE WHEN a.account_type IN ('asset_cash', 'asset_receivable') AND l.amount_currency > 0 THEN l.amount_currency ELSE 0 END) AS income,
                SUM(CASE WHEN a.account_type = 'expense' THEN l.amount_currency ELSE 0 END) AS expense
            FROM account_move_line l
            JOIN account_account a ON l.account_id = a.id
            JOIN res_company c ON l.company_id = c.id
            LEFT JOIN res_currency curr ON l.currency_id = curr.id
            WHERE a.legacy_report IS TRUE
              AND l.date BETWEEN %s AND %s
              AND l.parent_state = 'posted'
              AND a.account_type IN ('asset_cash', 'asset_receivable', 'expense')
            GROUP BY c.id, c.name, currency
            ORDER BY c.name
        """
        self.env.cr.execute(sql, [date_from, date_to])
        return self.env.cr.dictfetchall()

    def _get_accounts_summary(self, options, account_type):
        if account_type == 'income':
            return self._get_income_accounts_summary(options)
        elif account_type == 'expense':
            return self._get_expense_accounts_summary(options)
        return []

    def _get_income_accounts_summary(self, options):
        date_from = options["date"]["date_from"]
        date_to = options["date"]["date_to"]

        sql = f"""
            SELECT
                a.code AS account_code,
                a.name AS account_name,
                SUM(CASE WHEN curr.name = 'MXN' THEN l.amount_currency ELSE 0 END) AS balance_mxn,
                SUM(CASE WHEN curr.name = 'USD' THEN l.amount_currency ELSE 0 END) AS balance_usd
            FROM account_move_line l
            JOIN account_account a ON l.account_id = a.id 
            JOIN account_journal j ON l.journal_id = j.id 
            LEFT JOIN res_currency curr ON a.currency_id = curr.id
            WHERE l.parent_state = 'posted'
              AND a.account_type IN ('asset_cash', 'asset_receivable') AND j.expense_journal IS NOT TRUE 
              AND l.date BETWEEN '{date_from}' AND '{date_to}' 
              AND a.legacy_report IS TRUE  
            GROUP BY a.code, a.name
            ORDER BY a.code
        """
        self.env.cr.execute(sql)
        return self.env.cr.dictfetchall()

    def _get_expense_accounts_summary(self, options):
        date_from = options["date"]["date_from"]
        date_to = options["date"]["date_to"]

        sql = f"""
            SELECT
                a.code AS account_code,
                a.name AS account_name,
                SUM(CASE WHEN curr.name = 'MXN' THEN l.amount_currency ELSE 0 END) AS balance_mxn,
                SUM(CASE WHEN curr.name = 'USD' THEN l.amount_currency ELSE 0 END) AS balance_usd
            FROM account_move_line l
            JOIN account_account a ON l.account_id = a.id
            LEFT JOIN res_currency curr ON l.currency_id = curr.id
            WHERE a.account_type = 'expense'
              AND a.legacy_report IS TRUE 
              AND l.date BETWEEN '{date_from}' AND '{date_to}'
              AND l.parent_state = 'posted'
            GROUP BY a.code, a.name
            ORDER BY a.code
        """
        self.env.cr.execute(sql)
        return self.env.cr.dictfetchall()

    def _get_bank_accounts_lifetime(self):
        sql = f"""
            SELECT
                a.code AS account_code,
                MIN(a.name) AS account_name,
                SUM(CASE WHEN curr.name = 'MXN' THEN l.amount_currency ELSE 0 END) AS balance_mxn,
                SUM(CASE WHEN curr.name = 'USD' THEN l.amount_currency ELSE 0 END) AS balance_usd
            FROM account_move_line l
            JOIN account_account a ON l.account_id = a.id 
            JOIN account_journal j ON l.journal_id = j.id 
            LEFT JOIN res_currency curr ON a.currency_id = curr.id
            WHERE (a.account_type = 'asset_cash' OR j.type = 'sale') 
              AND a.legacy_report IS TRUE  
              AND l.parent_state = 'posted'
            GROUP BY a.code
            ORDER BY a.code
        """
        self.env.cr.execute(sql)
        return self.env.cr.dictfetchall()

    def _get_company_breakdown(self, account_code, options, prefix):
        date_from = options["date"]["date_from"]
        date_to = options["date"]["date_to"]

        if prefix == 'income_account':
            account_type_condition = "AND a.account_type IN ('asset_cash', 'asset_receivable') AND j.expense_journal IS NOT TRUE "
            ignore_date_filter = False
        elif prefix == 'expense_account':
            account_type_condition = "AND a.account_type = 'expense'"
            ignore_date_filter = False
        elif prefix == 'bank_account':
            account_type_condition = "AND (a.account_type = 'asset_cash' OR j.type = 'sale')"
            ignore_date_filter = True
        else:
            account_type_condition = ""
            ignore_date_filter = False

        date_filter = "" if ignore_date_filter else "AND l.date BETWEEN %s AND %s"

        sql = f"""
            SELECT
                c.id AS company_id,
                c.name AS company_name,
                SUM(CASE WHEN curr.name = 'MXN' THEN l.amount_currency ELSE 0 END) AS balance_mxn,
                SUM(CASE WHEN curr.name = 'USD' THEN l.amount_currency ELSE 0 END) AS balance_usd
            FROM account_move_line l
            JOIN account_account a ON l.account_id = a.id
            JOIN res_company c ON l.company_id = c.id
            JOIN account_journal j ON l.journal_id = j.id 
            LEFT JOIN res_currency curr ON l.currency_id = curr.id
            WHERE a.code = %s
              AND l.parent_state = 'posted'
              {account_type_condition}
              {date_filter}
            GROUP BY c.id, c.name
            ORDER BY c.name
        """

        params = [account_code] + ([] if ignore_date_filter else [date_from, date_to])
        self.env.cr.execute(sql.format(date_filter=date_filter), params)
        return self.env.cr.dictfetchall()

    def _build_account_lines(self, parent_line, options, results, prefix, allow_unfold):
        new_lines = []
        parent_id = parent_line['id']
        report_line_id = self.extract_report_line_id(parent_id)

        for result in results:
            line_id = f"{prefix}_line_{result['account_code']}"
            breakdown = self._get_company_breakdown(result['account_code'], options, prefix) if allow_unfold else []
            is_unfoldable = allow_unfold and len(breakdown) > 0
            is_unfolded = is_unfoldable and line_id in options.get('unfolded_lines', [])

            if prefix != 'utility' and result.get('account_code'):
                name = f"[{result['account_code']}] {result['account_name']}"
            else:
                name = result['account_name']

            line_dict = {
                'id': line_id,
                'name': name,
                'level': 2,
                'parent_id': parent_id,
                'columns': self._build_columns(result, options, report_line_id),
                'unfoldable': is_unfoldable,
                'unfolded': is_unfolded,
                'groupby': False,
                'style': 'color:#4A4F59; font-weight:normal;' if prefix == 'utility' else 'color:#01666b; font-weight:normal;',
            }

            new_lines.append(line_dict)

            for company in breakdown:
                columns = self._build_columns(company, options, report_line_id)
                if all(col['no_format'] == 0.0 for col in columns):
                    continue  # skip if all values are 0
                company_line = {
                    'id': f"{line_id}_company_{company['company_id']}",
                    'name': company['company_name'],
                    'level': 3,
                    'parent_id': line_id,
                    'columns': columns,
                    'unfoldable': False,
                    'unfolded': False,
                    'groupby': False,
                }
                new_lines.append(company_line)

        return new_lines

    def _build_columns(self, data, options, report_line_id):
        columns = []
        for column in options['columns']:
            expression = column['expression_label']
            amount = data.get(expression, 0.0)

            columns.append({
                'name': format_amount(self.env, amount, self.env.company.currency_id),
                'no_format': amount,
                'class': '',
                'style': 'white-space:nowrap; text-align:right; ; font-weight:bold; color: #4A4F59;',
                'expression_label': expression,
                'column_group_key': column['column_group_key'],
                'report_line_id': report_line_id,
                'auditable': False,
                'is_zero': amount == 0.0,
                'has_sublines': False,
            })
        return columns