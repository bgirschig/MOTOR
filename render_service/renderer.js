// TODO: a more sensible approach to error handling: don't try to encode if
// render failed, don't try to upload if encode failed, etc...

const path = require("path");
const fs = require('fs-extra')
const fetch = require('node-fetch');
const ftp = require('basic-ftp');
const spawn = require('child_process').spawn;
const runEncoders = require('./encodersRunner');
const global_config = require("./config");
const logger = require('./logging');

// const RENDER_TEMPS_DIR = path.resolve('./render_tmps');
// const TEMPLATES_DIR = path.resolve('./templates');
// const DEFAULT_COMP_NAME = 'main';
// const REMOTE_OUTPUT_DIR = 'render_outputs'

// const isWin = process.platform === "win32";
// const aerender = isWin ? config.ae_render : config.ae_render_osx;

// let busy = false;

class Renderer {
    constructor(config={}) {
        config = Object.assign({
            "render_temps_dir": path.resolve('./render_tmps'),
            "templates_dir": path.resolve('./templates'),
            "default_comp_name": 'main',
            "remote_output_dir": 'render_outputs',
        }, config);
        this.config = config;
        
        let isWin = process.platform === "win32";
        this.aerender_cmd = isWin ? global_config.ae_render : global_config.ae_render_osx;
        
        this.busy = false;
    }

    async render(request, logger) {
        const renderProjectDir = path.join(this.config.render_temps_dir, request.id);
        const templateFilePath = path.join(renderProjectDir, 'template.aep');
        try {
            if(this.busy) {
                logger.warn('rejected render: the renderer was busy');
                return;
            }
            this.busy = true;
            this.logger = logger;

            let outputDir = await this.prepareRender(request, renderProjectDir);
            let losslessFile = path.join(outputDir, 'lossless');
            let compName = request.compName || this.config.default_comp_name;
            
            await this.ae_render(templateFilePath, losslessFile, compName);
            this.logger.info('ae_render finished');
            
            // find the lossless file (after effects replaces the extension
            // depending on the environment, so we can't know)
            let losslessFiles = await findFiles(outputDir, 'lossless');
            if (losslessFiles.length === 0) throw new Error('rendered file not found');
            if (losslessFiles.length > 1) throw new Error('more than one rendered file found');
            losslessFile = losslessFiles[0];
    
            await runEncoders(losslessFile, request.encoders, this.logger);
            await fs.remove(losslessFile);
            let realCount = await cout_files(outputDir);
            let expectedCount = request.encoders.length;
            if (realCount != expectedCount){
                throw new Error(`Expected ${expectedCount}, found ${realCount} encoded files`);
            }
            await this.upload_renders(outputDir, request.id);
            
            this.logger.info('cleanup');
            await fs.remove(renderProjectDir);
            
            this.logger.info('done');
            this.busy = false;
        } catch (err) {
            this.logger.info('cleanup after error: ', err.message);
            await fs.remove(renderProjectDir);
            
            this.busy = false;
            throw err;
        }
    }

    async ae_render(templateFilePath, losslessFile, compName) {
        let args = [
            '-project', templateFilePath,
            '-comp', compName,
            '-output', losslessFile,
            '-continueOnMissingFootage',
        ];
    
        this.logger.info({
            command:{
                'command-path': this.aerender_cmd,
                'args': args,
            }
        }, `spawn process: ${this.aerender_cmd + args.join(' ')}`);
    
        // TODO: add a timeout
        // TODO: bundle multiple stdout lines together before sending, or only
        // debug-log them
        var ae = spawn(this.aerender_cmd, args);
        ae.stdin.end();
        ae.on('error', (err) => {
            this.logger.error(err, String(err));
        });
        ae.stdout.on('data', data => {
            this.logger.info('stdout: ' + data.toString().trim());
        })
        ae.stderr.on('data', (data) => {
            this.logger.error('stderr:', data.toString());
        });
        return new Promise((resolve, reject)=>{
            ae.on('close', function (code) {
                if (code == 0) resolve();
                else reject('aerender command failed');
            });
        })
    }

    /**
     * Prepares the render "environment" for a given request: downloads or copies
     * all the ressources needed for a render according to the request.
     * @param {renderRequest} request - the object that defines the request
     */
    async prepareRender (request, renderProjectDir) {
        this.logger.info('prepare render');

        let promises = [];

        // Define some paths
        const templateSourceDir = path.join(this.config.templates_dir, request.template);
        // no extension: aerender selects it depending on output module
        const outputDir = path.join(renderProjectDir, 'output');

        // Create folders
        promises.push(fs.ensureDir(this.config.render_temps_dir));
        promises.push(fs.ensureDir(renderProjectDir));
        promises.push(fs.ensureDir(outputDir));

        await Promise.all(promises);
        promises = [];

        // Copy template files
        await fs.copy(templateSourceDir, renderProjectDir);

        // get every resource in the render dir
        for (let ressourceItem of request.resources) {
            const filePath = path.join(renderProjectDir, ressourceItem.target);

            if ('data' in ressourceItem) {
                let data;
                if(typeof ressourceItem.data == 'object') {
                    // Here, we need a trick to avoid after effects's usesless, yet
                    // blocking popup: 'the structure of the data file has changed'.
                    // New keys can't be added, even the order of the keys needs to
                    // be respected.
                    // For that, we load the data file that was saved with the
                    // template (so it must have the expected 'structure') and
                    // replace the values with the request's when they match.
                    // This technique prevents unknown keys from being added and
                    // also preserves the original order.
                    // TODO: Make this more generic (eg. as-is, it
                    // wouldn't work with downloaded ressouces)
                    let templatecontent;
                    let objectdata = {};
                    if (await fs.exists(filePath)) {
                        templatecontent = await fs.readFile(filePath);
                        objectdata = JSON.parse(templatecontent.toString('utf8'));
                    }
                    for (let key in objectdata) {
                        if (key in ressourceItem.data){
                            objectdata[key] = ressourceItem.data[key];
                        }
                    }
                    data = JSON.stringify(objectdata);
                } else if (typeof ressourceItem.data == 'string') {
                    data = ressourceItem.data;
                }
                fs.outputFile(filePath, data);
            } else if ('src' in ressourceItem) {
                promises.push(fetchResource(ressourceItem.src, filePath));
            }
        }
        await Promise.all(promises);

        return outputDir;
    }

    async upload_renders(outputDir, target) {
        const client = new ftp.Client();
        try {
            await client.access(global_config.ftp);
            await client.cd(this.config.remote_output_dir);
            await client.uploadDir(outputDir, target);
            this.logger.info('upload successful');
            client.close();
        } catch(err) {
            client.close();
            throw new Error('upload failed' + err)
        }
    }
}

async function cout_files(dir) {
    return fs.readdir(dir).then((files)=>{
        return files.length;
    })
}

/**
 * Returns all the files whose name mathes the given one (equivalent of <dir>/<name>.*)
 * @param {string} name The name of the file(s) to match, without extension
 */
async function findFiles(dir, name) {
    let files = await fs.readdir(dir);
    matched = files.filter(file => path.parse(file).name === name);
    matched = matched.map(file=>path.join(dir, file));
    return matched;
}

async function fetchResource(urls, targetPath) {
    if(Array.isArray(urls)) {
        promises = urls.map((url, idx)=>{
            let targetPathIndexed = targetPath.replace('#', idx);
            return fetchResource(url, targetPathIndexed)
        });
        return Promise.all(promises)
    } else {
        let url = urls;

        await fs.ensureFile(targetPath)
        response = await fetch(url);
        if (response.status !== 200) {
            throw new Error('failed asset request: ' + url);
        } else {
            const file = fs.createWriteStream(targetPath);
            let promise = new Promise((resolve, reject)=>{
                response.body.pipe(file);
                response.body.on('end', resolve);
                response.body.on('error', reject);
            })
            await promise;
            file.close();
        }
    }
}

module.exports = Renderer;
