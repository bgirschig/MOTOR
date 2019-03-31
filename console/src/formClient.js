import {firebase} from './firebase';
import * as yaml from 'js-yaml';

const apiurl = 'http://localhost:8082/api';
// const apiurl = 'https://forms-dot-kairos-motor.appspot.com/api';

/**
 * retrieves a form definition
 * @param {string} id - id of the form.
 * @param {string} format - output format: text or json
 * @return {Promise<Object>} form definition
 */
export async function getForm(id, format='json') {
  const token = await firebase.auth().currentUser.getIdToken();
  const response = await fetch(`${apiurl}/definition/${id}?auth=${token}`);

  if (response.status === 404) {
    return null;
  } else if (!response.ok) {
    throw new Error(`An error occured while retrieving form '${id}'`);
  }
  const doc = await response.json();
  if (format==='json') return yaml.safeLoad(doc.content);
  else if (format==='text') return doc.content;
  else throw new Error('unexpected format value: '+format.toString());
}

/**
 * Retrieves the list of all available form devinitions
 * @return {Promise<Array>}
 */
export async function listForms() {
  const token = await firebase.auth().currentUser.getIdToken();
  const response = await fetch(`${apiurl}/definitions?auth=${token}`);
  return await response.json();
}

/**
 * Updates a form definition
 * @param {string} id - id for the form
 * @param {string} content - the content of the form definition to be saved
 */
export async function saveForm(id, content) {
  const token = await firebase.auth().currentUser.getIdToken();
  const url = `${apiurl}/definition/${id}?auth=${token}`;
  const options = {
    method: 'PUT',
    body: content,
  };
  const response = await fetch(url, options);
  if (!response.ok) throw new Error('could not save file');
}

/** Thrown when a ressource is not found */
export class NotFound extends Error {}
