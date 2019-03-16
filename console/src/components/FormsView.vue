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
  mounted() {
    monaco.editor.create(this.$refs.editor, {
      value: '# empty definition',
      language: 'yaml',
    });
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
