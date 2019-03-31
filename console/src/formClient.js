import {firebase} from './firebase';

const apiurl = 'http://localhost:8082/api';
// const apiurl = 'https://forms-dot-kairos-motor.appspot.com/api';

/**
 * retrieves a form definition
 * @param {string} id - id of the form.
 */
export async function getForm(id) {
  const token = await firebase.auth().currentUser.getIdToken();
  fetch(`${apiurl}/definition/${id}?auth=${token}`)
      .then((r)=>r.json())
      .then(console.log);
}
