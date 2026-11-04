// UserPromptSubmit: handle /lucid-writer prose|full|off|status (lite and on are aliases)
// and /lucid-writer nudge on|off. Other prompts get at most one nudge line.
// Prompt text is never stored; only the mode and nudge flags are.
const fs = require('fs');
const path = require('path');
const { readMode, setMode, flagPath, normalise, stateDir, writeOutput, readStdin } = require('./lib');

const COMMAND = /^[/@$]lucid-writer(?::lucid-writer)?\s+(on|lite|prose|full|off|status)$/;
const NUDGE_COMMAND = /^[/@$]lucid-writer(?::lucid-writer)?\s+nudge\s+(on|off)$/;
const OWN_COMMAND = /^[/@$]lucid-writer/;
// Nudge heuristic, part 1: the prompt holds a correction word.
const CORRECTION = /\b(always|never|don['’]?t|do not|stop|prefer|instead of|from now on)\b/i;
// Part 2a: the previous assistant turn wrote or edited a prose file.
const PROSE_EXT = new Set(['.md', '.tex', '.qmd', '.docx', '.txt']);
const EDIT_TOOLS = new Set(['Edit', 'Write', 'MultiEdit', 'NotebookEdit']);
// Part 2b: in full mode, the prompt names a rewrite or quotes a passage of 15+ characters.
const REWRITE_REF = /\b(rewrite|rewrote|rewritten|rephras\w*|reword\w*|your (?:version|draft|edit|revision))\b|["“][^"”]{15,}["”]/i;
const TAIL_BYTES = 256 * 1024;
const NUDGE = 'If this is a lasting writing preference, offer /lucid-writer:learn once.';

function nudgePath() {
  return path.join(stateDir(), '.lucid-writer-nudge');
}

// Absent flag means on.
function nudgeOn() {
  try {
    return fs.readFileSync(nudgePath(), 'utf8').trim() !== 'off';
  } catch (e) {
    return true;
  }
}

function setNudge(arg) {
  if (arg === 'off') {
    fs.mkdirSync(path.dirname(nudgePath()), { recursive: true });
    fs.writeFileSync(nudgePath(), 'off');
    return;
  }
  try { fs.unlinkSync(nudgePath()); } catch (e) {}
}

function readTail(file) {
  const fd = fs.openSync(file, 'r');
  try {
    const size = fs.fstatSync(fd).size;
    const length = Math.min(size, TAIL_BYTES);
    const buf = Buffer.alloc(length);
    fs.readSync(fd, buf, 0, length, size - length);
    return buf.toString('utf8');
  } finally {
    fs.closeSync(fd);
  }
}

// A typed prompt, not a tool result and not injected skill text (isMeta).
function isRealPrompt(entry) {
  if (entry.type !== 'user' || entry.isMeta || entry.isSidechain) return false;
  const content = entry.message && entry.message.content;
  if (typeof content === 'string') return true;
  if (!Array.isArray(content)) return false;
  return !content.some(b => b && b.type === 'tool_result') && content.some(b => b && b.type === 'text');
}

function editsProse(entry) {
  const content = entry.type === 'assistant' && !entry.isSidechain && entry.message && entry.message.content;
  return Array.isArray(content) && content.some(b => {
    if (!b || b.type !== 'tool_use' || !EDIT_TOOLS.has(b.name)) return false;
    const file = b.input && (b.input.file_path || b.input.notebook_path);
    return typeof file === 'string' && PROSE_EXT.has(path.extname(file).toLowerCase());
  });
}

// True if the assistant turn before the current prompt wrote or edited a prose file.
// The current prompt may already be in the transcript, so prompts are only a
// boundary once an assistant line has been seen.
function previousTurnEditedProse(transcriptPath) {
  try {
    const lines = readTail(transcriptPath).split('\n');
    let seenAssistant = false;
    for (let i = lines.length - 1; i >= 0; i--) {
      let entry;
      try { entry = JSON.parse(lines[i]); } catch (e) { continue; } // cut first line, blanks
      if (!entry) continue;
      if (entry.type === 'assistant') {
        if (editsProse(entry)) return true;
        seenAssistant = true;
        continue;
      }
      if (seenAssistant && isRealPrompt(entry)) return false;
    }
    return false;
  } catch (e) {
    return false;
  }
}

function shouldNudge(payload, prompt, mode) {
  if (mode === 'off' || !nudgeOn() || OWN_COMMAND.test(prompt) || !CORRECTION.test(prompt)) return false;
  if (payload.transcript_path && previousTurnEditedProse(payload.transcript_path)) return true;
  return mode === 'full' && REWRITE_REF.test(prompt);
}

readStdin(payload => {
  try {
    const prompt = String(payload.prompt || '').trim();
    const nudge = prompt.toLowerCase().match(NUDGE_COMMAND);
    if (nudge) {
      setNudge(nudge[1]);
      writeOutput('UserPromptSubmit', `LUCID-WRITER NUDGE ${nudgeOn() ? 'ON' : 'OFF'}. Report this line to the user and do nothing else.`);
      process.exit(0);
    }
    const match = prompt.toLowerCase().match(COMMAND);
    if (match) {
      const arg = match[1] === 'status' ? 'status' : normalise(match[1]);
      if (arg !== 'status') setMode(arg);
      const alias = match[1] === 'lite' ? ' (lite is now called prose; use /lucid-writer prose)' : '';
      const mode = readMode();
      // Rules are injected at session start, so a change lands after /clear or a new session.
      const when = arg === 'status' ? '' : ' from the next session start or /clear';
      const msg = mode === 'off'
        ? `LUCID-WRITER ALWAYS-ON OFF${when}. Turn on: /lucid-writer prose or /lucid-writer full.`
        : `LUCID-WRITER ALWAYS-ON ${mode.toUpperCase()}${when}. Flag: ${flagPath()}. Turn off: /lucid-writer off.${alias}`;
      writeOutput('UserPromptSubmit', `${msg} Report this line to the user and do nothing else.`);
    } else if (shouldNudge(payload, prompt, readMode())) {
      writeOutput('UserPromptSubmit', NUDGE);
    }
  } catch (e) {}
  process.exit(0);
});
