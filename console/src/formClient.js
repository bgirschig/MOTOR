import {firebase} from './firebase';

const apiurl = 'https://forms-dot-kairos-motor.appspot.com/api';

/**
 * retrieves a form definition
 * @param {string} id - id of the form.
 */
export async function getForm(id) {
  const token = await firebase.auth().currentUser.getIdToken();
  console.log(token);
  // fetch(`${apiurl}/${id}?auth=${token}`).then(console.log);
}
