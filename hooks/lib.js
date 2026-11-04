// Shared helpers for the lucid-writer always-on hooks. Every path fails open:
// a bad flag or a missing rules file never blocks a session or a prompt.
const crypto = require('crypto');
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

const RULES_BUDGET = 2000; // whole learned-rules block, header and notices included
const RULE_MAX = 300;
const UNTRUSTED = 'Project rules in .lucid-writer/rules.json are not trusted; run /lucid-writer:rules trust after reviewing them.';

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function readJson(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')) || {}; } catch (e) { return {}; }
}

function activeRules(store) {
  return (Array.isArray(store.rules) ? store.rules : [])
    .filter(r => r && r.status === 'active' && typeof r.text === 'string' && r.text.trim());
}

// Active rules for this cwd: the project file first (narrower), then the global
// file. The project file loads only when its sha256 is trusted in the global
// file; otherwise rules.notice carries one line saying so. Never throws.
function readLearnedRules(cwd = process.cwd()) {
  let rules = [];
  try {
    const global = readJson(path.join(stateDir(), 'lucid-writer', 'rules.json'));
    const file = path.join(cwd, '.lucid-writer', 'rules.json');
    let text = null;
    try { text = fs.readFileSync(file); } catch (e) {}
    let notice = '';
    if (text !== null) {
      let real = file;
      try { real = fs.realpathSync(file); } catch (e) {}
      const hash = sha256(text);
      const trusted = (Array.isArray(global.trusted) ? global.trusted : [])
        .some(t => t && t.path === real && t.sha256 === hash);
      if (trusted) {
        try { rules = rules.concat(activeRules(JSON.parse(text.toString('utf8')))); } catch (e) {}
      } else {
        notice = UNTRUSTED;
      }
    }
    rules = rules.concat(activeRules(global));
    rules.notice = notice;
  } catch (e) {
    rules = [];
    rules.notice = '';
  }
  return rules;
}

// One line, no leading '#', whitespace collapsed, so rule text cannot open a fake heading.
function escapeRule(text) {
  return String(text || '').replace(/\s+/g, ' ').trim().replace(/^#+\s*/, '').slice(0, RULE_MAX);
}

// '' when there is nothing to say. Overflow adds "N rules not shown".
function learnedBlock(rules) {
  const notice = rules.notice || '';
  if (!rules.length && !notice) return '';
  const lines = rules.map(r => `- ${escapeRule(r.text)}`).filter(l => l.length > 2);
  let out = '## Learned writing rules\n';
  const reserve = (notice ? notice.length + 1 : 0) + 60; // notice and the overflow line
  let shown = 0;
  for (const line of lines) {
    if (out.length + line.length + 1 + reserve > RULES_BUDGET) break;
    out += line + '\n';
    shown++;
  }
  if (shown < lines.length) out += `${lines.length - shown} rules not shown; run /lucid-writer:rules\n`;
  if (notice) out += notice + '\n';
  return out.trim();
}

// prose is the plain-prose rules; full adds the evidence ceiling and a voice.
// Learned rules follow in both modes.
function render(mode, cwd = process.cwd()) {
  const parts = [readRules('prose')];
  if (mode === 'full') parts.push(readRules('full'), voiceBlock(cwd));
  parts.push(learnedBlock(readLearnedRules(cwd)));
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

module.exports = { MODES, ALIASES, normalise, stateDir, flagPath, readMode, setMode, render, writeOutput, readStdin, readLearnedRules, learnedBlock, escapeRule, sha256 };
