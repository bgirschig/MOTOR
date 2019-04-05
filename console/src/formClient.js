import {firebase} from './firebase';
import * as yaml from 'js-yaml';

// const serverUrl = 'http://localhost:8082';
const serverUrl = 'https://forms-dot-kairos-motor.appspot.com';
const apiurl = `${serverUrl}/api`;

/**
 * Thin wrapper around the fetch function to make authenticated requests.
 * This simply adds the custom X-firebase-auth, that can then be checked server
 * side with firebase, to get the current user's identity
 * @param {String} url - url of the ressource to fetch
 * @param {Object} options - options for the request
 * @return {Promise<Response>} the response
 */
export async function authFetch(url, options) {
  const token = await firebase.auth().currentUser.getIdToken();
  options = Object.assign({
    headers: {
      'X-firebase-auth': token,
    },
  }, options);
  return fetch(url, options);
}

/**
 * retrieves a form definition
 * @param {string} id - id of the form.
 * @param {string} format - output format: text or json
 * @return {Promise<Object>} form definition
 */
export async function getForm(id, format='json') {
  const response = await authFetch(`${apiurl}/definition/${id}`);

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
  const response = await authFetch(`${apiurl}/definitions`);
  return await response.json();
}

/**
 * Updates a form definition
 * @param {string} id - id for the form
 * @param {string} content - the content of the form definition to be saved
 */
export async function saveForm(id, content) {
  const url = `${apiurl}/definition/${id}`;
  const response = await authFetch(url, {
    method: 'PUT',
    body: content,
  });
  if (!response.ok) throw new Error('could not save file');
}

/**
 * returns the signed url for a rendered form
 * @param {string} id - id of the form
 * @return {string} the signed url of the form
 */
export async function getFormUrl(id) {
  if (!id) return null;
  const token = await firebase.auth().currentUser.getIdToken();
  return `${serverUrl}/${id}?auth=${token}`;
}

/**
 * Submits formdata to the appropriate route, for processing.
 * @param {string} id - the id of the form
 * @param {FormData} data - the data of the form
 * @return {boolean} true if the submit was successful, false otherwise
 */
export async function submit(id, data) {
  data.append('form_definition', id);

  const url = `${serverUrl}/response`;
  const reponse = await authFetch(url, {
    method: 'POST',
    body: data,
  });
  return reponse.ok;
}

/** Thrown when a ressource is not found */
export class NotFound extends Error {}
