const { app, BrowserWindow, Menu, shell, ipcMain, dialog } = require('electron');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development';
const { spawn } = require('child_process');
const fs = require('fs');

// Keep a global reference of the window object
let mainWindow;
let backendProcess;
let pythonBackendProcess;

// Prevent multiple instances
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
  app.quit();
} else {
  app.on('second-instance', () => {
    // Someone tried to run a second instance, focus our window instead
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'icon.png'),
    show: false,
    titleBarStyle: 'default',
    frame: true
  });

  // Load the app
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    // Open DevTools in development
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

function startBackends() {
  if (!isDev) {
    try {
      // Start Node.js backend
      const backendPath = path.join(process.resourcesPath, 'app', 'backend', 'server.js');
      if (fs.existsSync(backendPath)) {
        backendProcess = spawn('node', [backendPath], {
          cwd: path.dirname(backendPath),
          stdio: 'pipe'
        });

        backendProcess.stdout.on('data', (data) => {
          console.log(`Backend: ${data}`);
        });

        backendProcess.stderr.on('data', (data) => {
          console.error(`Backend Error: ${data}`);
        });
      }

      // Start Python backend
      const pythonBackendPath = path.join(process.resourcesPath, 'app', 'python-backend', 'app.py');
      if (fs.existsSync(pythonBackendPath)) {
        pythonBackendProcess = spawn('python', [pythonBackendPath], {
          cwd: path.dirname(pythonBackendPath),
          stdio: 'pipe'
        });

        pythonBackendProcess.stdout.on('data', (data) => {
          console.log(`Python Backend: ${data}`);
        });

        pythonBackendProcess.stderr.on('data', (data) => {
          console.error(`Python Backend Error: ${data}`);
        });
      }
    } catch (error) {
      console.error('Error starting backends:', error);
    }
  }
}

// Create menu
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Exit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'close' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About Warrior Support System',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About',
              message: 'Warrior Support System',
              detail: 'Version 1.0.0\nSecure Military Portal for Personnel Assessment and Support'
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// App event listeners
app.whenReady().then(() => {
  createWindow();
  createMenu();
  startBackends();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  // Kill backend processes
  if (backendProcess) {
    backendProcess.kill();
  }
  if (pythonBackendProcess) {
    pythonBackendProcess.kill();
  }

  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
  // Clean up backend processes
  if (backendProcess) {
    backendProcess.kill();
  }
  if (pythonBackendProcess) {
    pythonBackendProcess.kill();
  }
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (navigationEvent, url) => {
    navigationEvent.preventDefault();
    shell.openExternal(url);
  });
});

// IPC handlers
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('show-message-box', async (event, options) => {
  const result = await dialog.showMessageBox(mainWindow, options);
  return result;
});

// Export for testing
module.exports = { createWindow };
