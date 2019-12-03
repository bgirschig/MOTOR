// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import App from './App';
import * as router from './router';
import VueSnackbar from 'vue-snack';
import {firebase} from './firebase';

Vue.config.productionTip = false;
Vue.use(VueSnackbar, {close: true});

firebase.auth().onAuthStateChanged(()=> {
  router.initGuards();
  /* eslint-disable no-new */
  new Vue({
    el: '#app',
    router: router.default,
    components: {App},
    template: '<App/>',
  });
});
