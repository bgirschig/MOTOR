/**
 * Promise generators and helpers
 * @module promises
 * @example
 * import { seconds } from 'jsUtils/promises'
 * async function main() {
 *  console.log('before');
 *  await seconds(3);
 *  console.log('after');
 * }
 */

/**
 * Pauses the promise chain for 'duration' seconds (passes data through,
 * unchanged)
 * @example
 * fetch('www.something.com')
 *  .then(pauseChainFor(2))
 *  .then(console.log)
 * @param {int} seconds how long to wait for
 * @return {function(): Promise<*>}
 */
export function pauseChainFor(seconds) {
  const func = function(data) {
    return new Promise((resolve, _reject)=>{
      setTimeout(()=>resolve(data), seconds * 1000);
    });
  };
  return func;
}

/**
 * Wait for x seconds
 * @param {*} count Number of seconds to wait for before yielding
 * @return {Promise<void>} A promise that resolves after a number of seconds
 */
export function seconds(count) {
  return millis(count*1000);
}

/**
 * Wait for x milliseconds
 * @param {*} count Number of millis to wait for before yielding
 * @return {Promise<void>} a promise that resolves after a number of millis
 */
export function millis(count) {
  return new Promise((resolve) => setTimeout(resolve, count));
}

/**
 * Pauses the promise chain for a single animation frame
 * @return {Promise}
 */
export function frame() {
  return new Promise((resolve) => requestAnimationFrame(resolve));
}

/**
 * Logs something from within a promise chain, then yields the payload, unchanged
 * @param {String} message
 * @return {function}
 */
export function log(message) {
  return (payload) => {
    console.log(message);
    return payload;
  };
}
