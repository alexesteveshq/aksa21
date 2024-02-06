odoo.define('dynamic_forms.snippets.options', function (require) {
    'use strict';

    const options = require('web_editor.snippets.options');
    const core = require('web.core');
    const _t = core._t;
    const ListUserValueWidget = options.userValueWidgetsRegistry['we-list'];

    ListUserValueWidget.include({
        events: Object.assign({}, ListUserValueWidget.prototype.events, {
            'click .radio_img_upload': '_onRadioImgUpload',
        }),

        start: function() {
            this.$target.find('.radio-img-container').attr('contenteditable', 'true');
            return this._super.apply(this, arguments)
        },

        _onRadioImgUpload(ev){
            var value = $(ev.target).attr('radio-value')
            this.$target.find("input[value='"+value+"']").parent().find('img').dblclick()
        },

        _addItemToTable(id, value = this.el.dataset.defaultValue || _t("Item"), recordData) {
            this._super.apply(this, arguments)
            if (this.$target.attr('data-type') === 'img_select'){
                var file = $("<we-button class='o_we_bg_brand_primary radio_img_upload' data-replace-media='true' data-no-preview='true'>Upload image</we-button>")
                file.attr('radio-value', value)
                const fileTdEl = document.createElement('td');
                fileTdEl.classList.add('o_we_list_record_name');
                fileTdEl.appendChild(file[0])
                $(this.listTable).find('tr:last td:eq(3)').after($(fileTdEl)[0])
            }
        },
    });
})
