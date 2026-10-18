#!/usr/bin/env node

/**
 * EasyDP Local PII Scanner - NPM Launcher
 * https://easydp.in
 */

const { spawn } = require('child_process');

const args = process.argv.slice(2);

// Check if python3 / python is available
const child = spawn('python3', ['-m', 'pii_scanner.cli', ...args], {
  stdio: 'inherit'
});

child.on('error', () => {
  // Try fallback to 'python'
  const fallback = spawn('python', ['-m', 'pii_scanner.cli', ...args], {
    stdio: 'inherit'
  });

  fallback.on('error', () => {
    console.error('\n[EasyDP Error] Python 3 is required to run easydp-scan.');
    console.error('Please install Python 3 or use our standalone binary: https://github.com/easydp-in/pii-scanner/releases\n');
    process.exit(1);
  });

  fallback.on('exit', (code) => {
    process.exit(code || 0);
  });
});

child.on('exit', (code) => {
  process.exit(code || 0);
});
