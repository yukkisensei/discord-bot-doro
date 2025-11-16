import fs from 'fs';
import path from 'path';

const DATA_DIR = path.join(process.cwd(), 'data');
const BLOCK_FILE = path.join(DATA_DIR, 'blockedUsers.json');

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
if (!fs.existsSync(BLOCK_FILE)) fs.writeFileSync(BLOCK_FILE, JSON.stringify({ blocked: [] }, null, 2));

const readFile = () => JSON.parse(fs.readFileSync(BLOCK_FILE, 'utf8'));
const writeFile = (obj) => fs.writeFileSync(BLOCK_FILE, JSON.stringify(obj, null, 2), 'utf8');

// In-memory counters for rate window
const dmCounts = new Map(); // userId -> {count, firstTs}
const DM_WINDOW_MS = 60_000; // 1 minute window
const DM_LIMIT = 10; // limit within window

let blockedUsers = new Set((readFile().blocked) || []);

function persistBlocked() {
  writeFile({ blocked: Array.from(blockedUsers) });
}

function recordDm(userId) {
  if (blockedUsers.has(userId)) return { blocked: true };

  const now = Date.now();
  const s = dmCounts.get(userId) || { count: 0, firstTs: now };

  if (now - s.firstTs > DM_WINDOW_MS) {
    s.count = 1;
    s.firstTs = now;
  } else {
    s.count++;
  }

  dmCounts.set(userId, s);

  if (s.count > DM_LIMIT) {
    blockedUsers.add(userId);
    persistBlocked();
    return { blocked: true, newlyBlocked: true };
  }
  return { blocked: false };
}

function isBlocked(userId) {
  return blockedUsers.has(userId);
}

function unblock(userId) {
  if (blockedUsers.has(userId)) {
    blockedUsers.delete(userId);
    persistBlocked();
    return true;
  }
  return false;
}

function listBlocked() {
  return Array.from(blockedUsers);
}

export default {
  recordDm,
  isBlocked,
  unblock,
  listBlocked,
};
