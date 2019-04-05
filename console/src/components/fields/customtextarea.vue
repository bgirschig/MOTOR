<template>
  <label>
    <h3>{{config.displayName || config.name}}</h3>
    <textarea
      :name="config.name"
      cols="40"
      rows="10"
      :placeholder="config.placeholder"
      :value="config.value"
      :maxlength="constraints.maxlength"
      :required="constraints.required" />
  </label>
</template>

<script>
export default {
  props: {
    config: {
      default() {
        return {};
      },
    },
  },
  computed: {
    constraints() {
      const defaultConstraints = {
        maxlength: null,
        required: false,
      };
      return Object.assign(defaultConstraints, this.config.constraints);
    },
  },
};
</script>
