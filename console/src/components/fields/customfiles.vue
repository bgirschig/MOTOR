<template>
  <label class="labelfor">
    <span class="custom_files">
      Upload an image ({{fileCount}})
    </span>
    <input
      ref="input"
      type="file"
      @change="updateFiles"
      :name="config.name"
      :required="constraints.required"
      :multiple="constraints.maxCount != 1"
    />
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
label.labelfor {
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}
.custom_files {
  font-family: 'myFont';
  color: black;
}
@media screen and (max-width:  600px) {
  label.labelfor{
    height: 60px;
  }
  .custom_files{
    font-size: 20px;
  }
}
@media screen and (min-width:  600px) {
  label.labelfor{
    height: 100px;
  }
  .custom_files{
    font-size: 35px;
  }
}
</style>
