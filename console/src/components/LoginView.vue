<template>
  <div class="LoginView">
    <h1>Welcome to Kairos - MOTOR</h1>
    <div id="firebaseui-auth-container"></div>
  </div>
</template>

<script>
import {firebase, firebaseui} from '@/firebase';
const ui = new firebaseui.auth.AuthUI(firebase.auth());

export default {
  name: 'LoginView',
  mounted() {
    // const nextRoute = this.$route.query.next || '/';
    // let nextHref = window.location.href.split('#')[0];
    // nextHref += '#' + nextRoute;
    const uiConfig = {
      // signInSuccessUrl: nextHref,
      signInOptions: [
        firebase.auth.GoogleAuthProvider.PROVIDER_ID,
        firebase.auth.EmailAuthProvider.PROVIDER_ID,
      ],
      tosUrl: '',
      privacyPolicyUrl: '',
    };

    ui.start('#firebaseui-auth-container', uiConfig);
  },
};
</script>

<style scoped>
  .LoginView {
    text-align: center;
    width: 100%;
  }
</style>
