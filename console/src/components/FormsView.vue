<template>
  <div class="formsView">
    <div class="formsList">
      <h2>Forms</h2>
      <router-link :to="{params: { name: 'truc' }}">truc</router-link>
      <router-link :to="{params: { name: 'machin' }}">machin</router-link>
    </div>
    <div ref="editor" id="editor" v-show="showEditor"></div>
    <div v-show="!showEditor">
      Please select a form in the list, or create a new one
    </div>
  </div>
</template>

<script>
import * as monaco from 'monaco-editor/esm/vs/editor/editor.api';

const formsApiUrl = 'https://forms-dot-kairos-motor.appspot.com/api';

export default {
  name: 'FormsView',
  data() {
    return {
      editor: null,
      showEditor: true,
    };
  },
  watch: {
    async $route(to, from) {
      this.load();
    },
  },
  mounted() {
    this.editor = monaco.editor.create(this.$refs.editor, {
      language: 'yaml',
    });
    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S, ()=>{
      this.save();
    });
    this.load();
  },
  methods: {
    async save() {
      const url = formsApiUrl+'/definitions/'+this.$route.params.name;
      const response = await fetch(url, {
        credentials: 'include',
        method: 'PUT',
        body: this.editor.getValue(),
      });
      if (response.ok) this.$snack.success('saved!');
      else this.$snack.danger('could not save.'); // TODO: give a reason why
    },
    async load() {
      if (this.$route.params.name) {
        this.showEditor = true;

        const url = formsApiUrl+'/definitions/'+this.$route.params.name;
        const response = await fetch(url, {credentials: 'include'});
        if (response.ok) {
          // load up the contents of the file
          const definition = await response.json();
          this.editor.setValue(definition.content);
        } else if (response.status === 404) {
          // if the file was not found, create one
          const contents = '# New form definition: '+this.$route.params.name;
          this.editor.setValue(contents);
        }
      } else {
        this.showEditor = false;
      }
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .formsView {
    height: 100%;
    display: flex;
  }
  .formsList {
    width: 200px;
    height: 100%;
    padding: 10px 0;
    box-sizing: border-box;
    background-color: var(--light);
    color: var(--dark);
  }
  .formsList a {
    display: block;
    padding: 10px 20px;
    text-decoration: none;
    color: inherit;
  }
  .formsList a.router-link-exact-active {
    background-color: var(--dark);
    color: var(--light);
  }
  h2 {
    padding: 0 20px;
    margin-top: 0;
  }
  #editor {
    width: 100%;
    height: 100%;
  }
</style>
