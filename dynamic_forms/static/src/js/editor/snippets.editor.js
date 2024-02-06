odoo.define('dynamic_forms.snippet.editor', function (require) {
    'use strict';

    const snippetEditor = require('web_editor.snippet.editor');

    snippetEditor.SnippetEditor.include({
        _initializeOptions: function () {
            var self = this;
            return this._super.apply(this, arguments).then(() => {
                if (self.$target.parent().hasClass('s_dynamic_form_section')){
                    self.$optionsSection.find('.snippet-option-AddField').remove()
                }
            });
        },
        removeSnippet: async function (shouldRecordUndo = true) {
            if (this.$target.attr('data-snippet') === 's_text_block' &&
             this.$target.closest('.s_website_form_field') > 0){
                this.$target = this.$target.closest('.s_website_form_field')
            }
            if (this.$target.closest('.partner-field-wrapper').length > 0){
                this.$target = this.$target.closest('.partner-field-wrapper')
            }
            this._super.apply(this, arguments);
        },
    });

    snippetEditor.SnippetsMenu.include({
        _activateSnippet: async function($snippet, previewMode, ifInactiveOptions) {
            return this._super.apply(this, arguments).then(() => {
                var SectionHtmlEditor = $(this.lastElement).closest('.section_text_block')
                if (SectionHtmlEditor.length > 0){
                    SectionHtmlEditor.attr('contenteditable', true);
                }
            })
        },
    });

})
