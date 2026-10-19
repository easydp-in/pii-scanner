#!/usr/bin/env node

/**
 * EasyDP Local PII Scanner - NPM Launcher
 * https://easydp.in
 */

const { spawn, execSync } = require('child_process');

const args = process.argv.slice(2);

function checkCliCommand() {
  try {
    const isWin = process.platform === 'win32';
    const checkCmd = isWin ? 'where easydp-scan' : 'which easydp-scan';
    const out = execSync(checkCmd, { stdio: 'pipe' }).toString().trim();
    if (out) return 'easydp-scan';
  } catch (e) {
    // Not found in PATH
  }
  return null;
}

const cliCmd = checkCliCommand();
if (cliCmd) {
  const child = spawn(cliCmd, args, { stdio: 'inherit' });
  child.on('exit', (code) => process.exit(code || 0));
  child.on('error', () => runPython());
} else {
  runPython();
}

function runPython() {
  const primaryCmd = process.platform === 'win32' ? 'python' : 'python3';
  const child = spawn(primaryCmd, ['-m', 'pii_scanner.cli', ...args], {
    stdio: 'inherit'
  });

  child.on('error', () => {
    const fallbackCmd = primaryCmd === 'python3' ? 'python' : 'python3';
    const fallback = spawn(fallbackCmd, ['-m', 'pii_scanner.cli', ...args], {
      stdio: 'inherit'
    });

    fallback.on('error', () => {
      console.error('\n[EasyDP Error] Python 3 is required to run easydp-scan via npm/npx.');
      console.error('Please install Python 3 or download our standalone pre-compiled binary:');
      console.error('  https://github.com/easydp-in/pii-scanner/releases\n');
      console.error('To run with Pass 2 Local AI NER:');
      console.error('  pip install "easydp-pii-scanner[ai]"');
      console.error('  npx easydp-pii-scanner scan . --local-ai\n');
      process.exit(1);
    });

    fallback.on('exit', (code) => {
      process.exit(code || 0);
    });
  });

  child.on('exit', (code) => {
    process.exit(code || 0);
  });
}
