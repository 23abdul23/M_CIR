const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
  
  // Add any other secure APIs you need here
  platform: process.platform,
  isElectron: true
});

// Prevent the renderer process from accessing Node.js APIs
window.addEventListener('DOMContentLoaded', () => {
  console.log('Warrior Support System - Electron Preload Loaded');
});
