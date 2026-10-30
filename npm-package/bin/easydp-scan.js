#!/usr/bin/env node

/**
 * EasyDP Local PII Scanner - NPM Launcher
 * https://easydp.in
 *
 * This wrapper finds a pip-installed `easydp-scan` binary on PATH
 * and delegates to it. If none is found, it falls back to invoking
 * Python directly (`python3 -m pii_scanner.cli`).
 *
 * Self-reference guard: when installed globally via npm, the npm bin
 * shim is also called `easydp-scan`. We detect and skip it to avoid
 * an infinite spawn loop.
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);

/**
 * Check if a resolved binary path is this script (or an npm-generated
 * shell wrapper that delegates to it).
 */
function isSelfReference(binPath) {
  try {
    const resolvedBin = fs.realpathSync(binPath);
    const resolvedSelf = fs.realpathSync(__filename);
    if (resolvedBin === resolvedSelf) return true;
  } catch (_) {
    /* ignore resolve errors */
  }

  // npm sometimes creates a shell/cmd wrapper that calls `node <our-script>`.
  // Read the first few hundred bytes and look for telltale markers.
  try {
    const head = fs.readFileSync(binPath, 'utf8').substring(0, 512);
    if (
      head.includes('easydp-scan.js') &&
      (head.includes('/usr/bin/env node') || head.includes('"$basedir/node"'))
    ) {
      return true;
    }
  } catch (_) {
    /* binary or unreadable file — not a JS shim */
  }

  return false;
}

/**
 * Search PATH for a pip-installed `easydp-scan` binary, skipping any
 * matches that resolve back to this npm wrapper script.
 */
function findPipBinary() {
  try {
    const isWin = process.platform === 'win32';
    // `where` on Windows lists all matches; `which` on Unix lists only the first.
    const checkCmd = isWin ? 'where easydp-scan' : 'which -a easydp-scan 2>/dev/null || which easydp-scan 2>/dev/null';
    const rawOut = execSync(checkCmd, { stdio: 'pipe' }).toString().trim();
    if (!rawOut) return null;

    const candidates = rawOut.split(/\r?\n/).map((s) => s.trim()).filter(Boolean);

    for (const candidate of candidates) {
      if (!isSelfReference(candidate)) {
        return candidate;
      }
    }
  } catch (_) {
    // `which`/`where` found nothing
  }
  return null;
}

// --- Main ---

const pipBin = findPipBinary();
if (pipBin) {
  const child = spawn(pipBin, args, { stdio: 'inherit' });
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
