<!-- The end user's product: renders the form he can use to request a video -->

<template>
  <div id="FormView">
    Hi there {{$route.params.id}}
  </div>
</template>

<script>
import {getForm} from '../formClient';
export default {
  name: 'FormView',
  mounted() {
    getForm('xenix');
    console.log('hi!');
  },
};
</script>
