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
        clone: async function(recordUndo) {
            this.trigger_up('snippet_will_be_cloned', {
                $target: this.$target
            });
            var $clone = this.$target.clone(false);
            this.$target.after($clone);
            if (recordUndo) {
                this.options.wysiwyg.odooEditor.historyStep(true);
            }
            if (!['html_editor', 'img_select'].includes(this.$target.attr('data-type'))){
                await new Promise(resolve=>{
                    this.trigger_up('call_for_each_child_snippet', {
                        $snippet: $clone,
                        callback: function(editor, $snippet) {
                            for (var i in editor.styles) {
                                editor.styles[i].onClone({
                                    isCurrent: ($snippet.is($clone)),
                                });
                            }
                        },
                        onSuccess: resolve,
                    });
                }
                );
            }
            this.trigger_up('snippet_cloned', {
                $target: $clone,
                $origin: this.$target
            });
            $clone.trigger('content_changed');
        },
        removeSnippet: async function (shouldRecordUndo = true) {
            if (this.$target.attr('data-snippet') === 's_text_block' &&
             this.$target.closest('.s_website_form_field').length > 0){
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
