// This script is automatically run after npm install.

'use strict';
const fs = require('fs-extra');
fs.createReadStream('.env-template').pipe(fs.createWriteStream('.env'));