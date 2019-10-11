<template>
  <label class="field">
    <!-- <h3>{{config.displayName || config.name}}</h3> -->
    <template v-if="config.type === 'textfield'">
      <input
        class="cells"
        :name="config.name"
        type="text"
        :placeholder="changeCapitalize()"
        :value="config.value"
        :maxlength="constraints.maxLength"
        :required="constraints.required"
      />
    </template>
    <template v-else-if="config.type === 'textarea'">
      <textarea
        class="cells"
        :name="config.name"
        type="text"
        :placeholder="changeCapitalize()"
        :value="config.value"
        :maxlength="constraints.maxLength"
        :required="constraints.required"
      />
    </template>
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
  methods: {
    changeCapitalize: function() {
      const placeholder = this.config.placeholder;
      return placeholder.charAt(0).toUpperCase() + placeholder.slice(1);
    },
  },
};
</script>
<style scoped>
.field textarea {
  font-family: 'myFont';
  text-align: center;
  padding: 0px;
  color: black;
  resize: none;
  border-bottom: 1px solid;
  padding-top: 30px;
  word-break: break-all;
  overflow-y: scroll;
  overflow-x: hidden;
  height: 100px;
}
input.cells {
  font-family: 'myFont';
  text-align: center;
  padding: 0px;
  color: black;
  border-bottom: 1px solid;
  height: 100px;
}
.field textarea::placeholder, input::placeholder {
  color: #f0f0f0;
}
@media screen and (max-width:  600px) {
  .field textarea{
    font-size: 20px;
    padding-top: 15px;
    word-break: break-all;
    height: 60px;
  }
  input.cells{
    font-size: 20px;
    height: 60px;
  }
}
@media screen and (min-width:  600px) {
  .field textarea{
    font-size: 35px;
    padding-top: 30px;
    word-break: break-all;
    height: 100px;
  }
  input.cells{
    font-size: 35px;
    height: 100px;
  }
}
</style>
