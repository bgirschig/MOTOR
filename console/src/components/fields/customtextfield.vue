<template>
  <label>
    <h3>{{config.displayName || config.name}}</h3>
    <input
      :name="config.name"
      type="text"
      :placeholder="config.placeholder"
      :value="config.value"
      :maxlength="constraints.maxLength"
      :required="constraints.required">
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
