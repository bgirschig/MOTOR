<template>
  <div id="admin">

    <div class="sideBar">
      <nav>
        <router-link
          v-for="item in menu"
          :key="item.target"
          :to=item.target>{{item.title}}</router-link>
      </nav>
    </div>

    <router-view class="viewContainer"/>

    <button class="logoutBtn" @click="logout" v-if="$route.name!=='login'">
      log out
    </button>
  </div>
</template>

<script>
import {firebase} from '@/firebase';

export default {
  name: 'AdminView',
  data() {
    return {
      menu: [
        {title: 'spreadsheets', target: '/admin/spreadsheets'},
        {title: 'forms', target: '/admin/forms'},
        {title: 'templates', target: '/admin/templates'},
      ],
    };
  },
  methods: {
    logout() {
      firebase.auth().signOut();
    },
  },
};
</script>

<style>
#admin {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;

  --white: rgb(250, 250, 250);
  --light: rgb(218, 218, 218);
  --medium: rgb(98, 115, 167);
  --dark: rgb(47, 61, 104);

  background-color: var(--white);
  display: flex;
  width: 100%;
  height: 100%;

  overflow: hidden;
}
</style>

<style scoped>
.sideBar {
  background-color: var(--dark);
  color: var(--light);
  min-width: 200px;
}
nav {
  display: flex;
  flex-direction: column;
}
nav a {
  color: inherit;
  text-decoration: none;
  padding: 15px;
}
nav a:hover {
  background-color: var(--light);
  color: var(--dark);
}
.viewContainer {
  flex: 1 1;
}
.viewContainer.fullPage {
  position: absolute;
  width: 100%;
  height: 100%;
  background-color: var(--white);
}

.logoutBtn {
  position: fixed;
  top: 10px;
  right: 10px;
  z-index: 10;
  background-color: var(--dark);
  color: var(--white);
  padding: 8px 10px;
  text-transform: uppercase;
  font-weight: bold;
  /* border: 4px solid var(--dark); */
}
.logoutBtn:hover {
  background-color: var(--light);
  color: var(--dark);
  cursor: pointer;
}
</style>

