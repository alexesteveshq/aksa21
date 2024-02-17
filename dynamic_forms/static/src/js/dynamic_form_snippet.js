odoo.define('dynamic_forms.dynamic_form_snippet', function(require) {

    const publicWidget = require('web.public.widget');
    const core = require('web.core');
    const dom = require('web.dom');
    const _t = core._t;
    const ajax = require('web.ajax');
    require("website.s_website_form");
    const concurrency = require('web.concurrency');

    publicWidget.registry.DynamicForm = publicWidget.registry.s_website_form.extend({
        selector: '.s_dynamic_form form',

        addEvents: function(){
            var self = this
            this.$controls = this.$target.closest('.s_dynamic_form').find('.dynamic_form_controls').show()
            this.$controls.find('.s_website_form_prev').on("click", function(){self._prevSection(self)});
            this.$controls.find('.s_website_form_next').on("click", function(){self._nextSection(self)});
            this.$controls.find('.s_website_form_send').on("click", function(ev){self.send(ev)});
            this.$target.find("[data-type='integer'] input, [data-type='float'] input").on(
                "change", function(){self._calculateFormulas()});
            this.$target.find("[data-type='integer'], [data-type='float']").on("DOMSubtreeModified", function(ev){self._setNumberValue(ev)});
            this.$target.find("[data-type='formula']").on("DOMSubtreeModified", function(){self._calculateFormulas()});
            this.$target.find("select[name='state_partner_id']").on("change", function(ev){self._togglePartners(ev)});
            this.$target.find("select[name='partner_assigned_id']").on("change", function(ev){self._togglePartnerDescription(ev)});
        },
        start: function() {
            var self = this
            this.addEvents()
            return this._super(...arguments).then(() => {
                this._toggleElements()
                this._toggleFormulaFields()
                this.$target.find("select[name='partner_assigned_id']").val("")
            })
        },
        _toggleElements: function(){
            this.$target.find('[data-type="img_select"] .radio').show()
            this.$target.find('.s_dynamic_form_section').addClass('o_animate_in_dropdown')
            this.$target.parent().parent().find('.loading-dynamic').removeClass("active")
            this.$target.parent().find('.s_dynamic_form_section:first-child').addClass('active')
            this.$target.parent().find('.s_dynamic_form_section:not(:first)').removeClass("active")
            this._toggleControls()
        },
        _toggleFormulaFields: function(){
            var formulas = this.$target.find("[data-type='formula'] textarea")
            formulas.each(function() {
                $(this).attr("disabled", true).hide()
                $(this).after("<input name='"+$(this).attr('name')+"' class='formula_calc' disabled>");
            })
        },
        _setNumberValue: function(ev){
            if ($(ev.target).closest('.s_website_form_field').hasClass('s_website_form_field_hidden_if') &&
                $(ev.target).closest('.s_website_form_field').hasClass('d-none')){
                $(ev.target).val("").change()
            }
        },
         matchFormulaVariable: function(variable){
            var result = 0
            $('.s_website_form_input').each(function() {
                var inputName = $(this).attr('name');
                var convertedName = inputName.replace(/\s+/g, '_').toLowerCase();
                if (convertedName === variable){
                    var field = $(this).closest('.s_website_form_field')
                    if (field.hasClass('s_website_form_field_valid_if') && field.hasClass('d-none')){
                        result = 0
                        $('input[name="' + inputName + '"]').val(0);
                    }else{
                        value = $('input[name="' + inputName + '"]').val();
                        result = value !== '' ? value : 0
                    }
                }
            });
            return result
        },
        _calculateFormulas: function(only_validate=false){
            var formulas = this.$el.find('[data-type="formula"] textarea')
            var inputId = false
            var self = this
            formulas.each(function() {
              expr = $(this).val().replace(/#{([a-z0-9_]+)}/ig, function(match, variable) {
                  var inputValue = self.matchFormulaVariable(variable)
                  return inputValue;
                });
                try {
                   var result = eval(expr);
                   if ((typeof result !== 'number' || !isFinite(result)) && expr !== "") {
                      inputId = $(this).attr('id')
                   }else{
                      $(this).next().val(Math.trunc(result * 100) / 100)
                   }
                } catch (error) {
                   inputId = $(this).attr('id')
                }
            });
            return inputId
        },
        _toggleControls: function() {
            $('html, body').scrollTop(0);
            var current = this.$target.find('.s_dynamic_form_section.active')
            var prev = this.$controls.find('.s_website_form_prev')
            var next = this.$controls.find('.s_website_form_next')
            var submit = this.$controls.find('.s_website_form_submit')
            if (this.$target.find('.s_dynamic_form_section').length <= 1){
                this.$controls.find('.control-opt').removeClass("active")
                submit.addClass('active')
            }else if(!current.next().hasClass('s_dynamic_form_section')){
                prev.addClass('active')
                submit.addClass('active')
                next.removeClass("active")
            }else if(!current.prev().hasClass('s_dynamic_form_section')){
                prev.removeClass("active")
                next.addClass('active')
                submit.removeClass("active")
            }else{
                submit.removeClass("active")
                this.$controls.find('.control-opt:not(.s_website_form_submit)').addClass('active')
            }
        },
        _togglePartnerDescription: function(ev){
            var option = $(ev.target).find('option:selected')
            if (option.attr("website_short_description") !== 'false' && option.text() !== ''){
                var url = option.text().toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '') + "-" + option.val()
                $('.partner-img-logo').attr("src", "/web/image?model=res.partner&field=avatar_128&id="+option.val())
                $('.partner-title').html("<a href=/partners/"+url+" target='_blank'>"+option.text()+"</a>")
                $('.partner-info').html(option.attr("website_short_description"))
                $('.partner-info-wrapper').addClass('active')
            }else{
                $('.partner-info-wrapper').removeClass('active')
            }
        },
        _addHtmlContent: function(form_values, input){
            var html_field =$("[name='" + input.name + "']").closest(
            "[data-type='html_editor']:not(.s_website_form_report_hide)")
            $(html_field).each(function() {
                var input_name = $(this).find("input").attr('name')
                var html_body = $(this).find(".s_allow_columns").html()
                form_values[input_name] = html_body
            })
            var radio_img_field = $("[name='" + input.name + "']").closest("[data-type='img_select']")
            $(radio_img_field).each(function() {
                $(this).find("input:not(:checked)").closest('.radio').hide()
                var input_name = $(this).find("input").attr('name')
                var html_body = $(this).find("input:checked").parent().find('.radio-img-container').html()
                form_values[input_name] = $(this).find("input:checked").val()
                form_values["#html_"+input_name] = html_body
            })
        },
        send: async function (e) {
            e.preventDefault();
            const $button = this.$target.closest('.s_dynamic_form').find('.s_website_form_send, .o_website_form_send');
            this.$target.find('[data-type="formula"]:not(.d-none) .formula_calc').removeAttr('disabled').prev().attr('disabled', 'disabled');
            $button.addClass('disabled').attr('disabled', 'disabled');
            this.restoreBtnLoading = dom.addButtonLoadingEffect($button[0]);

            var self = this;

            self.$target.find('#s_website_form_result, #o_website_form_result').empty();
            if (!self.check_error_fields({})) {
                self.update_status('error', _t("Please fill in the form correctly."));
                return false;
            }
            this.form_fields = this.$target.serializeArray();
            $(this.$target.find('.s_website_form_concat_name')).each(function() {
                var inputValue = $(this).find('input').val();
                self.form_fields.forEach(item => {
                    if (item['name'] === 'name') {
                        item['value'] = item['value'] + " " + inputValue
                    }
                });
            })
            var revenue = $(this.$target.find('.s_website_form_expected_revenue:not(.d-none)'))
            if (revenue.length > 0 && !this.form_fields.find(item => item.name === 'expected_revenue')){
                var inputValue = revenue.find('.formula_calc').val();
                this.form_fields.push({name: 'expected_revenue', value: inputValue})
            }

            $(this.$target.find(".s_website_form_field")).each(function() {
                var inputLabel = $(this).find('.s_website_form_label_content').text();
                var inputName = $(this).find('[name]').attr('name');
                if (inputLabel !== inputName){
                    self.form_fields.forEach(item => {
                        if (item['name'] === inputName) {
                            item['name'] += inputLabel
                        }
                    });
                }
            })

            $.each(this.$target.find('input[type=file]:not([disabled])'), (outer_index, input) => {
                $.each($(input).prop('files'), function (index, file) {
                    self.form_fields.push({
                        name: input.name + '[' + outer_index + '][' + index + ']',
                        value: file
                    });
                });
            });
            var form_values = {};
            _.each(this.form_fields, function (input) {
                if (input.name in form_values) {
                    if (Array.isArray(form_values[input.name])) {
                        form_values[input.name].push(input.value);
                    } else {
                        form_values[input.name] = [form_values[input.name], input.value];
                    }
                } else {
                    if (input.value !== '') {
                        form_values[input.name] = input.value;
                    }
                    self._addHtmlContent(form_values, input)
                }
            });
            this.$target.find('.s_website_form_field:not(.s_website_form_custom)')
            .find('.s_website_form_date, .s_website_form_datetime').each(function () {
                const inputEl = this.querySelector('input');
                if (!inputEl.value) {
                    return;
                }
                var date = $(this).datetimepicker('viewDate').clone().locale('en');
                var format = 'YYYY-MM-DD';
                if ($(this).hasClass('s_website_form_datetime')) {
                    date = date.utc();
                    format = 'YYYY-MM-DD HH:mm:ss';
                }
                form_values[inputEl.getAttribute('name')] = date.format(format);
            });

            if (this._recaptchaLoaded) {
                const tokenObj = await this._recaptcha.getToken('website_form');
                if (tokenObj.token) {
                    form_values['recaptcha_token_response'] = tokenObj.token;
                } else if (tokenObj.error) {
                    self.update_status('error', tokenObj.error);
                    return false;
                }
            }
            this.$target.closest('.s_dynamic_form').find('.s_website_form_prev').removeClass('active')
            ajax.post(this.$target.attr('action') + (this.$target.data('force_action') || this.$target.data('model_name')), form_values)
            .then(async function (result_data) {
                result_data = JSON.parse(result_data);
                if (!result_data.id) {
                    self.update_status('error', result_data.error ? result_data.error : false);
                    if (result_data.error_fields) {
                        self.check_error_fields(result_data.error_fields);
                    }
                } else {
                    let successMode = self.$target[0].dataset.successMode;
                    let successPage = self.$target[0].dataset.successPage;
                    if (!successMode) {
                        successPage = self.$target.attr('data-success_page'); // Compatibility
                        successMode = successPage ? 'redirect' : 'nothing';
                    }
                    switch (successMode) {
                        case 'redirect': {
                            let hashIndex = successPage.indexOf("#");
                            if (hashIndex > 0) {
                                let currentUrlPath = window.location.pathname;
                                if (!currentUrlPath.endsWith("/")) {
                                    currentUrlPath = currentUrlPath + "/";
                                }
                                if (!successPage.includes("/#")) {
                                    successPage = successPage.replace("#", "/#");
                                    hashIndex++;
                                }
                                if ([successPage, "/" + session.lang_url_code + successPage].some(link => link.startsWith(currentUrlPath + '#'))) {
                                    successPage = successPage.substring(hashIndex);
                                }
                            }
                            if (successPage.charAt(0) === "#") {
                                const successAnchorEl = document.getElementById(successPage.substring(1));
                                if (successAnchorEl) {
                                    await dom.scrollTo(successAnchorEl, {
                                        duration: 500,
                                        extraOffset: 0,
                                    });
                                }
                                break;
                            }
                            $(window.location).attr('href', successPage);
                            return;
                        }
                        case 'message': {
                            self.$target[0].classList.add('d-none');
                            self.$target[0].parentElement.querySelector('.s_website_form_end_message').classList.remove('d-none');
                            self.$target.closest('.s_dynamic_form').find('.dynamic_form_controls').hide()
                            self.$target.closest('.s_dynamic_form').find('.download-report').attr('href', result_data.report)
                            break;
                        }
                        default: {
                            await concurrency.delay(dom.DEBOUNCE);
                            self.update_status('success');
                            break;
                        }
                    }

                    self.$target[0].reset();
                    self.restoreBtnLoading();
                }
            })
            .guardedCatch(error => {
                this.update_status(
                    'error',
                    error.status && error.status === 413 ? _t("Uploaded file is too large.") : "",
                );
            });
        },
        _togglePartners: function(ev) {
            var select = this.$target.find("select[name='partner_assigned_id']")
            select.find("option[state_id="+$(ev.target).val()+"]").show()
            select.find("option[state_id!="+$(ev.target).val()+"]").hide()
            select.val("")
            $('.partner-title').html("")
            $('.partner-info').html("")
        },
        _nextSection: function(self) {
            var current = self.$target.find('.s_dynamic_form_section.active')
            var nextElem = current.next()
            var editable = self.$target.closest('.o_editable')
            if (nextElem.hasClass('s_dynamic_form_section') && editable.length === 0){
                current.removeClass("active")
                nextElem.addClass('active')
                self._toggleControls()
            }
        },
        _prevSection: function(self) {
            var current = self.$target.find('.s_dynamic_form_section.active')
            var prevElem = current.prev()
            var editable = self.$target.closest('.o_editable')
            if (prevElem.hasClass('s_dynamic_form_section') && editable.length === 0){
                current.removeClass("active")
                prevElem.addClass('active')
                self._toggleControls()
            }
        },
    });
});
