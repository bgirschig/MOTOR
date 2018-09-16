const path = require("path");
const express = require("express");
const fs = require('fs-extra')
const fetch = require('node-fetch');
const FtpClient = require('ftp');
const ftp = require('basic-ftp');
var spawn = require('child_process').spawn;

const RENDER_TEMPS_DIR = path.resolve('./render_tmps');
const TEMPLATES_DIR = path.resolve('./templates');
const AERENDER_PATH = '/Applications/Adobe\ After\ Effects\ CC\ 2018/aerender';
const DEFAULT_COMP_NAME = 'main';

const renderRequest = {
    template: "boat",
    compName: "main",
    id: "5789147q",
    resources: [
        // {target: "img.png", source: "http://images.math.cnrs.fr/IMG/png/section8-image.png"},
        {target: "img.png", source: "https://via.placeholder.com/350x150/FF7700/FFFFFF?text================="},
        {target: "data.json", data: {
            truc: "yamero !",
        }},
    ],
}
const ftpConfig = {




}

function handle_request() {
    let {templateFilePath, outputDir, compName,
         renderProjectDir} = prepareRender(renderRequest);

    render(templateFilePath, outputDir, compName, renderProjectDir)
    .then(()=>upload(outputDir, renderRequest.id))
    .then(()=>fs.remove(renderProjectDir))
    .catch(e=>console.error(e));
}

async function upload (outputDir, target) {
    const client = new ftp.Client();
    try {
        await client.access(ftpConfig);
        await client.uploadDir(outputDir, target);
    } catch(err) {
        console.log(err);
    }
    client.close();
}

function render (templateFilePath, outputDir, compName) {
    let errors = []

    var ae = spawn(AERENDER_PATH, [
        '-project', templateFilePath,
        '-comp', compName,
        '-output', path.join(outputDir, 'lossless'),
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
}

/**
 * Prepares the render "environment" for a given request: downloads or copies
 * all the ressources needed for a render according to the request.
 * @param {renderRequest} request - the object that defines the request
 */
function prepareRender (request) {
    // TODO: make this whole function asynchronous

    // Define some paths
    const renderProjectDir = path.join(RENDER_TEMPS_DIR, request.id);
    const resourcesPath = path.join(renderProjectDir, "(Metrage)");
    const templateSourceDir = path.join(TEMPLATES_DIR, request.template);
    // no extension: aerender selects it depending on output module
    const outputDir = path.join(renderProjectDir, 'output');
    const templateFilePath = path.join(renderProjectDir, 'template.aepx');

    // Create folders
    if (!fs.existsSync(RENDER_TEMPS_DIR)) fs.mkdirSync(RENDER_TEMPS_DIR);
    if (!fs.existsSync(renderProjectDir)) fs.mkdirSync(renderProjectDir);
    if (!fs.existsSync(resourcesPath)) fs.mkdirSync(resourcesPath);
    if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);

    // Copy template files
    fs.copySync(templateSourceDir, renderProjectDir);

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

    return {templateFilePath, outputDir, compName, renderProjectDir}
}

init();