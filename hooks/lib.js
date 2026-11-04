// Shared helpers for the lucid-writer always-on hooks. Every path fails open:
// a bad flag or a missing rules file never blocks a session or a prompt.
const fs = require('fs');
const os = require('os');
const path = require('path');

const MODES = ['off', 'prose', 'full'];
// lite was renamed prose in 1.3.0; the alias lasts one version.
const ALIASES = { lite: 'prose', on: 'full' };

function stateDir() {
  return process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
}

function flagPath() {
  return path.join(stateDir(), '.lucid-writer-mode');
}

function normalise(mode) {
  const m = ALIASES[mode] || mode;
  return MODES.includes(m) ? m : 'off';
}

// Absent or unreadable flag means off: always-on is opt-in.
function readMode() {
  try {
    return normalise(fs.readFileSync(flagPath(), 'utf8').trim());
  } catch (e) {
    return 'off';
  }
}

function setMode(arg) {
  const mode = normalise(arg);
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

const VOICE_MAX = 4000;

// A voice profile file as an injected block, or '' when it is missing, empty
// or not a file. It is style evidence; the full rules keep it from adding claims.
function readVoice(file, label) {
  try {
    if (!fs.statSync(file).isFile()) return '';
    const text = fs.readFileSync(file, 'utf8').trim();
    if (!text) return '';
    const cut = text.length > VOICE_MAX ? text.slice(0, VOICE_MAX) + '\n[voice profile truncated]' : text;
    return `### ${label} voice (${file})\n\n${cut}`;
  } catch (e) {
    return '';
  }
}

// Project voice, then the user's global voice, then the built-in default.
function voiceBlock(cwd) {
  return readVoice(path.join(cwd, '.lucid-writer', 'voice.md'), 'Project') ||
    readVoice(path.join(stateDir(), 'lucid-writer', 'voice.md'), 'Global') ||
    readRules('voice-default');
}

// prose is the plain-prose rules; full adds the evidence ceiling and a voice.
function render(mode, cwd = process.cwd()) {
  const parts = [readRules('prose')];
  if (mode === 'full') parts.push(readRules('full'), voiceBlock(cwd));
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

module.exports = { MODES, ALIASES, normalise, stateDir, flagPath, readMode, setMode, render, writeOutput, readStdin };
