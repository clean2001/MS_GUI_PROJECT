'use strict'

const { app, BrowserWindow, Menu, dialog, shell } = require('electron');
const path = require('path');
const spawn = require('child_process').spawn; // python code 실행을 위한

require('electron-reload')(__dirname+`\\spectrums\\spectrum_naive0.html`);
// console.log(__dirname+`\\spectrums\\`)


const isDev = require('electron-is-dev');
const remote = require('@electron/remote/main');


let mainWindow = null;
let is_index = false;
let tolerance = 0.5;
let currentFiles; // 현재 열려있는 파일

remote.initialize()

// var _path = app.getAppPath()


// dialog
const options = {
  // type: 'question',
  buttons: ['OK'],
  defaultId: 2,
  title: '😊',
  message: '준비중입니다.',
};

const equal_tol = {
  buttons: ['OK'],
  defaultId: 3,
  title: '😊',
  message: '현재 tolerance와 같습니다.',
};

const open_file_first = {
  buttons: ['OK'],
  defaultId: 4,
  title: '😊',
  message: '파일을 먼저 열어주세요!',
};


//


// menu bar
const template = [
  {
    label: "File",
    submenu: [
      {
        label: "File Open",
        click: async function () {
          const selectWindow = new BrowserWindow({
            show: false,
            alwaysOnTop: true
          });

          const { filePaths } = await dialog.showOpenDialog(selectWindow, {
            properties: ["openFile"]
          });

          selectWindow.close();
          // console.log(filePaths);

          if(filePaths.length > 0) {
            currentFiles = filePaths;
            const result = spawn('python', ['process_data.py', filePaths, tolerance]);
            result.stdout.on('data', function (data) {
              // console.log("done!");
              let testData = JSON.parse(JSON.stringify("spectrums.json"));
              console.log(testData);
              mainWindow.loadURL(`file://${app.getAppPath()}/index.html`);
              is_index = true;
            });
            
            mainWindow.loadURL(`file://${app.getAppPath()}/loading.html`)
          }
  
        }

      },
      {
        label: "Save Image as JPG",
        click: function () {
          dialog.showMessageBoxSync(null, options);
        }
      }
    ]
  },
  {
    label: "Window",
    submenu: [
      {
        label: "Reload Window",
        click: function () {
          if(is_index) {
            mainWindow.loadURL(`file://${app.getAppPath()}/index.html`);
          } else {
            mainWindow.loadURL(`file://${app.getAppPath()}/prologue.html`);
          }
        }

      },
      {
        label: "Reset GUI",
        click: function () {
            is_index = false;
            mainWindow.loadURL(`file://${app.getAppPath()}/prologue.html`);
        }

      }

    ]
  },

  {
    label: "Tolerance",
    submenu: [
      {
        label: tolerance === 0.5 ? "0.5 ✅" : "0.5",
        click: function () {
          if(!is_index) {
            dialog.showMessageBoxSync(null, open_file_first);
          } else if(tolerance === 0.5) { // 이미 0.5입니다. 
            dialog.showMessageBoxSync(null, equal_tol);
          } else {

            tolerance = 0.5
            const result = spawn('python', ['process_data.py', currentFiles, tolerance]);
            result.stdout.on('data', function (data) {
              let testData = JSON.parse(JSON.stringify("spectrums.json"));
              is_index = true;
            });

            result.stderr.on('data', function (data) {
              console.log("err!");
            });

            mainWindow.loadURL(`file://${app.getAppPath()}/loading.html`);
          }

        }
      },
      {
        label: tolerance === 0.05 ? "0.05 ✅" : "0.05",
        click: function() {
          if(!is_index) {
            dialog.showMessageBoxSync(null, open_file_first);
          } else if(tolerance === 0.05) { // 이미 0.05입니다. 
            dialog.showMessageBoxSync(null, equal_tol);
          } else {

            tolerance = 0.05
            const result = spawn('python', ['process_data.py', currentFiles, tolerance]);
            result.stdout.on('data', function (data) {
              let testData = JSON.parse(JSON.stringify("spectrums.json"));
              is_index = true;
            });

            result.stderr.on('data', function (data) {
              console.log("err!");
            });

            mainWindow.loadURL(`file://${app.getAppPath()}/loading.html`);
          }

        }
      }
    ]
  },
  {
    label: "Help",
    submenu: [
      {
        label: "Documentation",
        click: function () {
          let document_window = new BrowserWindow({width: 800, height: 600})
          document_window.on('closed', () => {
            document_window = null
          })
          document_window.loadURL(`file://${app.getAppPath()}/document.html`);
        }
      },
      {
        label: "Github",
        click: function () {
          let github_window = new BrowserWindow({width: 800, height: 600})
          github_window.on('closed', () => {
            github_window = null
          })
          github_window.loadURL(`https://github.com/clean2001/MS_GUI_PROJECT`);
        }

      }

    ]
  }
];

const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);

//


app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();

});

app.on('ready', () => {
  mainWindow = new BrowserWindow({
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    }

    });

  mainWindow.webContents.openDevTools();
  mainWindow.loadURL(`file://${app.getAppPath()}/prologue.html`);
  is_index = false;



  mainWindow.on('closed', () => { mainWindow = null; });

});
