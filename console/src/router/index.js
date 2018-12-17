import Vue from 'vue';
import Router from 'vue-router';
import SpreadsheetsView from '@/components/SpreadsheetsView';
import FormsView from '@/components/FormsView';
import TemplatesView from '@/components/TemplatesView';
// import SpreadsheetsView from '@/components/SpreadsheetsView';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/spreadsheets',
      component: SpreadsheetsView,
      // addToMenu: true,
    },
    {
      path: '/forms',
      component: FormsView,
      addToMenu: true,
    },
    {
      path: '/templates',
      component: TemplatesView,
      addToMenu: true,
    },
  ],
});
