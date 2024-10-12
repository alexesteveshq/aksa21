/** @odoo-module **/

import { _t } from '@web/core/l10n/translation';
import paymentForm from '@payment/js/payment_form';
import { RPCError } from '@web/core/network/rpc_service';

paymentForm.include({

    /**
     * Prepare the inline form of StaxPay for direct payment.
     *
     * @override method from payment.payment_form
     * @private
     * @param {number} providerId - The id of the selected payment option's provider.
     * @param {string} providerCode - The code of the selected payment option's provider.
     * @param {number} paymentOptionId - The id of the selected payment option
     * @param {string} paymentMethodCode - The code of the selected payment method, if any.
     * @param {string} flow - The online payment flow of the selected payment option
     * @return {void}
     */
    async _prepareInlineForm(providerId, providerCode, paymentOptionId, paymentMethodCode, flow) {
        if (providerCode !== 'staxpay') {
            this._super(...arguments);
            return;
        }

        this.staxCheckout = new StaxJs('Visionee-782ca23c08a6', {
            number: {
                id: 'card-number',
                placeholder: '0000 0000 0000 0000',
                type: 'tel',
                format: 'prettyFormat',
            },
            cvv: {
                id: 'card-cvv',
                placeholder: 'CVV',
                type: 'text',
                format: 'prettyFormat',
            }
        });

        // Load the card form
        this.staxCheckout.showCardForm().then((handler) => {
            console.log("form was loaded");
        }).catch((err) => {
          console.log("there was an error loading the form: ", err);
        });
    },

    _initiatePaymentFlow(providerCode, paymentOptionId, paymentMethodCode, flow) {
        if (providerCode !== 'staxpay') {
            this._super(...arguments);
            return;
        }

        const extraDetails = {
          total: 0.01,
          firstname: "John",
          lastname: "Doe",
          month: "10",
          year: "2024",
          phone: "5555555555",
          address_1: "100 S Orange Ave",
          address_2: "Suite 400",
          address_city: "Orlando",
          address_state: "FL",
          address_zip: "32811",
          address_country: "USA",
          send_receipt: false,
          match_customer: false,
          validate: false,
          meta: {
            poNumber: "7649", // customer code used for L2 processing.
            shippingAmount: 0, // the shipping amount for the transaction used for L2 processing
            invoice_merchant_custom_fields: [
              {
                id: "dc4b-6c74-00dd-fab1-fe00", // Required, must be a unique string.
                name: "External ID", // The name of the custom field that will be displayed to your customers and users; this will appear above the field as a label.
                placeholder: "Ex. #123", // The placeholder for the field; this is the faint text that will appear in the entry box of your custom field to help guide your users before they enter in the value when creating an Invoice.
                required: true, // Determines if this field is required to be filled by the user (not customer) when first creating an Invoice.
                type: "text", // Input type. Only 'text' is supported.
                value: "123456789", // The value that will appear when viewing the Invoice or Invoice Email. For the merchant, this will also appear when viewing the Invoice via the Invoices or Edit Invoice pages.
                visible: true, // This determines if the field is visible when viewing the Invoice or Invoice Email. If false, will only appear in merchant-facing pages such as the Invoices or Edit Invoice pages.
              },
            ],
          },
        };

        this.staxCheckout.pay(extraDetails).then((response) => {
          console.log("invoice object:", response);
          console.log("transaction object:", response.child_transactions[0]);
        }).catch((err) => {
          console.log("unsuccessful payment:", err);
          this._enableButton();
        });

        this._super(...arguments);
    },
});
