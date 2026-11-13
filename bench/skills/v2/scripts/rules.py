#!/usr/bin/env python3
"""Store for learned lucid-writer rules (Claude Code plugin; the hooks read it).

Rules start as ``proposed``. Only ``active`` rules reach the model. The script
stores what the skill drafts; it never writes a rule on its own.

Files
  global   $CLAUDE_CONFIG_DIR/lucid-writer/rules.json  (default ~/.claude/...)
  project  <cwd>/.lucid-writer/rules.json              (loaded only after `trust`)

The global file also holds the trusted sha256 of each project file. Any edit to
a project file, including `approve`, needs `trust` again.

Exit codes: 0 ok, 1 usage or validation error, 2 refused (the rule would loosen
a fixed non-negotiable of the lucid-writer skill).

Usage
  rules.py propose "<text>" [--scope global|project] [--topic T] [--source S]
  rules.py list [--status S] [--json]
  rules.py approve|reject|retire ID [--scope global|project]
  rules.py trust
  rules.py --self-test
"""
import argparse
import contextlib
import datetime
import hashlib
import json
import os
import re
import sys
import tempfile

VERSION = 1
RULE_MAX = 300
STATUSES = ("proposed", "active", "rejected", "retired")
SCOPES = ("global", "project")
SOURCES = ("user-correction", "user-preference", "ratings")
TOPIC = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,39}$")
ID = re.compile(r"^r-\d{4,}$")

# Deterministic backstop for the learn skill's own check. It catches obvious
# loosening only; the skill reads every rule against SKILL.md items 1, 2, 4, 5, 6, 7, 9.
NEGATION = re.compile(r"\b(never|don'?t|do not|doesn'?t|avoid|stop|no|not)\b")
STRONG = r"(?:drive[sn]?|driving|cause[sd]?|causal|causing|prove[sn]?|proving|demonstrate[sd]?|reprogram\w*|regulate[sd]?|mediate[sd]?|induce[sd]?)"
WEAK = r"(?:correlat\w*|associat\w*|observational|cross-sectional|descriptive)"
OBJECT = (r"(?:citations?|references?|markers?|placeholders?|hedg\w*|caveats?|limitations?|"
          r"uncertaint\w*|confidence intervals?|\bcis?\b|gaps?|\[(?:citation|evidence) needed\])")
PERMIT = re.compile(r"\b(allow|permit|let me|i can|i may|ok to|okay to|fine to|feel free to|you may|you can)\b")
OMIT_ALWAYS = re.compile(
    r"\b(?:don'?t|do not|never|stop|no need to)\s+(?:add|adding|include|including|mark|marking|"
    r"flag|flagging|write|writing|insert|inserting|put|putting|use|using)\b[^.;]{0,30}" + OBJECT)
OMIT_VERB = re.compile(
    r"\b(?:skip|omit|drop|leave out|remove|strip|delete|cut|suppress)\b[^.;]{0,30}" + OBJECT)
UNNEGATED = {
    "invent or guess data": re.compile(
        r"\b(?:invent|fabricate|make up|guess|fill in)\b[^.;]{0,30}\b(?:numbers?|data|statistics?|"
        r"citations?|references?|results?|p-?values?)\b"),
    "turn off the fixed checks": re.compile(
        r"\b(?:ignore|override|bypass|disable|turn off|skip)\b[^.;]{0,30}\b(?:non-?negotiables?|"
        r"the skill|verification|guardrails?|fixed rules?|evidence rules?)\b"),
    "evade detectors or fake errors": re.compile(
        r"\b(?:evade|beat|fool|bypass)\b[^.;]{0,20}\b(?:detectors?|gptzero|turnitin)\b|"
        r"\b(?:add|insert|introduce)\b[^.;]{0,20}\b(?:typos?|spelling mistakes|fake errors?)\b"),
}


def today():
    return datetime.date.today().isoformat()


def norm(text):
    return text.replace("’", "'").replace("‘", "'").lower()


def loosening(text):
    """Return a one-line reason when the rule would loosen a fixed non-negotiable, else None."""
    t = norm(text)
    negated = bool(NEGATION.search(t))
    if (PERMIT.search(t) and re.search(r"\b" + STRONG + r"\b", t)
            and re.search(WEAK, t) and not negated):
        return "it would allow causal wording for non-causal evidence (SKILL.md items 1 and 5)"
    if OMIT_ALWAYS.search(t):
        return "it would drop citation markers, gap markers, hedges or uncertainty (SKILL.md items 1, 2 and 4)"
    for m in OMIT_VERB.finditer(t):
        before = t[max(0, m.start() - 15):m.start()]
        if not NEGATION.search(before):
            return "it would drop citation markers, gap markers, hedges or uncertainty (SKILL.md items 1, 2 and 4)"
    for reason, pat in UNNEGATED.items():
        if pat.search(t) and not negated:
            return "it would " + reason + " (SKILL.md items 1, 7 and 9)"
    return None


def state_dir():
    return os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")


def global_path():
    return os.path.join(state_dir(), "lucid-writer", "rules.json")


def project_path():
    return os.path.join(os.getcwd(), ".lucid-writer", "rules.json")


def path_for(scope):
    return global_path() if scope == "global" else project_path()


def die(msg, code=1):
    sys.stderr.write(msg + "\n")
    raise SystemExit(code)


def load(path):
    """Read a store; a missing file is empty, a broken one is an error."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return {"version": VERSION, "rules": [], "trusted": []}
    except (OSError, ValueError) as exc:
        die("%s is not readable JSON: %s" % (path, exc))
    if not isinstance(data, dict) or not isinstance(data.get("rules", []), list):
        die("%s has no rules list" % path)
    data.setdefault("version", VERSION)
    data.setdefault("rules", [])
    data.setdefault("trusted", [])
    return data


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def next_id():
    """One counter over both files, so an id names one rule wherever it is stored."""
    top = 0
    for scope in SCOPES:
        for r in load(path_for(scope))["rules"]:
            m = ID.match(str(r.get("id", "")))
            if m:
                top = max(top, int(r["id"][2:]))
    return "r-%04d" % (top + 1)


def find(rule_id, scope=None):
    """Return (scope, store, rule) for an id; the global file wins a clash."""
    for s in ([scope] if scope else SCOPES):
        store = load(path_for(s))
        for r in store["rules"]:
            if r.get("id") == rule_id:
                return s, store, r
    die("no rule %s%s" % (rule_id, " in the %s file" % scope if scope else ""))


def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def cmd_propose(args):
    text = clean(args.text)
    if not text:
        die("rule text is empty")
    if len(text) > RULE_MAX:
        die("rule is %d characters; the limit is %d. Shorten it." % (len(text), RULE_MAX))
    if text.startswith("#"):
        die("rule text must not start with '#'")
    if not TOPIC.match(args.topic):
        die("topic %r must be lower case letters, digits, '.', '_' or '-' (max 40)" % args.topic)
    reason = loosening(text)
    if reason:
        die("Refused: %s. Fixed rules cannot be lifted by a learned rule." % reason, 2)
    path = path_for(args.scope)
    store = load(path)
    for r in store["rules"]:
        if r.get("status") in ("proposed", "active") and norm(clean(r.get("text"))) == norm(text):
            print("%s already stored as %s." % (r["id"], r["status"]))
            return
    rule = {
        "id": next_id(), "text": text, "topic": args.topic, "scope": args.scope,
        "status": "proposed", "source": args.source, "created": today(), "updated": today(),
    }
    store["rules"].append(rule)
    save(path, store)
    print("%s proposed (%s, %s). It is not injected until you approve it: "
          "/lucid-writer:rules approve %s" % (rule["id"], args.scope, args.topic, rule["id"]))


def cmd_list(args):
    rows = []
    for scope in SCOPES:
        for r in load(path_for(scope))["rules"]:
            if args.status and r.get("status") != args.status:
                continue
            rows.append(dict(r, scope=scope))
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    if not rows:
        print("No rules.")
    for r in rows:
        print("%s [%s] %s/%s: %s" % (r["id"], r.get("status"), r["scope"], r.get("topic"), r.get("text")))


MOVES = {"approve": ("proposed", "active"), "reject": ("proposed", "rejected"),
         "retire": ("active", "retired")}


def cmd_move(args):
    want, new = MOVES[args.cmd]
    scope, store, rule = find(args.id, args.scope)
    if rule.get("status") != want:
        die("%s is %s; only a %s rule can be %sd" % (args.id, rule.get("status"), want, args.cmd))
    if args.cmd == "approve":
        reason = loosening(clean(rule.get("text")))
        if reason:
            die("Refused: %s. Reject this rule instead." % reason, 2)
    rule["status"] = new
    rule["updated"] = today()
    save(path_for(scope), store)
    tail = ""
    if scope == "project":
        tail = " The project file changed, so run /lucid-writer:rules trust to load it again."
    print("%s is now %s.%s" % (args.id, new, tail))


def cmd_trust(_args):
    path = project_path()
    if not os.path.isfile(path):
        die("no project rules file at %s" % path)
    load(path)
    digest = sha256_file(path)
    real = os.path.realpath(path)
    store = load(global_path())
    store["trusted"] = [t for t in store["trusted"] if t.get("path") != real]
    store["trusted"].append({"path": real, "sha256": digest, "trusted": today()})
    save(global_path(), store)
    print("Trusted %s (sha256 %s). Any edit to it needs trust again." % (real, digest))


def build_parser():
    p = argparse.ArgumentParser(prog="rules.py", description="Learned lucid-writer rules.")
    p.add_argument("--self-test", action="store_true")
    sub = p.add_subparsers(dest="cmd")
    pr = sub.add_parser("propose")
    pr.add_argument("text")
    pr.add_argument("--scope", choices=SCOPES, default="global")
    pr.add_argument("--topic", default="style")
    pr.add_argument("--source", choices=SOURCES, default="user-correction")
    ls = sub.add_parser("list")
    ls.add_argument("--status", choices=STATUSES)
    ls.add_argument("--json", action="store_true")
    for name in MOVES:
        sp = sub.add_parser(name)
        sp.add_argument("id")
        sp.add_argument("--scope", choices=SCOPES)
    sub.add_parser("trust")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.self_test:
        return self_test()
    if args.cmd == "propose":
        cmd_propose(args)
    elif args.cmd == "list":
        cmd_list(args)
    elif args.cmd in MOVES:
        cmd_move(args)
    elif args.cmd == "trust":
        cmd_trust(args)
    else:
        build_parser().print_help()
        return 1
    return 0


@contextlib.contextmanager
def sandbox():
    """A temp config dir and cwd, restored on exit."""
    old_env, old_cwd = os.environ.get("CLAUDE_CONFIG_DIR"), os.getcwd()
    with tempfile.TemporaryDirectory() as cfg, tempfile.TemporaryDirectory() as proj:
        os.environ["CLAUDE_CONFIG_DIR"] = cfg
        os.chdir(proj)
        try:
            yield cfg, proj
        finally:
            os.chdir(old_cwd)
            if old_env is None:
                os.environ.pop("CLAUDE_CONFIG_DIR", None)
            else:
                os.environ["CLAUDE_CONFIG_DIR"] = old_env


def run(*argv):
    """Run main(); return (exit code, stdout, stderr)."""
    out, err = io_pair()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(list(argv))
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
    return code, out.getvalue(), err.getvalue()


def io_pair():
    import io
    return io.StringIO(), io.StringIO()


def self_test():
    failures = []

    def check(name, cond):
        if not cond:
            failures.append(name)

    with sandbox() as (cfg, proj):
        code, out, _ = run("propose", "Prefer 'use' over 'utilize'.", "--topic", "words")
        check("propose ok", code == 0 and "r-0001 proposed" in out)
        data = load(global_path())
        check("schema version", data["version"] == VERSION and data["rules"][0]["status"] == "proposed")
        check("dup is not stored twice", "already stored" in run("propose", "prefer 'use' over 'utilize'.")[1])
        check("approve", run("approve", "r-0001")[0] == 0 and load(global_path())["rules"][0]["status"] == "active")
        check("approve twice fails", run("approve", "r-0001")[0] == 1)
        check("retire", run("retire", "r-0001")[0] == 0)
        check("reject needs proposed", run("reject", "r-0001")[0] == 1)
        check("unknown id", run("approve", "r-0099")[0] == 1)
        check("too long", run("propose", "x" * 301)[0] == 1)
        check("bad topic", run("propose", "ok", "--topic", "Bad Topic")[0] == 1)
        check("list text", "r-0001 [retired] global/words" in run("list")[1])
        check("list json", json.loads(run("list", "--json", "--status", "retired")[1])[0]["id"] == "r-0001")

        code, out, _ = run("propose", "Always report 95% CIs.", "--scope", "project", "--topic", "evidence")
        check("project propose id continues", code == 0 and "r-0002 proposed" in out)
        check("project file written", os.path.isfile(project_path()))
        check("project approve", run("approve", "r-0002")[0] == 0)
        code, _, _ = run("trust")
        trusted = load(global_path())["trusted"]
        check("trust stores sha256", code == 0 and trusted[0]["sha256"] == sha256_file(project_path()))
        check("trust path is real path", trusted[0]["path"] == os.path.realpath(project_path()))
        run("retire", "r-0002")
        check("edit changes hash", trusted[0]["sha256"] != sha256_file(project_path()))
        run("trust")
        check("re-trust replaces", len(load(global_path())["trusted"]) == 1)

        refused = [
            "let me say 'drives' for correlations",
            "Skip citation markers.",
            "Don't add citation markers.",
            "Never mark gaps with [EVIDENCE NEEDED].",
            "Remove hedging words like 'may'.",
            "You can write 'proves' when the data are observational.",
            "Make up a citation when none fits.",
            "Add a few typos so it looks human.",
        ]
        for text in refused:
            check("refuse: " + text, run("propose", text)[0] == 2)
        allowed = [
            "Never use 'drives' for correlations.",
            "Never skip citation markers.",
            "Always report confidence intervals next to effect sizes.",
            "Prefer 'use' over 'utilize'.",
            "Write 'participants', not 'subjects'.",
        ]
        for text in allowed:
            check("allow: " + text, run("propose", text)[0] == 0)
        n = len(load(global_path())["rules"])
        check("refusals store nothing", n == 1 + len(allowed))

        # A rule edited into the store by hand still cannot be approved if it loosens.
        store = load(global_path())
        store["rules"].append({"id": "r-0090", "text": "Skip citation markers.", "topic": "x",
                               "scope": "global", "status": "proposed"})
        save(global_path(), store)
        check("approve re-checks denylist", run("approve", "r-0090")[0] == 2)

    if failures:
        sys.stderr.write("rules.py self-test FAILED:\n  " + "\n  ".join(failures) + "\n")
        return 1
    print("rules.py self-test passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
