// UserPromptSubmit: handle /lucid-writer on|lite|full|off|status.
// Prompt text is never stored; only the mode flag is.
const { readMode, setMode, flagPath, writeOutput, readStdin } = require('./lib');

const COMMAND = /^[/@$]lucid-writer(?::lucid-writer)?\s+(on|lite|full|off|status)$/;

readStdin(payload => {
  try {
    const match = String(payload.prompt || '').trim().toLowerCase().match(COMMAND);
    if (match) {
      const arg = match[1] === 'on' ? 'full' : match[1];
      if (arg !== 'status') setMode(arg);
      const mode = readMode();
      // Rules are injected at session start, so a change lands after /clear or a new session.
      const when = arg === 'status' ? '' : ' from the next session start or /clear';
      const msg = mode === 'off'
        ? `LUCID-WRITER ALWAYS-ON OFF${when}. Turn on: /lucid-writer lite or /lucid-writer full.`
        : `LUCID-WRITER ALWAYS-ON ${mode.toUpperCase()}${when}. Flag: ${flagPath()}. Turn off: /lucid-writer off.`;
      writeOutput('UserPromptSubmit', `${msg} Report this line to the user and do nothing else.`);
    }
  } catch (e) {}
  process.exit(0);
});
