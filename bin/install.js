#!/usr/bin/env node
const fs = require('fs');
const os = require('os');
const path = require('path');

const root = path.resolve(__dirname, '..');

const sourceSkillsDir = path.join(root, 'skills');
const metadataTargets = [
  ['agents', '_workflow/agents'],
  ['workflow', '_workflow/workflow'],
  ['validation', '_workflow/validation'],
  ['config', '_workflow/config'],
  ['README.md', '_workflow/README.md'],
];

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

function printHelp() {
  console.log(
    [
      'Usage: codex-agent-workflow-install [--ide codex|trae|cursor|all] [--dest <path>]',
      '',
      'Options:',
      '  --ide   Target IDE profile. Default: codex',
      '  --dest  Custom installation root directory (overrides --ide)',
      '',
      'Examples:',
      '  codex-agent-workflow-install',
      '  codex-agent-workflow-install --ide trae',
      '  codex-agent-workflow-install --ide all',
      '  codex-agent-workflow-install --dest D:\\tools\\skills\\codex-agent-workflow',
    ].join('\n')
  );
}

function parseArgs(args) {
  const parsed = { ide: 'codex', dest: null };
  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === '--ide') {
      parsed.ide = (args[i + 1] || '').toLowerCase();
      i += 1;
      continue;
    }
    if (arg === '--dest') {
      parsed.dest = args[i + 1] || null;
      i += 1;
      continue;
    }
    if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    }
    console.error(`Unknown argument: ${arg}`);
    printHelp();
    process.exit(1);
  }
  return parsed;
}

function installRootForIde(ide) {
  if (ide === 'codex') {
    const base = process.env.CODEX_HOME || path.join(os.homedir(), '.codex');
    return path.join(base, 'skills', 'codex-agent-workflow');
  }
  if (ide === 'trae') {
    const base = process.env.TRAE_HOME || path.join(os.homedir(), '.trae');
    return path.join(base, 'skills', 'codex-agent-workflow');
  }
  if (ide === 'cursor') {
    const base = process.env.CURSOR_HOME || path.join(os.homedir(), '.cursor');
    return path.join(base, 'skills', 'codex-agent-workflow');
  }
  throw new Error(`Unsupported IDE: ${ide}`);
}

function copySkillFolders(installRoot) {
  const entries = fs.readdirSync(sourceSkillsDir, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue;
    }
    const src = path.join(sourceSkillsDir, entry.name);
    const dest = path.join(installRoot, entry.name);
    copyRecursive(src, dest);
  }
}

function validateSources() {
  if (!fs.existsSync(sourceSkillsDir)) {
    throw new Error('Install failed: missing skills directory in package.');
  }
  for (const [sourcePath] of metadataTargets) {
    if (!fs.existsSync(path.join(root, sourcePath))) {
      throw new Error(`Install failed: missing ${sourcePath} in package.`);
    }
  }
}

function isSubPath(child, parent) {
  const rel = path.relative(parent, child);
  return rel && !rel.startsWith('..') && !path.isAbsolute(rel);
}

function validateTargetPath(installRoot) {
  const resolvedRoot = path.resolve(root);
  const resolvedTarget = path.resolve(installRoot);

  if (resolvedTarget === resolvedRoot || isSubPath(resolvedTarget, resolvedRoot)) {
    throw new Error(
      'Install failed: target path cannot be inside this repository (would cause recursive copy).'
    );
  }
}

function installTo(installRoot) {
  validateTargetPath(installRoot);
  copySkillFolders(installRoot);
  for (const [sourcePath, targetPath] of metadataTargets) {
    copyRecursive(path.join(root, sourcePath), path.join(installRoot, targetPath));
  }
  console.log(`Installed to ${installRoot}`);
}

function main() {
  try {
    validateSources();
    const args = parseArgs(process.argv.slice(2));

    let targets = [];
    if (args.dest) {
      targets = [path.resolve(args.dest)];
    } else if (args.ide === 'all') {
      targets = ['codex', 'trae', 'cursor'].map(installRootForIde);
    } else {
      targets = [installRootForIde(args.ide || 'codex')];
    }

    for (const target of targets) {
      installTo(target);
    }
    console.log('Restart your IDE to pick up the installed workflow skills.');
  } catch (error) {
    console.error(error.message || String(error));
    process.exit(1);
  }
}

main();
