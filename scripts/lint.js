import { readdirSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawnSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');
const IGNORE_DIRS = new Set(['node_modules', '.git', '.github', '.vscode', 'data']);

function collectJsFiles(dirPath) {
  const entries = readdirSync(dirPath, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    if (IGNORE_DIRS.has(entry.name)) continue;
    const fullPath = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      files.push(...collectJsFiles(fullPath));
    } else if (entry.isFile() && entry.name.endsWith('.js')) {
      files.push(fullPath);
    }
  }
  return files;
}

const jsFiles = collectJsFiles(projectRoot);
if (jsFiles.length === 0) {
  console.log('No JavaScript files found to lint.');
  process.exit(0);
}

for (const file of jsFiles) {
  const result = spawnSync(process.execPath, ['--check', file], { stdio: 'inherit' });
  if (result.status !== 0) {
    console.error(`Syntax check failed for ${file}`);
    process.exit(result.status ?? 1);
  }
}

console.log(`Syntax check passed for ${jsFiles.length} files.`);
