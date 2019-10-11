<!-- The end user's product: renders the form he can use to request a video -->

<template>
  <div class="rootForm">
    <div class='FormView'>
      <div class='container'>
        <header>
          <span>Motor</span>
          <span>{{title}}</span>
        </header>
        <form ref='form'>
          <fieldset :disabled="disabled">
            <component
              :is="'custom'+field.type"
              v-for="field in fields"
              v-bind:key="field.name"
              :config="field"
            ></component>
          </fieldset>
          <div class='previewroot'>
            <img v-if="preview" :src="preview" alt="output example" />
            <div v-if="!disabled" class='submit' @click="submit" tabindex='0'>
              send
            </div>
          </div>
        </form>
      </div>

      <div class='message' v-if="currentMessage" @click="currentMessage=null">
        <div class='popup'>
          <div class='content'>{{currentMessage}}</div>
          <button @click="currentMessage=null">close</button>
        </div>
      </div>
    </div>
    <footer>
      <a class="beforelogout" href='https://kairos-studio.world/' target='_blank'>Kairos studio, Visual Affairs</a>
      <span class='logout' @click="logout">
        {{currentUser}} logout
      </span>
    </footer>
  </div>
</template>

<script>
import * as formsClient from '../formClient';
import customtextfield from './fields/customtextfield';
import customtextarea from './fields/customtextarea';
import customfiles from './fields/customfiles';
import customradio from './fields/customradio';
import customcheckbox from './fields/customcheckbox';
import customtime from './fields/customtime';
import {firebase} from '@/firebase';

export default {
  name: 'FormView',
  components: {
    customtextfield: customtextfield,
    customtextarea: customtextarea,
    customfiles: customfiles,
    customradio: customradio,
    customcheckbox: customcheckbox,
    customtime: customtime,
  },
  data() {
    return {
      title: '',
      logo: '',
      preview: '',
      fields: [],
      messages: {
        sending: 'Sending your request...',
        success: 'success!',
        error: 'Sorry. An error has occured. Please try again later',
      },
      currentMessage: null,
      disabled: false,
      currentUser: null,
    };
  },
  async mounted() {
    this.firebaseUnsub = firebase.auth().onAuthStateChanged((user)=>{
      this.currentUser = user.email;
    });
    const definition = await formsClient.getForm(
        this.$route.params.id, 'json', true);
    this.preview = definition.previewImage;
    this.fields = definition.fields;
    this.title = definition.title;
    this.logo = definition.logo;
    this.messages.success = definition.formSuccessMessage || 'success!';
  },
  methods: {
    async submit() {
      const isValid = this.$refs.form.reportValidity();
      if (!isValid) return;
      const formdata = new FormData(this.$refs.form);
      this.disabled = true;
      const success = await formsClient.submit(this.$route.params.id, formdata);
      this.disabled = false;
      if (success) {
        this.currentMessage = this.messages.success;
        this.$refs.form.reset();
      } else {
        this.currentMessage = this.messages.error;
      }
    },
    logout() {
      firebase.auth().signOut();
    },
  },
  beforeDestroy() {
    this.firebaseUnsub();
  },
};
</script>

<style scoped>
.rootForm{
  background-color: black;
}
.FormView {
  display: flex;
  justify-content: center;
  width: 100%;
  min-height: 100%;
  background-color: black;
  color: black;
  box-sizing: border-box;
  font-size: 100%;
  font-size: 100%;
}
.container {
  width: 100%;
  /* max-width: 500px; */
  background-color: black;
}
header {
  font-family: 'myFont';
  font-size: 18px;
  background-color: white;
  box-sizing: border-box;
  width: 100%;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid black;
}

.container >>> label {
  display: block;
}
.container >>> h3 {
  font-size: inherit;
  text-transform: capitalize;
  margin-bottom: 1px;
  margin-top: 12px;
  font-weight: bold;
}
.container >>> h3::before,
.container >>> label:focus-within h3::before,
img {
  width: 100%;
  max-width: 450px;
  display: flex;
  margin: auto;
}

.container >>> label:hover h3::before,
.container >>> input {
  background-color: transparent;
  border: none;
  border-bottom: solid 1px black;
  width: 100%;
  padding-bottom: 5px;
  box-sizing: border-box;
  outline: none;
  color: gray;
}
.container >>> textarea {
  background-color: transparent;
  border: solid 1px white;
  width: 100%;
  padding: 5px;
  box-sizing: border-box;
  resize: vertical;
  outline: none;
  color: white;
}
.container >>> .option_other input {
  width: calc(100% - 23px);
}
.container >>> input[type='radio'] {
  width: auto;
}
.container >>> input[type='file'] {
  opacity: 0;
  width: 1px;
  height: 1px;
  overflow: hidden;
  position: absolute;
  z-index: -1;
}
.submit {
  font-family: 'MyFont';
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background-color: white;
  color: black;
  margin-left: 0;
  padding: 0;
  outline: none;
  text-transform: capitalize;
  width: 100px;
  height: 50px;
  font-size: 15px;
  margin: 80px auto 30px auto;
  border-radius: 25px;
}

fieldset {
  border: none;
  padding: 0px;
  background-color: white;
  margin: 0px;
}
a {
  color: inherit;
  text-decoration: none;
}

.message {
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  background-color: rgba(0, 0, 0, 0.5);
}
.popup {
  color: white;
  position: fixed;
  top: 50%;
  left: 50%;
  width: 400px;
  max-width: calc(100% - 20px);
  box-sizing: border-box;
  transform: translate(-50%, -50%);
  background-color: black;
  padding: 15px;
  border: 1px solid white;
}
.popup .content {
  margin-bottom: 30px;
  white-space: pre-wrap;
}
.popup button {
  background-color: transparent;
  color: white;
  font: inherit;
  border: none;
  position: absolute;
  bottom: 10px;
  left: 10px;
  cursor: pointer;
}
.logout {
  cursor: pointer;
  position: relative;
}
.logout::before {
  content: attr(data-label);
  position: absolute;
  right: 55px;
}

footer {
  padding: 30px;
  box-sizing: border-box;
  width: 100%;
  display: flex;
  justify-content: space-between;
  position: relative;
  bottom: 0;
  left: 0;
  background-color: black;
  color: white;
}

@media screen and (max-width : 600px) {
  footer {
    padding: 30px;
    box-sizing: border-box;
    width: 100%;
    display: flex;
    justify-content: space-between;
    position: relative;
    bottom: 0;
    left: 0;
    background-color: black;
    color: white;
    display: inline-grid;
    justify-content: center;
  }
}
</style>
