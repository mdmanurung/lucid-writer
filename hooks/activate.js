// SessionStart and SubagentStart: inject the ruleset when always-on is set.
// The event name comes from argv because SubagentStart needs the JSON form.
const { readMode, render, writeOutput } = require('./lib');

try {
  const mode = readMode();
  if (mode !== 'off') writeOutput(process.argv[2] || 'SessionStart', render(mode));
} catch (e) {}
process.exit(0);
