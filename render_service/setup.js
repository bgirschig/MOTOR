// This script is automatically run after npm install.
'use strict';

const fs = require('fs-extra');
var Service = require('node-windows').Service;

// create env file
fs.createReadStream('.env-template').pipe(fs.createWriteStream('.env'));

// Create a new service object
var svc = new Service({
  name:'MOTOR render node',
  description: 'the render node client for the MOTOR render farm',
  script: 'C:\\Users\\bgirschig\\Desktop\\rendernode\\index.js'
});
// Listen for the "install" event, which indicates the process is available as a
// service.
svc.on('install',function(){
  svc.start();
});

svc.install();