<template>
    <div ref="form" />
</template>

<script>
import Form from "mvc/form/form-view";

export default {
    props: {
        id: {
            type: String,
            default: null,
        },
        inputs: {
            type: Array,
            required: true,
        },
        textEnable: {
            type: String,
            default: null,
        },
        textDisable: {
            type: String,
            default: null,
        },
        initialErrors: {
            type: Boolean,
            default: false,
        },
        validationScrollTo: {
            type: Array,
            default: null,
        },
        validationErrors: {
            type: Object,
            default: null,
        },
        formConfig: {
            type: Object,
            default: null,
        },
    },
    data() {
        return {
            formData: {},
        };
    },
    watch: {
        id() {
            this.onRender();
        },
        validationScrollTo() {
            this.onHighlight(this.validationScrollTo);
        },
        validation() {
            this.onHighlight(this.validation, true);
            this.$emit("onValidation", this.validation);
        },
        validationErrors() {
            const matchedErrors = Object.entries(this.form.data.matchResponse(this.validationErrors));
            if (matchedErrors.length > 0) {
                this.onHighlight(matchedErrors[0]);
            }
        },
        formConfig() {
            this.$nextTick(() => {
                this.form.update(this.formConfig);
                if (this.initialErrors) {
                    this.form.errors(this.formConfig);
                }
            });
        },
    },
    mounted() {
        this.onRender();
    },
    beforeDestroy() {
        this.form.off();
    },
    computed: {
        validation() {
            let batch_n = -1;
            let batch_src = null;
            for (const job_input_id in this.formData) {
                const input_value = this.formData[job_input_id];
                const input_id = this.form.data.match(job_input_id);
                const input_field = this.form.field_list[input_id];
                const input_def = this.form.input_list[input_id];
                if (!input_id || !input_def || !input_field) {
                    continue;
                }
                if (!input_def.optional && input_value == null && input_def.type != "hidden") {
                    return [input_id, "Please provide a value for this option."];
                }
                if (input_field.validate) {
                    const message = input_field.validate();
                    if (message) {
                        return [input_id, message];
                    }
                }
                if (input_value && input_value.batch) {
                    const n = input_value.values.length;
                    const src = n > 0 && input_value.values[0] && input_value.values[0].src;
                    if (src) {
                        if (batch_src === null) {
                            batch_src = src;
                        } else if (batch_src !== src) {
                            return [
                                input_id,
                                "Please select either dataset or dataset list fields for all batch mode fields.",
                            ];
                        }
                    }
                    if (batch_n === -1) {
                        batch_n = n;
                    } else if (batch_n !== n) {
                        return [
                            input_id,
                            `Please make sure that you select the same number of inputs for all batch mode fields. This field contains <b>${n}</b> selection(s) while a previous field contains <b>${batch_n}</b>.`,
                        ];
                    }
                }
            }
            return null;
        },
    },
    methods: {
        onChange() {
            this.formData = this.form.data.create();
            this.$emit("onChange", this.formData);
        },
        onRender() {
            this.$nextTick(() => {
                const el = this.$refs["form"];
                this.form = new Form({
                    el,
                    inputs: this.inputs,
                    initial_errors: this.initialErrors,
                    text_enable: this.textEnable,
                    text_disable: this.textDisable,
                    onchange: () => {
                        this.onChange();
                    },
                });
                this.onChange();
            });
        },
        onHighlight(validation, silent = false) {
            this.form.trigger("reset");
            if (validation && validation.length == 2) {
                this.form.highlight(validation[0], validation[1], silent);
            }
        },
    },
};
</script>
