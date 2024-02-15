odoo.define('dynamic_forms.dynamic_form', function (require) {
'use strict';

const options = require('web_editor.snippets.options');
const FormEditor = require('website.form_editor');
const core = require('web.core');
const qweb = core.qweb;
const _t = core._t;

options.registry.DynamicFormEditor = options.registry.WebsiteFormEditor.extend({
    events: _.extend({}, options.Class.prototype.events || {}, {
        'click .toggle-edit-message': '_toggleMessageClick',
    }),
    start: function() {
        this._super.apply(this, arguments)
        this.toggleElements()
        if (this.$target.find('.s_dynamic_form_section').length === 0){
            var section = this._renderSection()
            this.$target.find('.dynamic_form_content, .s_website_form_recaptcha').first().before(section);
            this.trigger_up('activate_snippet', {
                $snippet: $(section),
            });
            this.$target.find('.s_dynamic_form_section .section_text_block').attr('contenteditable', 'true');
        }
    },
     _toggleMessageClick: function(){
        this.showEndMessage = !this.showEndMessage;
        if (this.showEndMessage){
            this.$message.addClass('d-block-msg')
        }else{
            this.$message.removeClass('d-block-msg')
        }
    },
    toggleElements: function(){
        var form = this.$target
        form.parent().parent().find('.loading-dynamic').removeClass("active")
        form.parent().parent().find('.dynamic_form_controls').show()
        this.$target.find('.s_dynamic_form_section').addClass('active')
        this.$target.find('[data-type="img_select"] .radio').show()
        this.$target.closest('.s_dynamic_form').find('.control-opt').addClass('active')
        this.$target.find("select[name='partner_assigned_id']").closest('.s_website_form_field').show()
        this.$target.find("[data-type='formula'] textarea").attr('disabled', false).show()
        this.$target.find(".formula_calc").remove()
    },
    onSuccess: function(previewMode, value, params) {
        var self = this
        this.$target[0].dataset.successMode = value;
        if (value === 'message') {
            if (!this.$message.length) {
                this.$message = $(qweb.render('website.s_website_form_end_message_download_report'));
            }
            this.$target.before(this.$message);
        } else {
            this.showEndMessage = false;
            this.$message.remove();
        }
    },
    cleanForSave: function () {
        this._super.apply(this, arguments)
        this.$target[0].querySelectorAll('#editable_select').forEach(el => {
            $(el).prev().show()
            el.remove()});
        this.$message.removeClass('d-block-msg')
        this.$target.parent().find('.loading-dynamic').addClass("active")
        this.$target.parent().parent().find('.loading-dynamic').addClass("active")
        this.$target.find('.control-opt').addClass('active')
    },
    _renderSection: function(){
        var section = document.createElement('div');
        section.innerHTML = "<div class='s_website_form_label'></div>";
        section.setAttribute('data-name', "Section");
        section.className = 's_dynamic_form_section  s_website_form_rows row active';
        return section
    },
});

options.registry.AddSectionForm = options.registry.DynamicFormEditor.extend({
    isTopOption: true,
    isTopFirstOption: true,

    start: function() {
        this._super.apply(this, arguments)
        this.$el.children().not('.add-section').remove()
    },

    addSection: async function (previewMode, value, params) {
        var section = this._renderSection()
        this.$target.find('.dynamic_form_content, .s_website_form_recaptcha').first().before(section);
        this.trigger_up('activate_snippet', {
            $snippet: $(section),
        });
    },
});

options.registry.AddFieldSection = options.registry.AddFieldForm.extend({
    isTopOption: true,
    isTopFirstOption: true,

    start: function() {
        this._super.apply(this, arguments)
        this.$el.children().find('.snippet-option-AddField').remove()
        this.$target.find('.s_text_block .container').attr('contenteditable', 'true');
    },

    addSectionField: async function (previewMode, value, params) {
        const field = this._getCustomField('char', 'Custom Text');
        field.formatInfo = this._getDefaultFormat();
        const fieldEl = this._renderField(field);
        this.$target.append(fieldEl);
        this.trigger_up('activate_snippet', {
            $snippet: $(fieldEl),
        });
    },
});

options.registry.WebsiteFieldEditor.include({
    _rerenderXML: async function(callback) {
        var self = this;
        return this._super.apply(this, arguments).then(() => {
            if (this.$target.attr('data-type') === 'formula'){
                var input = this.$el.children("[data-select-textarea-value]").find('input').hide()
                var textarea = $('<textarea autocomplete="chrome-off" placeholder="" class="text-start" style="height: 100px;"></textarea>');
                textarea.val(input.val())
                input.after(textarea);
                textarea.on('input', function() {
                    input.val($(this).val());
                    input.trigger('input');
                });
            }
            if (this.$target.attr('data-type') === 'html_editor'){
                this.$el.children('[data-attribute-name="placeholder"], [data-name="required_opt"]').remove()
            }
            if (this.$target.attr('data-type') !== 'char'){
                this.$el.children('[data-name="concat_name"]').remove()
            }
            if (this.$target.attr('data-type') !== 'formula'){
                this.$el.children('[data-name="expected_revenue"]').remove()
            }
        });
    },
    _fetchFieldRecords: async function(field) {
        if (field.name === 'state_partner_id'){
            if (field.records) {
                return field.records;
            }
            field.records = await this._rpc({
                model: field.relation,
                method: 'get_states_published',
                args: [0],
            });
            return field.records
        }
        if (field.name === 'partner_assigned_id'){
            const partners = await this._rpc({
                model: field.relation,
                method: 'search_read',
                args: [[['is_published', '=', true]], ['display_name', 'state_id', 'website_short_description']],
            });
            if (field.records) {
                field.records.forEach(item => {
                    const match = partners.find(obj => obj.id === item.id);
                    if (match) {
                        item.state_id = match.state_id;
                        item.website_short_description = match.website_short_description;
                    }
                });
                return field.records
            }
            field.records = partners
            return field.records
        }
        return this._super.apply(this, arguments)
    },
    _getCustomField: function (type, name) {
        var field = this._super.apply(this, arguments)
        field.records.forEach(function(record) {
          record.img_src = "/web/image/web.image_placeholder"
        });
        return field
    },
    _setPartnerFieldData: async function(value, domain){
        var field = Object.assign({}, this.fields[value]);
        field.domain = domain
        field.formatInfo = this._getFieldFormat()
        await this._fetchFieldRecords(field);
        return field
    },
    _replaceField: async function(field) {
        if (field.type === 'partner'){
            var self = this
            var elems = []
            var data = [{value: 'state_partner_id',
                 domain: [['id', 'in', [13, 14, 15, 33, 659, 47]]]},
                {value: 'partner_assigned_id',
                 domain: [['is_published', '=', true]]}]
            data.forEach(function(item) {
               elems.push(self._setPartnerFieldData(item.value, item.domain))
            });
            await Promise.all(elems).then((result) => {
                this._replaceFieldElement(this._renderField(result[1]));
                this.$target.before(this._renderField(result[0]))
                this.$target.prev().addBack().wrapAll("<div class='partner-field-wrapper' data-name='Partner'></div>")
            })
        }else if(field.type === 'html_editor' && this.$target.find('.s_allow_columns').length > 0){
            var new_html = this._renderField(field)
            $(new_html).find('.s_allow_columns').replaceWith(this.$target.find('.s_allow_columns')[0])
            this._replaceFieldElement(new_html)
        }else{
            await this._super(...arguments);
        }
    },
    _setActiveProperties(field) {
        this._super.apply(this, arguments)
        const classList = this.$target[0].classList;
        field.hide_in_report = classList.contains('s_website_form_report_hide');
        field.use_for_name = classList.contains('s_website_form_concat_name');
        field.expected_revenue = classList.contains('s_website_form_expected_revenue');
    },
    _getListItems: function() {
        const select = this._getSelect();
        const multipleInputs = this._getMultipleInputs();
        let options = [];
        if (select) {
            options = [...select.querySelectorAll('option')];
        } else if (multipleInputs) {
            options = [...multipleInputs.querySelectorAll('.checkbox input, .radio input')];
        }
        return options.map(opt=>{
            const name = select ? opt : opt.nextElementSibling;
            return {
                id: /^-?[0-9]{1,15}$/.test(opt.value) ? parseInt(opt.value) : opt.value,
                display_name: name.textContent.trim(),
                selected: select ? opt.selected : opt.checked,
                img_src: $(opt).parent().find('.radio-img-item').attr("src")
            };
        }
        );
    },
})

});