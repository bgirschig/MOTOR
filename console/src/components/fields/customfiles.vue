<template>
  <label>
    <h3>{{config.displayName || config.name}} <span>({{fileCount}})</span></h3>
    <input
      ref="input"
      type="file"
      @change="updateFiles"
      :name="config.name"
      :required="constraints.required"
      :multiple="constraints.maxCount != 1">
  </label>
</template>

<script>
export default {
  data() {
    return {
      files: [],
    };
  },
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
    fileCount() {
      return this.files.length;
    },
  },
  methods: {
    updateFiles() {
      if (!this.$refs.input) this.files = null;
      else this.files = this.$refs.input.files;
    },
  },
};
</script>
<style scoped>
label {
  cursor: pointer;
}
</style>
