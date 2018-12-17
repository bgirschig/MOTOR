<template>
  <div id="app">
    <div class="navContainer">
      <nav>
          <router-link
            v-for="item in menu"
            :key="item.target"
            :to=item.target>{{item.title}}</router-link>
      </nav>
    </div>
    <div class="viewContainer">
      <router-view/>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      menu: [
        {title: 'spreadsheets', target: 'spreadsheets'},
        {title: 'forms', target: 'forms'},
        {title: 'templates', target: 'templates'},
      ],
    };
  },
};
</script>

<style>

html, body {
  width: 100%;
  height: 100%;
  margin: 0;
}
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;

  --light: rgb(218, 218, 218);
  --dark: rgb(14, 22, 49);

  display: flex;
  width: 100%;
  height: 100%;
}

.marginBox {
  margin: 20px;
}
.navContainer {
  background-color: var(--dark);
  color: var(--light);
  overflow-y: scroll;
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
  overflow-y: scroll;
  padding: 15px;
}
</style>
