const express = require("express");
const renderer = require('./renderer');
const requestDefaults = require('./request_defaults');
const config = require("./config");
var bodyParser = require('body-parser');
var hash = require('object-hash');

const app = express();
app.use(bodyParser.json());

app.get('/test', (req, res) => {
    res.send('ok');
})

app.post('/render', (req, res) => {
    let request = {};
    Object.assign(request, requestDefaults);
    Object.assign(request, req.body);
    request.id = hash(JSON.stringify(req.body) + Date.now())

    renderer(request)
    .then(()=>console.log('request', request.id, 'done'));
    
    res.send(`http://motor.bastiengirschig.com/render_outputs/${request.id}`);
})

app.listen(config.apiPort, '0.0.0.0', () => {console.log(`listening on ${config.apiPort}!`)})