/** @odoo-module **/

import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';

const { Component } = owl;

export class PrinterButton extends Component {
    setup() {
        this.orm = useService("orm");
    }

    async onClick() {
        const companies = await this.orm.call("res.company", "search_read", [], {
            fields: ["name", "phone", "street", "city", "state_id", "country_id", "zip"],
            domain: [["id", "=", this.props.record.data.company_id[0]]],
        });
        const partners = await this.orm.call("res.partner", "search_read", [], {
            fields: ["name"],
            domain: [["id", "=", this.props.record.data.partner_id[0]]],
        });
        var lines = ""
        const { _t } = this.env;
        this.props.record.data.order_line.records.forEach(function (item, index) {
            lines += `<tr class='itemrows'>
                  <td>
                      <i>${item.data.product_id[1]}</i>
                  </td>
                  <td align='right'>
                      ${item.data.price_subtotal}
                  </td>
              </tr>`
        });
        var iva = this.props.record.data.tax_totals.amount_total - this.props.record.data.tax_totals.amount_untaxed
        var html_info = `<div id='DivIdToPrint'>
            <style type='text/css'>
            body{
               font-size:16px;
                    line-height:24px;
                    font-family:'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
                    color:#555;
            }
            .heading{
                background:#ccc;
                font-weight:bold;
            }
            .heading td{
                padding: 10px 5px;
            }
            .itemrows{
                border-bottom:1px solid #555 !important;
            }
            .itemrows td{
                padding: 10px 0;
            }
            </style>
            <table cellpadding='0' cellspacing='0'>
                <table style='border:0;width:100%;border-collapse: collapse;'>
                <tr><td colspan='2' align='left'><b>${companies[0].name}</b></td></tr>
                <tr><td colspan='2' align='left'>${companies[0].street}, ${companies[0].city}, ${companies[0].state_id[1]}, ${companies[0].zip}</td></tr>
                <tr><td colspan='2' align='left'><b>${_t('Phone')}:</b> ${companies[0].phone}</td></tr>
                <tr><td style="padding: 20px 0"><b>${_t('Customer')}:</b> ${partners[0].name} </td><td align='right'><b>${_t('Reference')}:</b> # ${this.props.record.data.name}</td></tr>
                <tr><td colspan='2' style="padding: 20px 0; font-size: 18px;" align='left'><b>${_t('Quotation')}</b></td></tr>
                <tr class='heading'>
                    <td>
                        ${_t('Product')}
                    </td>
                    <td align='right'>
                        Subtotal
                    </td>
                </tr>
                ${lines}
                <tr class='total'>
                        <td></td>
                        <td align='right'>
                           <b>IVA:&nbsp;${iva.toFixed(2)}</b>
                        </td>
                    </tr>
                    <tr class='total'>
                        <td></td>
                        <td align='right'>
                           <b>Total:&nbsp;${this.props.record.data.tax_totals.amount_total.toFixed(2)}</b>
                        </td>
                    </tr>
                    </table>
                </table>
                </div>`
        var mywindow = window.open('', 'PRINT', 'height=800,width=600');
            mywindow.document.write('</head><body >');
            mywindow.document.write(html_info);
            mywindow.document.write('</body></html>');
            mywindow.document.close();
            mywindow.focus();
            mywindow.print();
            mywindow.close();

            return true;
    }
}

PrinterButton.template = 'sale_ext.PrinterButton'
PrinterButton.displayName = 'Printer Button'

registry.category('view_widgets').add('printer_button', PrinterButton);

