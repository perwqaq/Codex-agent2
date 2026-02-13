#!/usr/bin/env node
const fs = require('fs');
const os = require('os');
const path = require('path');

const root = path.resolve(__dirname, '..');

const targets = [
  ['skills', 'skills'],
  ['agents', 'agents'],
  ['workflow', 'workflow'],
  ['validation', 'validation'],
  ['config', 'config'],
];

const targetBase = process.env.CODEX_HOME || path.join(os.homedir(), '.codex');
const installRoot = path.join(targetBase, 'skills', 'codex-agent-workflow');

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function copyRecursive(src, dest) {
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    ensureDir(dest);
    for (const entry of fs.readdirSync(src)) {
      copyRecursive(path.join(src, entry), path.join(dest, entry));
    }
    return;
  }

  ensureDir(path.dirname(dest));
  fs.copyFileSync(src, dest);
}

for (const [sourceDir] of targets) {
  if (!fs.existsSync(path.join(root, sourceDir))) {
    console.error(`Install failed: missing ${sourceDir} directory in package.`);
    process.exit(1);
  }
}

for (const [sourceDir, targetDir] of targets) {
  copyRecursive(path.join(root, sourceDir), path.join(installRoot, targetDir));
}

console.log(`Installed to ${installRoot}`);
console.log('Restart Codex to pick up the installed workflow skills.');