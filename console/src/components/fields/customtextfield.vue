<template>
  <label>
    <!-- <h3>{{config.displayName || config.name}}</h3> -->
    <input
      class="cells"
      style="color: black"
      :name="config.name"
      type="text"
      :placeholder="config.placeholder"
      :value="config.value"
      :maxlength="constraints.maxLength"
      :required="constraints.required"
    />
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
<style scoped>
input.cells {
  font-family: 'myFont';
  text-align: center;
  text-transform: capitalize;
  padding: 0px;
}
input::placeholder {
  color: #f0f0f0;
}
@media screen and (max-width:  600px) {
  input{
    font-size: 20px;
    height: 60px;
  }
}
@media screen and (min-width:  600px) {
  input{
    font-size: 35px;
    height: 100px;
  }
}
</style>
