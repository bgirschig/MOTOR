const path = require("path");
const express = require("express");
const fs = require('fs-extra')
const fetch = require('node-fetch');
var spawn = require('child_process').spawn;

const RENDER_TEMPS_DIR = path.resolve('./render_tmps');
const TEMPLATES_DIR = path.resolve('./templates');
const AERENDER_PATH = '/Applications/Adobe\ After\ Effects\ CC\ 2018/aerender';
const DEFAULT_COMP_NAME = 'main';

const renderRequest = {
    template: "boat",
    compName: "main",
    id: "5789145",
    resources: [
        // {target: "img.png", source: "http://images.math.cnrs.fr/IMG/png/section8-image.png"},
        {target: "img.png", source: "https://via.placeholder.com/350x150/FF7700/FFFFFF?text================="},
        {target: "data.json", data: {
            truc: "yamero !",
        }},
    ],
}

function render (request) {
    let {templateFilePath, outputFilePath, compName} = prepareRender(request);
    let errors = []

    var ae = spawn(AERENDER_PATH, [
        '-project', templateFilePath,
        '-comp', compName,
        '-output', outputFilePath,
    ]);
    ae.on('error', function (err) {
        errors.push(err);
    });
    ae.stdout.on('data', data => {
        console.log('stdout: ' + data);
    })
    ae.stderr.on('data', function (data) {
        errors.push(data);
    });
    return new Promise((resolve, reject)=>{
        ae.on('close', function (code) {
            if (code == 0) {
                resolve();
            } else {
                let errorsMessage = errors.map(err=>err.message).join("\n  ");
                reject({
                    message: 'aerender command failed:\n  '+errorsMessage,
                    errors: errors,
                });
            }
        });
    })

    // convert
    // upload
}

/**
 * Prepares the render "environment" for a given request: downloads or copies
 * all the ressources needed for a render according to the request.
 * @param {renderRequest} request - the object that defines the request
 */
function prepareRender (request) {
    // TODO: make this whole function asynchronous

    // Define some paths
    const renderDir = path.join(RENDER_TEMPS_DIR, request.id);
    const resourcesPath = path.join(renderDir, "(Metrage)");
    const templateSourceDir = path.join(TEMPLATES_DIR, request.template);
    // no extension: aerender selects it depending on output module
    const outputFilePath = path.join(renderDir, 'output');
    const templateFilePath = path.join(renderDir, 'template.aepx');

    // Create folders
    if (!fs.existsSync(RENDER_TEMPS_DIR)) fs.mkdirSync(RENDER_TEMPS_DIR);
    if (!fs.existsSync(renderDir)) fs.mkdirSync(renderDir);
    if (!fs.existsSync(resourcesPath)) fs.mkdirSync(resourcesPath);

    // Copy template files
    fs.copySync(templateSourceDir, renderDir);

    // Define some variables
    const compName = request.compName || DEFAULT_COMP_NAME;

    // get every resource in the render dir
    for (let ressourceItem of request.resources) {
        const filePath = path.join(resourcesPath, ressourceItem.target);
        const file = fs.createWriteStream(filePath);
        
        if ('data' in ressourceItem) {
            let data;
            if(typeof ressourceItem.data == 'object') {
                data = JSON.stringify(ressourceItem.data);
            } else if (typeof ressourceItem.data == 'string') {
                data = ressourceItem.data;
            }
            file.write(data);
        } else if ('source' in ressourceItem) {
            fetch(ressourceItem.source)
            .then(resp=>resp.body.pipe(file))
            .catch(console.error);
        }
    }

    return {templateFilePath, outputFilePath, compName}
}

render(renderRequest)
.then(()=>console.log('yay'))
.catch(e=>console.log(e.message));