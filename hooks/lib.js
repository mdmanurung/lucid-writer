// Shared helpers for the lucid-writer always-on hooks. Every path fails open:
// a bad flag or a missing rules file never blocks a session or a prompt.
const fs = require('fs');
const os = require('os');
const path = require('path');

const MODES = ['off', 'lite', 'full'];

function flagPath() {
  const dir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
  return path.join(dir, '.lucid-writer-mode');
}

// Absent or unreadable flag means off: always-on is opt-in.
function readMode() {
  try {
    const mode = fs.readFileSync(flagPath(), 'utf8').trim();
    return MODES.includes(mode) && mode !== 'off' ? mode : 'off';
  } catch (e) {
    return 'off';
  }
}

function setMode(mode) {
  if (mode === 'off') {
    try { fs.unlinkSync(flagPath()); } catch (e) {}
    return;
  }
  fs.mkdirSync(path.dirname(flagPath()), { recursive: true });
  fs.writeFileSync(flagPath(), mode);
}

function readRules(name) {
  try {
    return fs.readFileSync(path.join(__dirname, 'rules', `${name}.md`), 'utf8').trim();
  } catch (e) {
    return '';
  }
}

// lite is the prose rules; full adds the evidence ceiling.
function render(mode) {
  const parts = [readRules('lite')];
  if (mode === 'full') parts.push(readRules('full'));
  const body = parts.filter(Boolean).join('\n\n');
  if (!body) return '';
  const head = `LUCID-WRITER ACTIVE (${mode}). "stop lucid-writer" turns it off for this session; ` +
    `/lucid-writer off turns always-on off (flag: ${flagPath()}).`;
  return `${head}\n\n${body}`;
}

// SubagentStart drops raw stdout, so it needs the JSON form.
function writeOutput(event, text) {
  if (!text) return;
  try {
    if (event === 'SessionStart') {
      process.stdout.write(text);
      return;
    }
    process.stdout.write(JSON.stringify(
      { hookSpecificOutput: { hookEventName: event, additionalContext: text } }));
  } catch (e) {}
}

// Calls cb once with the parsed payload, or {} on bad input, error or timeout.
function readStdin(cb) {
  let input = '';
  let done = false;
  const finish = () => {
    if (done) return;
    done = true;
    let payload = {};
    try { payload = JSON.parse(input.replace(/^﻿/, '')) || {}; } catch (e) {}
    cb(payload);
  };
  process.stdin.on('data', chunk => { input += chunk; });
  process.stdin.on('end', finish);
  process.stdin.on('error', finish);
  setTimeout(finish, 1000).unref();
}

module.exports = { MODES, flagPath, readMode, setMode, render, writeOutput, readStdin };
