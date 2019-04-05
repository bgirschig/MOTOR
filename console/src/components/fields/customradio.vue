<template>
  <div>
    <h3>{{config.displayName || config.name}}</h3>
    <label
      v-for="choice in config.choices"
      v-bind:key="choice">
        <input
          v-if="choice !== '_other'"
          :checked="config.default === choice"
          type="radio"
          :name="config.name"
          :value="choice">
        <div v-else class="option_other">
          <input
            type="radio"
            :name="config.name"
            :checked="config.default === choice"
            value="other">
          <input
            type="text"
            :name="config.name+'_other'"
            :placeholder="config.placeholder || 'other....'"
            :value="config.value"
            :maxlength="config.constraints.maxlength"
          >
        </div>
        {{choice !== '_other' ? choice : ''}}
    </label>
  </div>
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
      console.log(this.config);
      const defaultConstraints = {
        maxlength: null,
        required: false,
      };
      return Object.assign(defaultConstraints, this.config.constraints);
    },
  },
};
</script>
