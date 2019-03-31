import Vue from 'vue';
import Router from 'vue-router';
import SpreadsheetsView from '@/components/SpreadsheetsView';
import FormEditorView from '@/components/FormEditorView';
import FormView from '@/components/FormView';
import LoginView from '@/components/LoginView';
import TemplatesView from '@/components/TemplatesView';
import AdminView from '@/components/AdminView';
import {firebase} from '@/firebase';

Vue.use(Router);

const router = new Router({
  routes: [
    {
      name: 'login',
      path: '/login',
      component: LoginView,
      meta: {
        public: true,
        fullPage: true,
      },
    },
    {
      name: 'form',
      path: '/form/:id?',
      component: FormView,
    },
    {
      name: 'admin',
      path: '/admin',
      component: AdminView,
      children: [
        {
          path: 'spreadsheets',
          component: SpreadsheetsView,
        },
        {
          path: 'forms/:name?',
          component: FormEditorView,
        },
        {
          path: 'templates',
          component: TemplatesView,
        },
      ],
    },
  ],
});

// when a user connects, redirect him to the page he originally asked for
// when one disconnects, redirect him to the login page
firebase.auth().onAuthStateChanged((user)=>{
  if (user && router.currentRoute.query.next) {
    router.push(router.currentRoute.query.next || '/');
  } else if (!user && router.currentRoute.name !== 'login') {
    router.push({name: 'login', query: {next: router.currentRoute.fullPath}});
  }
});

router.beforeEach((to, from, next) => {
  const user = firebase.auth().currentUser;
  if (!user && !to.meta.public) {
    next({name: 'login', query: {next: to.fullPath}});
  } else {
    next();
  }
});

// // Wait for the firebase auth init, then add a navigation guard: if the user
// // is not connected, redirect him to the login page
// const unsubscribe = firebase.auth().onAuthStateChanged(() => {
//   unsubscribe();
// });

export default router;
