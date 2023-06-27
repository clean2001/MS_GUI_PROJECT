'use strict'

const { app, BrowserWindow, Menu, dialog, shell} = require('electron');
const path = require('path');
const spawn = require('child_process').spawn; // python code 실행을 위한


const isDev = require('electron-is-dev');
const remote = require('@electron/remote/main');


let mainWindow = null;


remote.initialize()

// dialog
const options = {
    // type: 'question',
    buttons: ['OK'],
    defaultId: 2,
    title: '😊',
    message: '준비중입니다.',
};
//

// menu bar
const template = [
    { 
      label: "File",
      submenu: [
        {
            label: "File Open",
            click: async function(){
              const selectWindow = new BrowserWindow({
                show: false, 
                alwaysOnTop: true
              }); 
              
              const { filePaths } = await dialog.showOpenDialog(selectWindow, {
                properties: ["openFile"]
              });
              
              selectWindow.close();

              const result = spawn('python', ['process_data.py', filePaths]);
              result.stdout.on('data', function(data) {
              console.log(data.toString());
                });
              }
        },
        {
            label: "Save Image as JPG",
            click: function() { 
                dialog.showMessageBoxSync(null, options);
            }
        }
      ]
    },
    {
        label: "Setting",
      submenu: [
        {
            label: "Tolerance",
            click: function(){ 
              dialog.showMessageBoxSync(null, options);
            }

        }
      ]
    },
    {
      label: "Help",
      submenu: [
        {
            label: "Documentation",
            click: function(){ 
              dialog.showMessageBoxSync(null, options);
            }

        }
      ]
    }
];

const menu = Menu.buildFromTemplate(template); 
Menu.setApplicationMenu(menu);

//

 
function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            enableRemoteModule: true,
            contextIsolation: false
        }
    })
 
    win.loadURL(
        isDev
          ? 'http://localhost:3000'
          : `file://${path.join(__dirname, '../build/index.html')}`
      )
 
    remote.enable(win.webContents);
}
 
app.on('ready', createWindow)
 
app.on('window-all-closed', function() {
    if(process.platform !== 'darwin') {
        app.quit()
    }
})
 
app.on('activate', function() {
    if(BrowserWindow.getAllWindows().length === 0) createWindow()
})