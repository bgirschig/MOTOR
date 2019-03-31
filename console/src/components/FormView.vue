<!-- The end user's product: renders the form he can use to request a video -->

<template>
  <div id="FormView">
    Hi there {{$route.params.id}}<br>
    {{fields}}
  </div>
</template>

<script>
import {getForm} from '../formClient';
export default {
  name: 'FormView',
  data() {
    return {
      title: '',
      logo: '',
      fields: [],
    };
  },
  async mounted() {
    const definition = await getForm('creditSuisse');
    this.fields = definition.fields;
    this.title = definition.title;
    this.logo = definition.logo;
  },
};
</script>
