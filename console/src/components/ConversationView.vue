<template>
  <div class="conversation"></div>
</template>

<script>
import {ConversationalForm} from 'conversational-form';
import * as formsClient from '../formClient';
import {seconds} from '@/utils/promises';

/**
 * @param {Object[]} fields A list of objects describing each element in the form
 * @return {Object[]} A list of objects, to be used with conversationnal-form
 */
function formFieldsToConversation(fields) {
  const typeMapping = {
    'files': 'file',
  };

  return fields.map((field) => {
    const label = field.displayName || field.name;
    const output = {
      'tag': 'input',
      'type': typeMapping[field.type] || field.type,
      'name': field.name,
      'cf-questions': field.question || field.displayName || field.name,
    };

    if ('placeholder' in field) output['cf-input-placeholder'] = field.placeholder;

    if ('constraints' in field) {
      output.min = field.constraints.min;
      output.max = field.constraints.max;
      output.minlength = field.constraints.minLength;
      output.maxlength = field.constraints.maxLength;
      output.required = field.constraints.required;

      // Number constraints
      if (output.min !== undefined && output.max !== undefined) {
        output['cf-error'] = `'${label}' must be between ${output.min} and ${output.max}`;
      } else if (output.min !== undefined) {
        output['cf-error'] = `'${label}' must be more than ${output.min}`;
      } else if (output.max !== undefined) {
        output['cf-error'] = `'${label}' must be less than ${output.max}`;
      }

      // Text length
      if (output.minlength !== undefined && output.maxlength !== undefined) {
        output['cf-error'] = `
          '${label}' must be between ${output.minlength} and ${output.maxlength} characters long`;
      } else if (output.minlength !== undefined) {
        output['cf-error'] = `'${label}' must be more than ${output.minlength} characters long`;
      } else if (output.maxlength !== undefined) {
        output['cf-error'] = `'${label}' must be less than ${output.maxlength} characters long`;
      }
    }

    if (output['cf-error']) output['cf-error'] = output['cf-error'].trim();

    return output;
  });
}

export default {
  async mounted() {
    const definition = await formsClient.getForm(this.$route.params.id, 'json', true);
    this.conversationTags = formFieldsToConversation(definition.fields);

    this.cf = ConversationalForm.startTheConversation({
      options: {
        submitCallback: this.onSubmit,
        preventAutoFocus: false,
        preventAutoStart: true,
        showProgressBar: true,
        context: this.$el,
      },
      tags: this.conversationTags,
    });

    // Fake loading sequence, because of a bug with conversationnal form:
    // - If we want actual preload messages like below, we need to initialize the cf without tags
    // - Then use cf.addTags(...) to push the retrieved questions
    // - However, when doing that, when we ask cf for the formData, it's empty (*this* is the bug)
    // - Serialized data works (cf.getFormData(true)), but we need real formdata because we have to
    // handle files
    this.cf.addRobotChatResponse(`
Hi!
We\'re settings things up...`.trim());
    await seconds(1.3);
    this.cf.addRobotChatResponse(`
We're good to go!
Together, we'll be creating a video for <strong>${definition.title}</strong>`.trim());
    await seconds(0.3);
    this.cf.start();
  },
  methods: {
    async onSubmit() {
      const formdata = this.cf.getFormData();
      this.cf.addRobotChatResponse('We\'re saving your request... Please wait a few seconds');
      const success = await formsClient.submit(this.$route.params.id, formdata);

      if (success) {
        this.cf.addRobotChatResponse('You\'re done here. We\'ll let you know when your video is' +
          ' ready.');
      } else {
        this.cf.addRobotChatResponse('Damn! Something went wrong. would you like to try again ?');
      }
    },
  },
};
</script>

<style scoped>
.conversation {
  width: 100%;
  height: 100%;
}
</style>
