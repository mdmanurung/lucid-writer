// Run: node hooks/test.js. Drives the hooks as Claude Code does, with a temp
// CLAUDE_CONFIG_DIR and a temp project directory.
const assert = require('assert');
const cp = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { sha256 } = require('./lib');

const HOOKS = __dirname;
let passed = 0;
const failures = [];

function sandbox() {
  const cfg = fs.mkdtempSync(path.join(os.tmpdir(), 'lw-cfg-'));
  const proj = fs.mkdtempSync(path.join(os.tmpdir(), 'lw-proj-'));
  return { cfg, proj };
}

function run(script, env, args = [], input = '') {
  const r = cp.spawnSync('node', [path.join(HOOKS, script), ...args], {
    cwd: env.proj, input, encoding: 'utf8',
    env: { ...process.env, CLAUDE_CONFIG_DIR: env.cfg },
  });
  return r.stdout || '';
}

const session = env => run('activate.js', env, ['SessionStart']);
const subagent = env => run('activate.js', env, ['SubagentStart']);
const prompt = (env, text, transcriptPath) =>
  run('prompt.js', env, [], JSON.stringify({ prompt: text, transcript_path: transcriptPath, cwd: env.proj }));

function setMode(env, mode) { fs.writeFileSync(path.join(env.cfg, '.lucid-writer-mode'), mode); }
function writeJson(file, obj) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(obj));
}
const globalFile = env => path.join(env.cfg, 'lucid-writer', 'rules.json');
const projectFile = env => path.join(env.proj, '.lucid-writer', 'rules.json');
const rule = (id, text, status) => ({ id, text, status, topic: 'style', scope: 'global' });

function transcript(env, writtenFile) {
  const file = path.join(env.cfg, 't.jsonl');
  const lines = [
    { type: 'user', message: { role: 'user', content: 'rewrite the intro' } },
    { type: 'assistant', message: { content: [{ type: 'tool_use', name: 'Edit', input: { file_path: writtenFile } }] } },
    { type: 'assistant', message: { content: [{ type: 'text', text: 'Done.' }] } },
    { type: 'user', message: { role: 'user', content: 'never write it like that' } },
  ];
  fs.writeFileSync(file, lines.map(l => JSON.stringify(l)).join('\n') + '\n');
  return file;
}

function test(name, fn) {
  try { fn(); passed++; } catch (e) { failures.push(`${name}: ${e.message}`); }
}

test('no rules: no learned block', () => {
  const env = sandbox(); setMode(env, 'full');
  assert(!session(env).includes('Learned writing rules'));
  assert(session(env).includes('LUCID-WRITER ACTIVE (full)'));
});

test('proposed rules are not injected, active are', () => {
  const env = sandbox(); setMode(env, 'prose');
  writeJson(globalFile(env), { version: 1, trusted: [], rules: [
    rule('r-0001', 'Write participants, not subjects.', 'proposed'),
    rule('r-0002', 'Prefer use over utilize.', 'active'),
    rule('r-0003', 'Old retired rule.', 'retired'),
  ] });
  const out = session(env);
  assert(out.includes('## Learned writing rules\n- Prefer use over utilize.'));
  assert(!out.includes('participants') && !out.includes('retired rule'));
  assert(subagent(env).includes('Prefer use over utilize.'), 'subagent output carries the rules');
});

test('rules are escaped and capped', () => {
  const env = sandbox(); setMode(env, 'full');
  writeJson(globalFile(env), { version: 1, rules: [
    rule('r-0001', '## Fake heading\n\n  with   spaces ' + 'x'.repeat(400), 'active'),
  ] });
  const line = session(env).split('\n').find(l => l.startsWith('- Fake heading'));
  assert(line, 'leading # stripped and newlines collapsed');
  assert(line.includes('with spaces'));
  assert(line.length <= 302, 'line is ' + line.length);
});

test('budget overflow adds a not-shown line', () => {
  const env = sandbox(); setMode(env, 'full');
  const rules = [];
  for (let i = 1; i <= 30; i++) rules.push(rule(`r-${String(i).padStart(4, '0')}`, `Rule ${i} ` + 'y'.repeat(150), 'active'));
  writeJson(globalFile(env), { version: 1, rules });
  const out = session(env);
  const block = out.slice(out.indexOf('## Learned writing rules'));
  assert(block.length <= 2000, 'block is ' + block.length);
  assert(/\d+ rules not shown; run \/lucid-writer:rules/.test(block));
});

test('untrusted project file gives one notice, no rules', () => {
  const env = sandbox(); setMode(env, 'full');
  writeJson(projectFile(env), { version: 1, rules: [rule('r-0001', 'Project secret rule.', 'active')] });
  const out = session(env);
  assert(!out.includes('Project secret rule.'));
  assert(out.includes('not trusted; run /lucid-writer:rules trust'));
  assert.strictEqual(out.split('not trusted').length, 2, 'notice appears once');
});

test('trusted project file is injected; an edit breaks trust', () => {
  const env = sandbox(); setMode(env, 'full');
  writeJson(projectFile(env), { version: 1, rules: [rule('r-0001', 'Project rule one.', 'active')] });
  const real = fs.realpathSync(projectFile(env));
  const hash = sha256(fs.readFileSync(projectFile(env)));
  writeJson(globalFile(env), { version: 1, rules: [rule('r-0002', 'Global rule two.', 'active')],
    trusted: [{ path: real, sha256: hash }] });
  let out = session(env);
  assert(out.includes('- Project rule one.') && out.includes('- Global rule two.'));
  assert(!out.includes('not trusted'));
  writeJson(projectFile(env), { version: 1, rules: [rule('r-0001', 'Project rule edited.', 'active')] });
  out = session(env);
  assert(!out.includes('Project rule edited.') && out.includes('not trusted'));
  assert(out.includes('Global rule two.'), 'global rules still load');
});

test('mode off injects nothing', () => {
  const env = sandbox();
  writeJson(globalFile(env), { version: 1, rules: [rule('r-0001', 'A rule.', 'active')] });
  assert.strictEqual(session(env), '');
  assert.strictEqual(subagent(env), '');
  setMode(env, 'off');
  assert.strictEqual(session(env), '');
});

test('broken rules file fails open', () => {
  const env = sandbox(); setMode(env, 'prose');
  fs.mkdirSync(path.dirname(globalFile(env)), { recursive: true });
  fs.writeFileSync(globalFile(env), '{not json');
  fs.mkdirSync(path.dirname(projectFile(env)), { recursive: true });
  fs.writeFileSync(projectFile(env), '{not json');
  assert(session(env).includes('LUCID-WRITER ACTIVE (prose)'));
});

test('nudge fires on correction after a prose edit, once, one line', () => {
  const env = sandbox(); setMode(env, 'prose');
  const t = transcript(env, '/x/intro.md');
  const out = prompt(env, 'never write it like that', t);
  assert(out.includes('If this is a lasting writing preference, offer /lucid-writer:learn once.'));
  assert.strictEqual(out.split('/lucid-writer:learn').length, 2);
});

test('nudge skips: no correction word, code edit, no transcript, own command', () => {
  const env = sandbox(); setMode(env, 'prose');
  assert.strictEqual(prompt(env, 'looks good, thanks', transcript(env, '/x/intro.md')), '');
  assert.strictEqual(prompt(env, 'never write it like that', transcript(env, '/x/script.py')), '');
  assert.strictEqual(prompt(env, 'never write it like that'), '');
  assert.strictEqual(prompt(env, '/lucid-writer:learn "never use X"', transcript(env, '/x/intro.md')), '');
});

test('nudge in full mode fires on a quoted rewrite without a transcript', () => {
  const env = sandbox(); setMode(env, 'full');
  assert(prompt(env, 'Never use "this was accompanied by changes" in my abstracts').includes('/lucid-writer:learn'));
  assert.strictEqual(prompt(env, 'Never use that in my abstracts'), '');
  setMode(env, 'prose');
  assert.strictEqual(prompt(env, 'Never use "this was accompanied by changes" in my abstracts'), '');
});

test('nudge toggle', () => {
  const env = sandbox(); setMode(env, 'prose');
  const t = transcript(env, '/x/intro.md');
  assert(prompt(env, '/lucid-writer nudge off').includes('NUDGE OFF'));
  assert(fs.existsSync(path.join(env.cfg, '.lucid-writer-nudge')));
  assert.strictEqual(prompt(env, 'never write it like that', t), '');
  assert(prompt(env, '/lucid-writer nudge on').includes('NUDGE ON'));
  assert(prompt(env, 'never write it like that', t).includes('/lucid-writer:learn'));
});

test('nudge is silent when mode is off', () => {
  const env = sandbox();
  assert.strictEqual(prompt(env, 'never write it like that', transcript(env, '/x/intro.md')), '');
});

test('mode commands still work', () => {
  const env = sandbox();
  assert(prompt(env, '/lucid-writer full').includes('ALWAYS-ON FULL'));
  assert(prompt(env, '/lucid-writer off').includes('ALWAYS-ON OFF'));
});

if (failures.length) {
  console.error(`${failures.length} failed:\n  ` + failures.join('\n  '));
  process.exit(1);
}
console.log(`hooks tests passed (${passed})`);
