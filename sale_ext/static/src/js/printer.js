/** @odoo-module **/

import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";

const { Component } = owl;

export class PrinterButton extends Component {
    async onClick() {
        var mywindow = window.open('', 'PRINT', 'height=400,width=600');
            mywindow.document.write('<html><head><title>test</title>');
            mywindow.document.write('</head><body >');
            mywindow.document.write('<h1>Test</h1>');
            mywindow.document.write('<div>Test</div>');
            mywindow.document.write('</body></html>');
            mywindow.document.close();
            mywindow.focus();
            mywindow.print();
            mywindow.close();

            return true;
    }
}

PrinterButton.template = "sale_ext.PrinterButton"
PrinterButton.displayName = "Printer Button"

registry.category("view_widgets").add("printer_button", PrinterButton);

