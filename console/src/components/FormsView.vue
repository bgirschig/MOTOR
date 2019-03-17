<template>
  <div class="formsView">
    <div class="formsList">
      <h2>Forms</h2>
      <div>form 1</div>
      <div>form 2</div>
      <div>form 3</div>
    </div>
    <div ref="editor" id="editor">
    </div>
  </div>
</template>

<script>
import * as monaco from 'monaco-editor/esm/vs/editor/editor.api';

export default {
  name: 'FormsView',
  data() {
    return {
      editor: null,
    };
  },
  async mounted() {
    let definition = await fetch('http://localhost:8081/api/definitions/truc', {credentials: 'include'});
    definition = await definition.json();

    this.editor = monaco.editor.create(this.$refs.editor, {
      value: definition.content,
      language: 'yaml',
    });

    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S, ()=>{
      this.save();
    });
  },
  methods: {
    async save() {
      const response = await fetch('http://localhost:8081/api/definitions/truc', {
        credentials: 'include',
        method: 'PUT',
        body: this.editor.getValue()});
      if (response.ok) this.$snack.success('saved!');
      else this.$snack.danger('could not save.'); // TODO: give a reason why
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
    padding: 10px 20px;
    box-sizing: border-box;
    background-color: var(--light);
    color: var(--dark);
  }
  h2 {
    margin-top: 0;
  }
  #editor {
    width: 100%;
    height: 100%;
  }
</style>
