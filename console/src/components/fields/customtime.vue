<template>
  <label>
    <h3>{{config.displayName || config.name}}</h3>
    <label>
      <input
        type="time"
        :name="config.name"
        :min="constraints.min" :max="constraints.max"
        :required="constraints.required">
    </label>
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
