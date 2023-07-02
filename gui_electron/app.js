const spawn = require('child_process').spawn; // python code 실행을 위한
const user = require('./user');

let filename = 'basic.html';

async function asyncCallDoubleReject() {
    try{
        const result = await promiseFunction();
    } catch (e) {
        console.error(e);
    }
}

function bindWindow() {
    if(!document) {
        document = window.document;
    }
}

async function insertMsg() {
    console.log("hehe");
    user.bindDocument(window);
    
    let graphWindow = document.querySelector(".graph-window");
    // console.log(graphWindow);
    let template = document.querySelector('.item-template');
    // console.log(template);
    let clone = document.importNode(template.content, true);
    // console.log(clone);

    console.log(clone.querySelector('.graph-template'));
    // clone.querySelector('.graph-template').innerHTML = `<iframe src='./spectrums/spectrum_nterm.html'/>`; // 이거 됨!
    // graphWindow.innerHtml = '<p>hihi</p>';
    // graphWindow.appendChild(clone);
    

    //
    let tmp = document.querySelector('#graph-iframe');
    tmp.src = './spectrums/spectrum_cterm.html';

  
}

module.exports = {filename, insertMsg};
