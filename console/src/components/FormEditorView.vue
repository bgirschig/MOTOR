<template>
  <div class="FormEditorView">
    <div class="formsList">
      <h2>Forms</h2>
      <router-link
        v-for="formName in forms"
        :key="formName"
        :to="{params: { name: formName }}">{{formName}}</router-link>
    </div>
    <div ref="editor" id="editor" v-show="showEditor"></div>
    <div v-show="!showEditor">
      Please select a form in the list, or create a new one
    </div>
  </div>
</template>

<script>
import * as monaco from 'monaco-editor/esm/vs/editor/editor.api';
import {getForm, listForms, saveForm} from '../formClient';

export default {
  name: 'FormEditorView',
  data() {
    return {
      editor: null,
      showEditor: true,
      forms: [],
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
      try {
        await saveForm(this.$route.params.name, this.editor.getValue());
        this.$snack.success('saved!');
      } catch (error) {
        // TODO: give a more explicit message
        this.$snack.danger('could not save.');
      }
    },
    async load() {
      const formsList = await listForms();
      this.forms = formsList;
      this.$set(this, 'forms', formsList);

      const formName = this.$route.params.name;
      if (formName) {
        this.showEditor = true;
        let definition = await getForm(formName, 'text');
        if (!definition) definition = '# New form definition: '+formName;
        this.editor.setValue(definition);
      } else {
        this.showEditor = false;
      }
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .FormEditorView {
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
